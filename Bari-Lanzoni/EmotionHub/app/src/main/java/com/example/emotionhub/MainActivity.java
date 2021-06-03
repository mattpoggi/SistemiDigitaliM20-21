package com.example.emotionhub;


import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.app.AppCompatDelegate;
import androidx.core.content.FileProvider;
import android.annotation.SuppressLint;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Log;
import android.view.View;
import android.widget.Toast;

import java.io.File;
import java.io.IOException;

import static android.app.UiModeManager.MODE_NIGHT_NO;

public class MainActivity extends AppCompatActivity {
    static final int REQUEST_IMAGE_CAPTURE = 1;
    static final int RESULT_LOAD_IMAGE = 2;
    private Uri imageToUploadUri;


    @SuppressLint("WrongConstant")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        setTheme(R.style.Theme_EmotionHub);
        AppCompatDelegate.setDefaultNightMode(MODE_NIGHT_NO);
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_IMAGE_CAPTURE && resultCode == RESULT_OK) {
            if (imageToUploadUri != null) {
                Intent intent = new Intent(this, MainActivity2.class);
                intent.putExtra("uri", imageToUploadUri);
                intent.putExtra("mode",0);
                startActivity(intent);
            }else{
            Toast.makeText(this,"Error while capturing Image",Toast.LENGTH_LONG).show();
            }
        }else if (requestCode == RESULT_LOAD_IMAGE) {
            if (resultCode == RESULT_OK) {
                final Uri imageUri = data.getData();
                Intent intent = new Intent(this, MainActivity2.class);
                intent.putExtra("uri", imageUri);
                intent.putExtra("mode",1);
                startActivity(intent);
            }else {
                Toast.makeText(this,"Error while choosing Image",Toast.LENGTH_LONG).show();
            }
        }
    }

    public void onButtonLoad (View view) throws IOException {
        dispatchTakePictureIntent();
    }

    public void onButtonLoad2 (View view) throws IOException {
        getImageFromAlbum();
    }

    private void dispatchTakePictureIntent() throws IOException {
        Intent takePictureIntent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        File image = new File(getExternalFilesDir(Environment.DIRECTORY_PICTURES),"Image.jpg");
        Uri photoURI = FileProvider.getUriForFile(this,
                "com.example.android.fileprovider",
                image);
        takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI);
        imageToUploadUri = Uri.fromFile(image);
        startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE);
    }

    private void getImageFromAlbum(){
        try{
            Intent i = new Intent(Intent.ACTION_PICK);
            i.setType("image/*");
            startActivityForResult(i, RESULT_LOAD_IMAGE);
        }catch(Exception exp){
            Log.i("Error",exp.toString());
        }
    }

}