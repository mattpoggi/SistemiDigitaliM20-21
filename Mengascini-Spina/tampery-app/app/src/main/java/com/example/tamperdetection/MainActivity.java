package com.example.tamperdetection;

import android.app.Activity;
import android.content.Context;
import android.content.ContextWrapper;
import android.content.Intent;
import android.content.res.AssetFileDescriptor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;


import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import org.tensorflow.lite.DataType;
import org.tensorflow.lite.Interpreter;
import org.tensorflow.lite.support.common.FileUtil;
import org.tensorflow.lite.support.common.TensorOperator;
import org.tensorflow.lite.support.common.ops.NormalizeOp;
import org.tensorflow.lite.support.image.ImageProcessor;
import org.tensorflow.lite.support.image.TensorImage;
import org.tensorflow.lite.support.image.ops.ResizeOp;
import org.tensorflow.lite.support.image.ops.ResizeWithCropOrPadOp;
import org.tensorflow.lite.support.image.ops.TransformToGrayscaleOp;
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.util.List;


public class MainActivity extends AppCompatActivity {

    protected Interpreter tfliteRgb;
    protected Interpreter tfliteSrm;
    private TensorImage inputImageBufferRgb;
    private TensorImage inputImageBufferSrm;
    private  TensorBuffer outputProbabilityBufferRgb;
    private  TensorBuffer outputProbabilityBufferSrm;
    private static final float IMAGE_MEAN = 0.0f;
    private static final float IMAGE_STD = 255.0f;
    private Bitmap bitmap;
    private List<String> labels;
    ImageView imageView;
    Uri imageuri;
    Button buclassify;
    float resultRgb = -1;
    float resultSrm = -1;
    float resultNoiseprint = -1;
    TextView prediction;
    PyObject module;
    float rgbTime;
    float srmTime;
    float noiseprintTime;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        imageView=(ImageView)findViewById(R.id.image);
        buclassify=(Button)findViewById(R.id.classify);
        prediction=(TextView)findViewById(R.id.classifytext);

        imageView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent=new Intent();
                intent.setType("image/*");
                intent.setAction(Intent.ACTION_GET_CONTENT);
                startActivityForResult(Intent.createChooser(intent,"Select Picture"),12);
            }
        });

        if (! Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }
        Python py = Python.getInstance();
        module = py.getModule("noiseprintExtractor");

        try{
            tfliteRgb=new Interpreter(loadmodelfile(MainActivity.this, "RGB"));
            tfliteSrm=new Interpreter(loadmodelfile(MainActivity.this, "SRM"));
        }catch (Exception e) {
            e.printStackTrace();
        }

        buclassify.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                int imageTensorIndex = 0;
                DataType imageDataType = tfliteRgb.getInputTensor(imageTensorIndex).dataType();

                int probabilityTensorIndex = 0;
                int[] probabilityShape = tfliteRgb.getOutputTensor(probabilityTensorIndex).shape(); // {1, NUM_CLASSES}
                DataType probabilityDataType = tfliteRgb.getOutputTensor(probabilityTensorIndex).dataType();

                inputImageBufferRgb = new TensorImage(imageDataType);
                outputProbabilityBufferRgb = TensorBuffer.createFixedSize(probabilityShape, probabilityDataType);

                inputImageBufferSrm = new TensorImage(imageDataType);
                outputProbabilityBufferSrm = TensorBuffer.createFixedSize(probabilityShape, probabilityDataType);

                bitmap = Crop(bitmap);
                float start = System.nanoTime();
                inputImageBufferRgb = loadRgb(bitmap);
                tfliteRgb.run(inputImageBufferRgb.getBuffer(),outputProbabilityBufferRgb.getBuffer().rewind());
                float end = System.nanoTime();
                rgbTime = (end - start)/1000000000;
                resultRgb = outputProbabilityBufferRgb.getFloatValue(0);

                start = System.nanoTime();
                inputImageBufferSrm = loadSrm(bitmap);
                tfliteSrm.run(inputImageBufferSrm.getBuffer(),outputProbabilityBufferSrm.getBuffer().rewind());
                end = System.nanoTime();
                srmTime = (end - start)/1000000000;
                resultSrm = outputProbabilityBufferSrm.getFloatValue(0);

                resultNoiseprint = getNoiseprint(bitmap);

                showresult();
            }
        });
    }


    private Bitmap Crop(Bitmap src) {

        if(src.getWidth() < 384 || src.getHeight() < 256)
            return src;

        final int height = 256;
        final int width = 384;
        final Bitmap finalBitmap = Bitmap.createBitmap(bitmap, 0, 0, width, height);
        final Bitmap lastBitmap = Bitmap.createScaledBitmap(finalBitmap, 384, 256, true);

        return lastBitmap;
    }

    private TensorImage loadRgb(final Bitmap bitmap) {

        inputImageBufferRgb.load(bitmap);

        ImageProcessor imageProcessor =
                new ImageProcessor.Builder()
                        .add(new ResizeWithCropOrPadOp(256, 384))
                        .add(new ResizeOp(256, 384, ResizeOp.ResizeMethod.NEAREST_NEIGHBOR))
                        .add(getPreprocessNormalizeOp())
                        .build();
        return imageProcessor.process(inputImageBufferRgb);
    }

    private TensorImage loadSrm(Bitmap bitmap) {

        inputImageBufferSrm.load(SRMExtractor.extract(bitmap));

        ImageProcessor imageProcessor =
                new ImageProcessor.Builder()
                        .add(new ResizeWithCropOrPadOp(256, 384))
                        .add(new ResizeOp(256, 384, ResizeOp.ResizeMethod.NEAREST_NEIGHBOR))
                        .add(getPreprocessNormalizeOp())
                        .build();
        return imageProcessor.process(inputImageBufferSrm);
    }

    private float getNoiseprint(final Bitmap bitmap) {

        //Create image file that will be used by the python module to extract the noiseprint
        FileOutputStream fos = null;
        Bitmap input = Bitmap.createScaledBitmap(bitmap, 384, 256, false);
        try {
            fos = openFileOutput("src.png", MODE_PRIVATE);
            input.compress(Bitmap.CompressFormat.JPEG, 100, fos);
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            try {
                if(fos != null)
                    fos.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }

        //Call python module which extracts the noiseprint and returns the output of the prediction
        float start = System.nanoTime();
        Float noiseprintResult = module.callAttr("noiseprint_calc").toFloat();
        float end = System.nanoTime();
        noiseprintTime = (end - start)/1000000000;

        //Delete src file
        File src = new File(getFilesDir(), "src.png");
        src.delete();

        return noiseprintResult;
    }




    private TensorOperator getPreprocessNormalizeOp() {
        return new NormalizeOp(IMAGE_MEAN, IMAGE_STD);
    }

    private MappedByteBuffer loadmodelfile(Activity activity, String type) throws IOException {

        AssetFileDescriptor fileDescriptor;
        if(type.equals("RGB"))
            fileDescriptor=activity.getAssets().openFd("rgb.tflite");
        else
            fileDescriptor=activity.getAssets().openFd("srm.tflite");

        FileInputStream inputStream=new FileInputStream(fileDescriptor.getFileDescriptor());
        FileChannel fileChannel=inputStream.getChannel();
        long startoffset = fileDescriptor.getStartOffset();
        long declaredLength=fileDescriptor.getDeclaredLength();
        return fileChannel.map(FileChannel.MapMode.READ_ONLY,startoffset,declaredLength);
    }


    private void showresult(){
        try{
            labels = FileUtil.loadLabels(this,"labels.txt");
        }catch (Exception e){
            e.printStackTrace();
        }

        String stringResult = "\nRGB prediction: ";
        if(resultRgb < 0.5)
            stringResult =  stringResult + labels.get(0) + "\t(" + (Math.round(rgbTime*1000)/1000) + "s)" + "\n\n";
        else
            stringResult = stringResult + labels.get(1) + "\t(" + (Math.round(rgbTime*1000)/1000) + "s)" + "\n\n";

        stringResult = stringResult + "SRM prediction: ";
        if(resultSrm < 0.5)
            stringResult = stringResult + labels.get(0) + "\t(" + (Math.round(srmTime*1000)/1000) + "s)"  + "\n\n";
        else
            stringResult = stringResult + labels.get(1) + "\t(" + (Math.round(srmTime*1000)/1000) + "s)"  + "\n\n";

        stringResult = stringResult + "Noiseprint prediction: ";
        if(resultNoiseprint < 0.5)
            stringResult = stringResult + labels.get(0) + "\t(" + (Math.round(noiseprintTime*1000)/1000) + "s)"  + "\n\n";
        else
            stringResult = stringResult + labels.get(1) + "\t(" + (Math.round(noiseprintTime*1000)/1000) + "s)"  + "\n\n";
        alert("Result", stringResult);

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

