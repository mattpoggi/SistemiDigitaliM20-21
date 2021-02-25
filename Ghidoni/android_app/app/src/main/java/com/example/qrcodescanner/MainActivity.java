package com.example.qrcodescanner;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Canvas;
import android.graphics.Matrix;
import android.os.Bundle;
import android.util.Size;
import android.view.View;
import android.widget.Toast;

import com.example.qrcodescanner.tflite.Model;
import com.example.qrcodescanner.tflite.ModelFactory;
import com.example.qrcodescanner.tflite.TensorflowLiteModel;

import java.io.File;

public class MainActivity extends AppCompatActivity {
    private CodeScanner mCodeScanner;
    private ModelFactory modelFactory;
    private Model currentModel;
    private Integer sensorOrientation;
    private Matrix frameToCropTransform;
    private Size halfScreenSize = null;
    private Size screenSize = null;
    private Bitmap originalFrame = null;
    private Bitmap croppedFrame = null;
    private Bitmap outputDisp = null;
    private Bitmap outputDispResized = null;
    private Bitmap outputRGB = null;
    private boolean applyColormap = true;
    private static final boolean MAINTAIN_ASPECT = true;
    private static float COLOR_SCALE_FACTOR =  10.5f;
    private static int NUMBER_THREADS = Runtime.getRuntime().availableProcessors();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);


       /*
       // UNCOMMENT THIS TO ENABLE TEST

        modelFactory = new ModelFactory(this);
        currentModel = modelFactory.getModel(0);
        currentModel.prepare();
        TestNetwork t = new TestNetwork(currentModel);
        t.test();
        System.exit(0);*/

        CodeScannerView scannerView = findViewById(R.id.scanner_view);
        mCodeScanner = new CodeScanner(this, scannerView);
        mCodeScanner.setDecodeCallback(new DecodeCallback() {
            @Override
            public void onDecoded(@NonNull final String result) {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        scannerView.setDecodedString(result);
                    }
                });
            }
        });
        scannerView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                mCodeScanner.startPreview();
            }
        });


    }

    @Override
    protected void onResume() {
        super.onResume();
        mCodeScanner.startPreview();
    }

    @Override
    protected void onPause() {
        mCodeScanner.releaseResources();
        super.onPause();
    }
}