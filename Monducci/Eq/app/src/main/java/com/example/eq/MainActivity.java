package com.example.eq;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.provider.MediaStore;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import org.opencv.android.OpenCVLoader;
import org.opencv.core.Mat;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;

public class MainActivity extends Activity
{
    private static final int CAMERA_REQUEST = 1888;
    private ImageView imageView;
    private TextView textView;
    private TextView resultView;
    private static final int MY_CAMERA_PERMISSION_CODE = 100;
    private static final int MY_GALLERY_PERMISSION_CODE = 200;
    private static int RESULT_LOAD_IMAGE = 1;
    private static int RESULT_RESOLVE = 2;
    private static String[] notSupported = {"!", "(", ")", ",", "[", "]", "a", "alpha", "ascii_124", "b", "beta", "c", "cos", "d", "delta", "div", "e", "exists", "f", "forall", "forward_slash", "g", "gamma", "geq", "gt", "h", "i", "in", "infty", "int", "j", "k", "l", "lambda", "leq", "lim", "log", "lt", "m", "mu", "n", "neq", "o", "p", "phi", "pi", "pm", "prime", "q", "r", "rightarrow", "s", "sigma", "sin", "sqrt", "sum", "t", "tan", "theta", "u", "v", "w", "y", "z", "{", "}"};
    private static String check = "+-=";


    @Override
        public void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            if (!OpenCVLoader.initDebug()) {
                OpenCVLoader.initAsync(OpenCVLoader.OPENCV_VERSION_3_4_0, this, null);
            }
            setContentView(R.layout.activity_main);
            Button buttonLoadImage = (Button) findViewById(R.id.buttonLoadImage);
            Button photoButton = (Button) this.findViewById(R.id.buttonPhoto);
            Button resolveButton = (Button) this.findViewById(R.id.buttonResolve);
            this.imageView = (ImageView)this.findViewById(R.id.imageView1);
            this.textView = (TextView)this.findViewById(R.id.textView1);
            this.resultView = (TextView)this.findViewById(R.id.textView2);
            photoButton.setOnClickListener(new View.OnClickListener()
            {
                @Override
                public void onClick(View v)
                {
                    if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED)
                    {
                        requestPermissions(new String[]{Manifest.permission.CAMERA}, MY_CAMERA_PERMISSION_CODE);
                    }
                    else
                    {
                        Intent cameraIntent = new Intent(android.provider.MediaStore.ACTION_IMAGE_CAPTURE);
                        startActivityForResult(cameraIntent, CAMERA_REQUEST);
                    }
                }
            });
            buttonLoadImage.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    if (checkSelfPermission(Manifest.permission.READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED)
                    {
                        requestPermissions(new String[]{Manifest.permission.READ_EXTERNAL_STORAGE}, MY_GALLERY_PERMISSION_CODE);
                    }
                    else
                    {
                        Intent galleryIntent = new Intent(Intent.ACTION_PICK,
                                android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
                        startActivityForResult(galleryIntent, RESULT_LOAD_IMAGE);
                    }
                }
            });
            resolveButton.setOnClickListener(new View.OnClickListener(){
                public void onClick(View v)
                {
                    String equation = textView.getText().toString();
                    if(MainActivity.notCorrect(equation)){
                        resultView.setText("Wrong syntax!");
                    }
                    else if(MainActivity.notSupported(equation)){
                        resultView.setText("Can't resolve this expression yet!");
                    }
                    else{
                        String result = SolveEquation.solveEquation(equation);
                        resultView.setText("Your result is: "+result);
                    }
                }
            });
        }




    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults)
    {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == MY_CAMERA_PERMISSION_CODE)
        {
            if (grantResults[0] == PackageManager.PERMISSION_GRANTED)
            {
                Toast.makeText(this, "camera permission granted", Toast.LENGTH_LONG).show();
                Intent cameraIntent = new Intent(android.provider.MediaStore.ACTION_IMAGE_CAPTURE);
                startActivityForResult(cameraIntent, CAMERA_REQUEST);
            }
            else
            {
                Toast.makeText(this, "camera permission denied", Toast.LENGTH_LONG).show();
            }
        }
        else if (requestCode == MY_GALLERY_PERMISSION_CODE)
        {
            if (grantResults[0] == PackageManager.PERMISSION_GRANTED)
            {
                Toast.makeText(this, "gallery permission granted", Toast.LENGTH_LONG).show();
                Intent galleryIntent = new Intent(Intent.ACTION_PICK,
                        android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
                startActivityForResult(galleryIntent, RESULT_LOAD_IMAGE);
            }
            else
            {
                Toast.makeText(this, "gallery permission denied", Toast.LENGTH_LONG).show();
            }
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == RESULT_LOAD_IMAGE && resultCode == RESULT_OK && null != data) {
            Uri selectedImage = data.getData();
            String[] filePathColumn = { MediaStore.Images.Media.DATA };
            Cursor cursor = getContentResolver().query(selectedImage,
                    filePathColumn, null, null, null);
            cursor.moveToFirst();
            int columnIndex = cursor.getColumnIndex(filePathColumn[0]);
            String picturePath = cursor.getString(columnIndex);
            cursor.close();
            Bitmap photo=BitmapFactory.decodeFile(picturePath);
            Segmentation seg = new Segmentation(photo);
            long start = System.currentTimeMillis();
            List<Mat> images = seg.segment();
            imageView.setImageBitmap(photo);
            try {
                Model m = new Model(images, MainActivity.this);
                textView.setText(""+m.process());
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        else if (requestCode == CAMERA_REQUEST && resultCode == Activity.RESULT_OK)
        {
            Bitmap photo = (Bitmap) data.getExtras().get("data");
            Segmentation seg = new Segmentation(photo);
            List<Mat> images = seg.segment();
            imageView.setImageBitmap(photo);

            try {
                Model m = new Model(images, MainActivity.this);
                textView.setText(""+m.process());
            } catch (IOException e) {
                e.printStackTrace();
            }

        }
    }

    private static Boolean notCorrect(String eq){

        boolean res = false;
        int count = 0;

        for (int i=0; i<eq.length();i++){
            if(check.indexOf(eq.charAt(i))!=-1){
                if((i+1)<eq.length() && check.indexOf(eq.charAt(i+1))!=-1){
                    res = true;
                    break;
                }
                else if((i+1)==eq.length()){
                    res = true;
                    break;
                }
            }
            else if(eq.charAt(i)=='x'){
                if((i+1)<eq.length() && eq.charAt(i+1)=='x'){
                    res = true;
                    break;
                }
            }
            if (eq.charAt(i)=='='){
                count++;
            }
        }

        if(count!=1){
            res=true;
        }

        return res;
    }

    private static boolean notSupported(String equation) {
        boolean contains = Arrays.stream(notSupported).anyMatch(equation::contains);
        if (contains){
            return true;
        }
        else{
            return false;
        }
    }


}