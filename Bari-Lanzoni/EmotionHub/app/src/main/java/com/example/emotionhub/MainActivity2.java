package com.example.emotionhub;

import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.app.AppCompatDelegate;

import android.annotation.SuppressLint;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.Matrix;
import android.media.ExifInterface;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import com.example.emotionhub.ml.Arousal3;
import com.example.emotionhub.ml.Emotions;
import com.example.emotionhub.ml.Valence2;
import org.tensorflow.lite.DataType;
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.text.DecimalFormat;
import java.util.HashMap;

import static android.app.UiModeManager.MODE_NIGHT_NO;

public class MainActivity2 extends AppCompatActivity {
    static final int REQUEST_IMAGE_CAPTURE = 1;
    private ImageView imageView;
    private TextView emozione1;
    private TextView emozione2;
    private TextView emozione3;
    private TextView emozione4;
    private TextView emozione5;
    private ProgressBar emozione1Bar;
    private ProgressBar emozione2Bar;
    private ProgressBar emozione3Bar;

    @RequiresApi(api = Build.VERSION_CODES.O)
    @SuppressLint("WrongConstant")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        AppCompatDelegate.setDefaultNightMode(MODE_NIGHT_NO);
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main2);
        imageView = findViewById(R.id.imageView);
        emozione1 = findViewById(R.id.textEmotion1);
        emozione2 = findViewById(R.id.textEmotion2);
        emozione3 = findViewById(R.id.textEmotion3);
        emozione4 = findViewById(R.id.textEmotion4);
        emozione5 = findViewById(R.id.textEmotion5);
        emozione1Bar = findViewById(R.id.Emotion1Bar);
        emozione2Bar = findViewById(R.id.Emotion2Bar);
        emozione3Bar = findViewById(R.id.Emotion3Bar);

        Wheel wheel = new Wheel();
        HashMap<String,Float> mappa = null;

        Uri imageUri = (Uri) getIntent().getExtras().get("uri");
        int mode = (int) getIntent().getExtras().get("mode");
        Bitmap reducedSizeBitmap = null;
        InputStream imageStream = null;
        ExifInterface exif = null;
        Matrix matrix = null;
        Bitmap b = null;
        int orientation = 0;
        if(mode==0) {
            reducedSizeBitmap = getBitmap(imageUri.getPath());
        }else if(mode ==1){
            try {
                imageStream = getContentResolver().openInputStream(imageUri);
                b = BitmapFactory.decodeStream(imageStream);
                imageStream = getContentResolver().openInputStream(imageUri);
            } catch (FileNotFoundException e) {
                e.printStackTrace();
            }
            try {
                exif = new ExifInterface(imageStream);
            } catch (IOException e) {
                e.printStackTrace();
            }
            orientation = exif.getAttributeInt(ExifInterface.TAG_ORIENTATION, 1);
            if(orientation == ExifInterface.ORIENTATION_ROTATE_90){
                matrix = new Matrix();
                matrix.postRotate(90);
                b = Bitmap.createBitmap(b, 0, 0, b.getWidth(), b.getHeight(), matrix, true);
            }else if (orientation == ExifInterface.ORIENTATION_ROTATE_180){
                matrix = new Matrix();
                matrix.postRotate(180);
                b = Bitmap.createBitmap(b, 0, 0, b.getWidth(), b.getHeight(), matrix, true);
            }else if (orientation == ExifInterface.ORIENTATION_ROTATE_270) {
                matrix = new Matrix();
                matrix.postRotate(270);
                b = Bitmap.createBitmap(b, 0, 0, b.getWidth(), b.getHeight(), matrix, true);
            }
            reducedSizeBitmap=b;
        }

        int width = reducedSizeBitmap.getWidth();
        int height = reducedSizeBitmap.getHeight();
        int crop=0;
        Bitmap cropImg = null;
        if(width>height){
            crop = (width - height) / 2;
            cropImg = Bitmap.createBitmap(reducedSizeBitmap, crop, 0, height, height);
        }
        else if(width<height){
            crop = (height - width) / 2;
            cropImg = Bitmap.createBitmap(reducedSizeBitmap, 0, crop, width, width);

        }else{
            cropImg = reducedSizeBitmap;
        }

        if(reducedSizeBitmap != null){
            imageView.setImageBitmap(cropImg);
        }else{
            Toast.makeText(this,"Error while capturing Image",Toast.LENGTH_LONG).show();
        }
        try {
            Valence2 model1 = Valence2.newInstance(this);

            Bitmap image = Bitmap.createScaledBitmap(cropImg,123,123,true);

            TensorBuffer inputFeature0 = TensorBuffer.createFixedSize(new int[]{1, 123, 123, 3}, DataType.FLOAT32);
            inputFeature0.loadBuffer(getByteBuffer(image));

            Valence2.Outputs outputs = model1.process(inputFeature0);
            TensorBuffer outputFeature0 = outputs.getOutputFeature0AsTensorBuffer();


            Arousal3 model2 = Arousal3.newInstance(this);

            TensorBuffer inputFeature1 = TensorBuffer.createFixedSize(new int[]{1, 123, 123, 3}, DataType.FLOAT32);
            inputFeature1.loadBuffer(getByteBuffer(image));

            Arousal3.Outputs outputs1 = model2.process(inputFeature0);
            TensorBuffer outputFeature1 = outputs1.getOutputFeature0AsTensorBuffer();

            mappa=wheel.getNear(outputFeature0.getFloatValue(0),outputFeature1.getFloatValue(0));

            DecimalFormat df = new DecimalFormat();
            df.setMaximumFractionDigits(2);

            Emotions model3 = Emotions.newInstance(this);

            TensorBuffer inputFeature2 = TensorBuffer.createFixedSize(new int[]{1, 123, 123, 3}, DataType.FLOAT32);
            inputFeature2.loadBuffer(getByteBuffer(image));

            Emotions.Outputs outputs2 = model3.process(inputFeature0);
            TensorBuffer outputFeature2 = outputs2.getOutputFeature0AsTensorBuffer();

            emozione5.setText("Main emotion: " + getEmotion(outputFeature2));

            emozione1.setText(wheel.getEmotions()[0]+": "+df.format(mappa.get(wheel.getEmotions()[0]))+"%");
            emozione2.setText(wheel.getEmotions()[1]+": "+df.format(mappa.get(wheel.getEmotions()[1]))+"%");
            emozione3.setText(wheel.getEmotions()[2]+": "+df.format(mappa.get(wheel.getEmotions()[2]))+"%");

            emozione4.setText("Valence:\t"+df.format(outputFeature0.getFloatValue(0))+"\t\t\tArousal:\t"+df.format(outputFeature1.getFloatValue(0)) );

            emozione1Bar.setProgress(Math.round(mappa.get(wheel.getEmotions()[0])));
            emozione2Bar.setProgress(Math.round(mappa.get(wheel.getEmotions()[1])));
            emozione3Bar.setProgress(Math.round(mappa.get(wheel.getEmotions()[2])));

            model1.close();
            model2.close();
            model3.close();
        } catch (IOException e) {
            // TODO Handle the exception
        }

    }

    private ByteBuffer getByteBuffer(Bitmap bitmap){
        int width = bitmap.getWidth();
        int height = bitmap.getHeight();
        ByteBuffer mImgData = ByteBuffer
                .allocateDirect(4 * width * height * 3);
        mImgData.order(ByteOrder.nativeOrder());
        int[] pixels = new int[width*height];
        bitmap.getPixels(pixels, 0, width, 0, 0, width, height);
        for (int pixel : pixels) {
            mImgData.putFloat((float) Color.red(pixel)/255.0f);
            mImgData.putFloat((float) Color.green(pixel)/255.0f);
            mImgData.putFloat((float) Color.blue(pixel)/255.0f);
        }
        return mImgData;
    }

   private Bitmap getBitmap(String path) {

        ExifInterface exif = null;
        Matrix matrix = null;
        int orientation = 0;
        Uri uri = Uri.fromFile(new File(path));
        InputStream in = null;
        try {
            final int IMAGE_MAX_SIZE = 1200000; // 1.2MP
            in = getContentResolver().openInputStream(uri);

            // Decode image size
            BitmapFactory.Options o = new BitmapFactory.Options();
            o.inJustDecodeBounds = true;
            BitmapFactory.decodeStream(in, null, o);
            in.close();


            int scale = 1;
            while ((o.outWidth * o.outHeight) * (1 / Math.pow(scale, 2)) >
                    IMAGE_MAX_SIZE) {
                scale++;
            }
            Log.d("", "scale = " + scale + ", orig-width: " + o.outWidth + ", orig-height: " + o.outHeight);

            Bitmap b = null;
            in = getContentResolver().openInputStream(uri);
            if (scale > 1) {
                scale--;
                // scale to max possible inSampleSize that still yields an image
                // larger than target
                o = new BitmapFactory.Options();
                o.inSampleSize = scale;
                b = BitmapFactory.decodeStream(in, null, o);

                // resize to desired dimensions
                int height = b.getHeight();
                int width = b.getWidth();
                Log.d("", "1th scale operation dimenions - width: " + width + ", height: " + height);

                double y = Math.sqrt(IMAGE_MAX_SIZE
                        / (((double) width) / height));
                double x = (y / height) * width;

                Bitmap scaledBitmap = Bitmap.createScaledBitmap(b, (int) x,
                        (int) y, true);
                b.recycle();
                b = scaledBitmap;

                System.gc();
            } else {
                b = BitmapFactory.decodeStream(in);
            }
            in.close();

            Log.d("", "bitmap size - width: " + b.getWidth() + ", height: " +
                    b.getHeight());
            exif = new ExifInterface(path);
            orientation = exif.getAttributeInt(ExifInterface.TAG_ORIENTATION, 1);
            if(orientation == ExifInterface.ORIENTATION_ROTATE_90){
                matrix = new Matrix();
                matrix.postRotate(90);
                b = Bitmap.createBitmap(b, 0, 0, b.getWidth(), b.getHeight(), matrix, true);
            }else if (orientation == ExifInterface.ORIENTATION_ROTATE_180){
                matrix = new Matrix();
                matrix.postRotate(180);
                b = Bitmap.createBitmap(b, 0, 0, b.getWidth(), b.getHeight(), matrix, true);
            }else if (orientation == ExifInterface.ORIENTATION_ROTATE_270) {
                matrix = new Matrix();
                matrix.postRotate(270);
                b = Bitmap.createBitmap(b, 0, 0, b.getWidth(), b.getHeight(), matrix, true);
            }
            return b;
        } catch (IOException e) {
            Log.e("", e.getMessage(), e);
            return null;
        }
    }

    public String getEmotion(TensorBuffer outputFeature2){
        String[] emotions={"Neutral","Happiness","No-Face","Surprise","Fear","Disgust","Anger","Contempt","None","Uncertain","Sadness"};
        String res = "";
        float max = 0;

        for (int i=0;i<11;i++){
            if(outputFeature2.getFloatValue(i)>max){
                res=emotions[i];
                max=outputFeature2.getFloatValue(i);
            }
        }

        if (max < 0.3f){
            return "Uncertain";
        }
        return res;

    }


}