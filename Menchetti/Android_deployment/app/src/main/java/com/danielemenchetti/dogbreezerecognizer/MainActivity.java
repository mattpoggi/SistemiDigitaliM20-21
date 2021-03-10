package com.danielemenchetti.dogbreezerecognizer;


import androidx.annotation.Nullable;
import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import android.app.Activity;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.res.AssetFileDescriptor;
import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.RectF;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.MediaStore;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.PopupWindow;
import android.widget.TextView;
import android.widget.Toast;

import org.tensorflow.lite.DataType;
import org.tensorflow.lite.Interpreter;
import org.tensorflow.lite.support.common.FileUtil;
import org.tensorflow.lite.support.common.TensorOperator;
import org.tensorflow.lite.support.common.TensorProcessor;
import org.tensorflow.lite.support.common.ops.NormalizeOp;
import org.tensorflow.lite.support.image.ImageProcessor;
import org.tensorflow.lite.support.image.TensorImage;
import org.tensorflow.lite.support.image.ops.ResizeOp;
import org.tensorflow.lite.support.image.ops.ResizeWithCropOrPadOp;
import org.tensorflow.lite.support.image.ops.Rot90Op;
import org.tensorflow.lite.support.label.TensorLabel;
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.ConnectException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import com.danielemenchetti.dogbreezerecognizer.Cane;


public class MainActivity extends AppCompatActivity {

    protected Interpreter tflite;
    private MappedByteBuffer tfliteModel;
    private TensorImage inputImageBuffer;
    private  int imageSizeX;
    private  int imageSizeY;
    private  TensorBuffer outputProbabilityBuffer;
    private  TensorProcessor probabilityProcessor;
    private static final float IMAGE_MEAN = 0.0f;
    private static final float IMAGE_STD = 1.0f;
    private static final float PROBABILITY_MEAN = 0.0f;
    private static final float PROBABILITY_STD = 255.0f;
    private Bitmap bitmap;
    private List<String> labels;
    ImageView imageView;
    Uri imageuri;
    Button buclassify;
    TextView classitext;
    Cane cane;
    private static Context context;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        imageView=(ImageView)findViewById(R.id.image);
        buclassify=(Button)findViewById(R.id.classify);
        classitext=(TextView)findViewById(R.id.classifytext);
        MainActivity.context = getApplicationContext();

        try {
            Bitmap bm = getBitmapFromAsset("placeholder.jpg");
            imageView.setImageBitmap(bm);
        } catch (IOException e) {
            e.printStackTrace();
        }

        imageView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent=new Intent();
                intent.setType("image/*");
                intent.setAction(Intent.ACTION_GET_CONTENT);
                startActivityForResult(Intent.createChooser(intent,"Scegli un'immagine"),12);
                //classitext.setText(MainActivity.context.getResources().getString(R.string.text_1));
            }
        });

        try{
            tflite=new Interpreter(loadmodelfile(this));
        }catch (Exception e) {
            e.printStackTrace();
        }

        buclassify.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                try{
                    int check= bitmap.getWidth(); //per controllare se la bitmap è stata scelta vedo se ha la width settata!!
                    int imageTensorIndex = 0;
                    int[] imageShape = tflite.getInputTensor(imageTensorIndex).shape(); // {1, height, width, channels}
                    imageSizeY = imageShape[1];
                    imageSizeX = imageShape[2];
                    DataType imageDataType = tflite.getInputTensor(imageTensorIndex).dataType();

                    int probabilityTensorIndex = 0;
                    int[] probabilityShape = tflite.getOutputTensor(probabilityTensorIndex).shape(); // {1, NUM_CLASSES}
                    DataType probabilityDataType = tflite.getOutputTensor(probabilityTensorIndex).dataType();

                    inputImageBuffer = new TensorImage(imageDataType);
                    outputProbabilityBuffer = TensorBuffer.createFixedSize(probabilityShape, probabilityDataType);
                    probabilityProcessor = new TensorProcessor.Builder().add(getPostprocessNormalizeOp()).build();


                    //Questa parte serve a gestire le immagini in RGB (in caso di reti con shape: [x, y, z, 3])
                    inputImageBuffer = loadImage(bitmap);
                    float startTime = System.nanoTime();
                    tflite.run(inputImageBuffer.getBuffer(),outputProbabilityBuffer.getBuffer().rewind());
                    float endTime = System.nanoTime();
                    System.out.println("TIME: "+(endTime-startTime));
                    showresult();
                }catch (Exception e) {
                    // the bitmap, not valid eighter null or empty
                    alert("Errore", "Scegli un'immagine prima di proseguire!");
                }
            }
        });

    }

    private Bitmap getBitmapFromAsset(String strName) throws IOException
    {
        AssetManager assetManager = getAssets();
        InputStream istr = assetManager.open(strName);
        Bitmap bitmap = BitmapFactory.decodeStream(istr);
        return bitmap;
    }

    public static Context getAppContext() {
        return MainActivity.context;
    }


    //Questa funzione, prima converte Bitmap in Grayscale, poi trasforma il tutto in un ByteBuffer
    /*
    private ByteBuffer getByteBuffer(Bitmap bitmap){
        int width = bitmap.getWidth();
        int height = bitmap.getHeight();
        ByteBuffer mImgData = ByteBuffer
                .allocateDirect(4 * width * height);
        mImgData.order(ByteOrder.nativeOrder());
        int[] pixels = new int[width*height];
        bitmap.getPixels(pixels, 0, width, 0, 0, width, height);
        for (int pixel : pixels) {
            mImgData.putFloat((float) Color.red(pixel));
        }
        return mImgData;
    }
    */




    public static Bitmap scalePreserveRatio(Bitmap imageToScale, int destinationWidth,
                                            int destinationHeight) {
        if (destinationHeight > 0 && destinationWidth > 0 && imageToScale != null) {
            int width = imageToScale.getWidth();
            int height = imageToScale.getHeight();

            //Calculate the max changing amount and decide which dimension to use
            float widthRatio = (float) destinationWidth / (float) width;
            float heightRatio = (float) destinationHeight / (float) height;

            //Use the ratio that will fit the image into the desired sizes
            int finalWidth = (int)Math.floor(width * widthRatio);
            int finalHeight = (int)Math.floor(height * widthRatio);
            if (finalWidth > destinationWidth || finalHeight > destinationHeight) {
                finalWidth = (int)Math.floor(width * heightRatio);
                finalHeight = (int)Math.floor(height * heightRatio);
            }

            //Scale given bitmap to fit into the desired area
            imageToScale = Bitmap.createScaledBitmap(imageToScale, finalWidth, finalHeight, true);

            //Created a bitmap with desired sizes
            Bitmap scaledImage = Bitmap.createBitmap(destinationWidth, destinationHeight, Bitmap.Config.ARGB_8888);
            Canvas canvas = new Canvas(scaledImage);

            //Draw background color
            Paint paint = new Paint();
            paint.setColor(Color.BLACK);
            paint.setStyle(Paint.Style.FILL);
            canvas.drawRect(0, 0, canvas.getWidth(), canvas.getHeight(), paint);

            //Calculate the ratios and decide which part will have empty areas (width or height)
            float ratioBitmap = (float)finalWidth / (float)finalHeight;
            float destinationRatio = (float) destinationWidth / (float) destinationHeight;
            float left = ratioBitmap >= destinationRatio ? 0 : (float)(destinationWidth - finalWidth) / 2;
            float top = ratioBitmap < destinationRatio ? 0: (float)(destinationHeight - finalHeight) / 2;
            canvas.drawBitmap(imageToScale, left, top, null);

            return scaledImage;
        } else {
            return imageToScale;
        }
    }

    private TensorImage loadImage(final Bitmap bitmap) {
        Bitmap bmp = scalePreserveRatio(bitmap, 128, 128);
        inputImageBuffer.load(bmp);
        ImageProcessor imageProcessor =
                new ImageProcessor.Builder()
                        .add(new NormalizeOp(0,255))
                        .build();
        return imageProcessor.process(inputImageBuffer);


        /*
        // Loads bitmap into a TensorImage.
        inputImageBuffer.load(bitmap);

        // Creates processor for the TensorImage.
        int cropSize = Math.min(bitmap.getWidth(), bitmap.getHeight());
        ImageProcessor imageProcessor =
                new ImageProcessor.Builder()
                        //.add(new ResizeWithCropOrPadOp(cropSize, cropSize))
                        .add(new ResizeOp(imageSizeX, imageSizeY, ResizeOp.ResizeMethod.NEAREST_NEIGHBOR))
                        .add(new NormalizeOp(0,1))
                        .build();
        return imageProcessor.process(inputImageBuffer);

         */
    }


    private MappedByteBuffer loadmodelfile(Activity activity) throws IOException {
        AssetFileDescriptor fileDescriptor=activity.getAssets().openFd("DBR1.9.8-8000.tflite");
        FileInputStream inputStream=new FileInputStream(fileDescriptor.getFileDescriptor());
        FileChannel fileChannel=inputStream.getChannel();
        long startoffset = fileDescriptor.getStartOffset();
        long declaredLength=fileDescriptor.getDeclaredLength();
        return fileChannel.map(FileChannel.MapMode.READ_ONLY,startoffset,declaredLength);
    }

    private TensorOperator getPreprocessNormalizeOp() {
        return new NormalizeOp(IMAGE_MEAN, IMAGE_STD);
    }
    private TensorOperator getPostprocessNormalizeOp(){
        return new NormalizeOp(PROBABILITY_MEAN, PROBABILITY_STD);
    }

    private void showresult(){
        try{
            labels = FileUtil.loadLabels(this,"IT_breeds.txt");
        }catch (Exception e){
            e.printStackTrace();
        }

        //Map<String, Float> labeledProbability = new TensorLabel(labels, probabilityProcessor.process(outputProbabilityBuffer).getMapWithFloatValue();
        Map<String, Float> labeledProbability = new TensorLabel(labels, outputProbabilityBuffer).getMapWithFloatValue();
        float massimo1, massimo2;
        String razza1 = "", razza2 = "";

        massimo1 = (Collections.max(labeledProbability.values()));

        for (Map.Entry<String, Float> entry : labeledProbability.entrySet()) {
            if (entry.getValue()==massimo1) {
                razza1 = entry.getKey();
            }
        }

        labeledProbability.remove(razza1);

        massimo2 = (Collections.max(labeledProbability.values()));
        for (Map.Entry<String, Float> entry : labeledProbability.entrySet()) {
            if (entry.getValue()==massimo2) {
                razza2 = entry.getKey();
            }
        }

        cane = new Cane(Cane.TipoCane.INVALIDO, razza1, massimo1, razza2, massimo2);

        double limit = 1;
        if (cane.getPercent1() < 0.7) {
            cane.setTipo(Cane.TipoCane.INVALIDO);
        } else {
            if (cane.getPercent1() >= 0.7 && cane.getPercent1() < 0.8) {
                limit = 0.15;
            } else {
                if (cane.getPercent1() >= 0.8 && cane.getPercent1() < 0.85) {
                    limit = 0.1;
                } else {
                    if (cane.getPercent1() >= 0.85 && cane.getPercent1() < 0.9) {
                        limit = 0.07;
                    } else {
                        if (cane.getPercent1() >= 0.9 && cane.getPercent1() < 0.95) {
                            limit = 0.04;
                        }
                    }
                }
            }
            if (cane.getPercent2() >= limit) {
                cane.setTipo(Cane.TipoCane.MISTO);
            } else {
                cane.setTipo(Cane.TipoCane.PURO);
            }
        }


        String result = cane.print_human_readable_dog();
        //classitext.setText(result);
        alert("Risultato", result);
        /*
        Map<String, Float> labeledProbability = new TensorLabel(labels, probabilityProcessor.process(outputProbabilityBuffer)).getMapWithFloatValue();
        float maxValueInMap =(Collections.max(labeledProbability.values()));

        for (Map.Entry<String, Float> entry : labeledProbability.entrySet()) {
            if (entry.getValue()==maxValueInMap) {
                classitext.setText(entry.getKey());
            }
        }
         */
    }

    public void alert(String title, String msg){
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle(title);
        builder.setMessage(msg);
        builder.setPositiveButton("Ok", null);
        AlertDialog dialog = builder.show();
        TextView messageView = (TextView)dialog.findViewById(android.R.id.message);
        messageView.setGravity(Gravity.CENTER);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if(requestCode==12 && resultCode==RESULT_OK && data!=null) {
            imageuri = data.getData();
            try {
                bitmap = MediaStore.Images.Media.getBitmap(getContentResolver(), imageuri);
                imageView.setImageBitmap(bitmap);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
}
