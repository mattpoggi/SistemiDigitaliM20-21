package com.MSL.multicameradepth.activities;

import android.Manifest;
import android.annotation.TargetApi;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.content.res.AssetFileDescriptor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.ImageFormat;
import android.graphics.SurfaceTexture;
import android.hardware.camera2.CameraAccessException;
import android.hardware.camera2.CameraCaptureSession;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraDevice;
import android.hardware.camera2.CameraManager;
import android.hardware.camera2.CameraMetadata;
import android.hardware.camera2.CaptureRequest;
import android.hardware.camera2.TotalCaptureResult;
import android.hardware.camera2.params.StreamConfigurationMap;
import android.media.Image;
import android.media.ImageReader;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.HandlerThread;
import android.support.annotation.NonNull;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.util.Size;
import android.util.SparseIntArray;
import android.view.Surface;
import android.view.TextureView;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.RelativeLayout;
import android.widget.Toast;


import com.MSL.multicameradepth.R;
import com.MSL.multicameradepth.listeners.PictureCapturingListener;
import com.MSL.multicameradepth.services.APictureCapturingService;
import com.MSL.multicameradepth.services.PictureCapturingServiceImpl;
import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import org.tensorflow.lite.Interpreter;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.TreeMap;



public class MainActivity extends AppCompatActivity implements PictureCapturingListener, ActivityCompat.OnRequestPermissionsResultCallback {

    String modelFile="optimized_pydnets.tflite";
    Interpreter tflite;

    private static final String[] requiredPermissions = {
                Manifest.permission.WRITE_EXTERNAL_STORAGE,
                Manifest.permission.CAMERA,
    };
    private static final int MY_PERMISSIONS_REQUEST_ACCESS_CODE = 1;
    private static final String TAG = "";

    private ImageView uploadBackPhoto;
    private ImageView uploadFrontPhoto;
     //The capture service          
    private APictureCapturingService pictureService;

    private TextureView textureView;
    private static final SparseIntArray ORIENTATIONS = new SparseIntArray();

    static {
        ORIENTATIONS.append(Surface.ROTATION_0, 90);
        ORIENTATIONS.append(Surface.ROTATION_90, 0);
        ORIENTATIONS.append(Surface.ROTATION_180, 270);
        ORIENTATIONS.append(Surface.ROTATION_270, 180);
    }

    private String cameraId;
    protected CameraDevice cameraDevice;
    protected CameraCaptureSession cameraCaptureSessions;
    protected CaptureRequest.Builder captureRequestBuilder;
    private Size imageDimension;
    private ImageReader imageReader;
    private static final int REQUEST_CAMERA_PERMISSION = 200;
    private Handler mBackgroundHandler;
    private HandlerThread mBackgroundThread;
    private String file;

    private byte[] immagine1;

    private File baseDir;
    private boolean calibrazioneAvvenuta;
    private int fotoCalibrazioneScattate;
    private boolean primoAvvio;


    TextureView.SurfaceTextureListener textureListener = new TextureView.SurfaceTextureListener() {
        @Override
        public void onSurfaceTextureAvailable(SurfaceTexture surface, int width, int height) {
            //open your camera here
            openCamera();
        }

        @Override
        public void onSurfaceTextureSizeChanged(SurfaceTexture surface, int width, int height) {
            // Transform you image captured size according to the surface width and height
        }

        @Override
        public boolean onSurfaceTextureDestroyed(SurfaceTexture surface) {
            return false;
        }

        @Override
        public void onSurfaceTextureUpdated(SurfaceTexture surface) {
        }
    };


    private final CameraDevice.StateCallback stateCallback = new CameraDevice.StateCallback() {
        @Override
        public void onOpened(CameraDevice camera) {
            //This is called when the camera is open
            Log.e(TAG, "onOpened");
            cameraDevice = camera;
            createCameraPreview();
        }

        @Override
        public void onDisconnected(CameraDevice camera) {
            cameraDevice.close();
        }

        @Override
        public void onError(CameraDevice camera, int error) {
            cameraDevice.close();
            cameraDevice = null;
        }
    };
    final CameraCaptureSession.CaptureCallback captureCallbackListener = new CameraCaptureSession.CaptureCallback() {
        @Override
        public void onCaptureCompleted(CameraCaptureSession session, CaptureRequest request, TotalCaptureResult result) {
            super.onCaptureCompleted(session, request, result);
            Toast.makeText(MainActivity.this, "Saved:" + file, Toast.LENGTH_SHORT).show();
            createCameraPreview();
        }
    };


    protected void startBackgroundThread() {
        mBackgroundThread = new HandlerThread("Camera Background");
        mBackgroundThread.start();
        mBackgroundHandler = new Handler(mBackgroundThread.getLooper());
    }

    protected void stopBackgroundThread() {
        mBackgroundThread.quitSafely();
        try {
            mBackgroundThread.join();
            mBackgroundThread = null;
            mBackgroundHandler = null;
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    protected void createCameraPreview() {
        try {
            SurfaceTexture texture = textureView.getSurfaceTexture();
            assert texture != null;
            texture.setDefaultBufferSize(imageDimension.getWidth(), imageDimension.getHeight());
            Surface surface = new Surface(texture);
            captureRequestBuilder = cameraDevice.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW);
            captureRequestBuilder.addTarget(surface);
            cameraDevice.createCaptureSession(Arrays.asList(surface), new CameraCaptureSession.StateCallback() {
                @Override
                public void onConfigured(@NonNull CameraCaptureSession cameraCaptureSession) {
                    //The camera is already closed
                    if (null == cameraDevice) {
                        return;
                    }
                    // When the session is ready, we start displaying the preview.
                    cameraCaptureSessions = cameraCaptureSession;
                    updatePreview();
                }

                @Override
                public void onConfigureFailed(@NonNull CameraCaptureSession cameraCaptureSession) {
                    Toast.makeText(MainActivity.this, "Configuration change", Toast.LENGTH_SHORT).show();
                }
            }, null);
        } catch (CameraAccessException e) {
            e.printStackTrace();
        }
    }

    private void openCamera() {
        CameraManager manager = (CameraManager) getSystemService(Context.CAMERA_SERVICE);
        Log.e(TAG, "is camera open");
        try {
            cameraId = manager.getCameraIdList()[0];
            CameraCharacteristics characteristics = manager.getCameraCharacteristics(cameraId);
            StreamConfigurationMap map = characteristics.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP);
            assert map != null;
            imageDimension = map.getOutputSizes(SurfaceTexture.class)[0];
            // Add permission for camera and let user grant the permission
            if (ActivityCompat.checkSelfPermission(this, Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED && ActivityCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(MainActivity.this, new String[]{Manifest.permission.CAMERA, Manifest.permission.WRITE_EXTERNAL_STORAGE}, REQUEST_CAMERA_PERMISSION);
                return;
            }
            manager.openCamera(cameraId, stateCallback, null);
        } catch (CameraAccessException e) {
            e.printStackTrace();
        }
        Log.e(TAG, "openCamera 0");
    }

    protected void updatePreview() {
        if (null == cameraDevice) {
            Log.e(TAG, "updatePreview error, return");
        }
        captureRequestBuilder.set(CaptureRequest.CONTROL_MODE, CameraMetadata.CONTROL_MODE_AUTO);
        try {
            cameraCaptureSessions.setRepeatingRequest(captureRequestBuilder.build(), null, mBackgroundHandler);
        } catch (CameraAccessException e) {
            e.printStackTrace();
        }
    }

    private void closeCamera() {
        Log.e("CLOSE", "Camera 0");
        if (null != cameraDevice) {
            cameraDevice.close();
            cameraDevice = null;
        }
        if (null != imageReader) {
            imageReader.close();
            imageReader = null;
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        Log.e(TAG, "onResume");
        startBackgroundThread();
        if (textureView.isAvailable()) {
            openCamera();
        } else {
            textureView.setSurfaceTextureListener(textureListener);
        }
    }

    @Override
    protected void onPause() {
        Log.e(TAG, "onPause");
        //closeCamera();
        stopBackgroundThread();
        super.onPause();
    }

    private void setMyPreviewSize(int width, int height) {
        // Get the set dimensions
        float newProportion = (float) width / (float) height;

        // Get the width of the screen
        int screenWidth = getWindowManager().getDefaultDisplay().getWidth();
        int screenHeight = getWindowManager().getDefaultDisplay().getHeight();
        float screenProportion = (float) screenWidth / (float) screenHeight;

        // Get the SurfaceView layout parameters
        android.view.ViewGroup.LayoutParams lp = textureView.getLayoutParams();
        if (newProportion > screenProportion) {
            lp.width = screenWidth;
            lp.height = (int) ((float) screenWidth / newProportion );
        } else {
            lp.width = (int) (newProportion * (float) screenHeight);
            lp.height = screenHeight;
        }
        // Commit the layout parameters
        textureView.setLayoutParams(lp);
    }

    boolean preview = true;



    @Override
    protected void onCreate(Bundle savedInstanceState) {
        primoAvvio=true;
        super.onCreate(savedInstanceState);
        setContentView(R.layout.layout2);
        checkPermissions();
        createDir();
        calibrazioneAvvenuta = checkCalibration(); //se falso devo scattare le 5 foto
        if(!calibrazioneAvvenuta){
            showToast("Non calibrato");
        }
        textureView = (TextureView) findViewById(R.id.textureView);
        assert textureView != null;
        setMyPreviewSize(480,680);
        textureView.setSurfaceTextureListener(textureListener);
        RelativeLayout bg = (RelativeLayout)findViewById(R.id.prev);
        uploadBackPhoto = (ImageView) findViewById(R.id.backIV);
        uploadFrontPhoto = (ImageView) findViewById(R.id.frontIV);
        Button btnDepth = (Button) findViewById(R.id.depthBtn);
        final Button btn = (Button) findViewById(R.id.startCaptureBtn);
        // getting instance of the Service from PictureCapturingServiceImpl
        pictureService = PictureCapturingServiceImpl.getInstance(this);

        btn.setOnClickListener(v -> {
            if(preview){

                //Hai premuto scatta foto: nasconde la preview, lo sfondo nero, imposta le due foto
                showToast("Starting capture!");

                uploadBackPhoto.setVisibility(View.VISIBLE);
                uploadFrontPhoto.setVisibility(View.VISIBLE);
                File fileLeft;
                File fileRight;
                if(!calibrazioneAvvenuta){
                    fileLeft = new File(baseDir.getPath()+"/scacchiera/left"+fotoCalibrazioneScattate+".jpg");
                    fileRight = new File(baseDir.getPath()+"/scacchiera/right"+fotoCalibrazioneScattate+".jpg");

                } else{
                    fileLeft = new File(baseDir.getPath()+"/left.jpg");
                    fileRight = new File(baseDir.getPath()+"/right.jpg");

                    bg.setVisibility(View.INVISIBLE);
                    btnDepth.setVisibility(View.VISIBLE);
                    btn.setText("Nuovo scatto");
                    preview=false;
                }

                primoAvvio=false;
                takePicture(fileRight);
                pictureService.startCapturing(this, fileLeft);
                if(!calibrazioneAvvenuta){
                    openCamera();
                }



            }else{
                //Hai premuto nuovo scatto: mostra la preview e lo sfondo nero
                btn.setText(R.string.take_pic_btn_label);
                uploadBackPhoto.setVisibility(View.INVISIBLE);
                uploadFrontPhoto.setVisibility(View.INVISIBLE);
                bg.setVisibility(View.VISIBLE);
                textureView.setVisibility(View.VISIBLE);
                //btnDepth.setVisibility(View.INVISIBLE);
                openCamera();
                preview=true;
            }
        });

        btnDepth.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // pulsante depth premuto
                bg.setVisibility(View.INVISIBLE);
                //btnDepth.setVisibility(View.INVISIBLE);
                textureView.setVisibility(View.INVISIBLE);
                uploadBackPhoto.setVisibility(View.VISIBLE);
                uploadFrontPhoto.setVisibility(View.VISIBLE);
                preview=false;

                //impostare la foto di profondità
                if (! Python.isStarted()) {
                    Python.start(new AndroidPlatform(MainActivity.this));
                }
                Python obj = Python.getInstance();
                PyObject file = obj.getModule("stereo_depth_nostro");

                Log.e("Salva in: ", baseDir.getPath());
                long time= System.currentTimeMillis();
                int i = file.callAttr("stereo_depth",baseDir+"/stereo_cam.yml", baseDir+"/left.jpg", baseDir+"/right.jpg", 0, baseDir+"").toInt();
                Log.e("TIME OPENCV",""+(System.currentTimeMillis()-time));
                if(i!=1){
                    Log.e("DEPTH", "Non riuscita");
                }
                uploadBackPhoto.invalidate();
                Bitmap myBitmap = BitmapFactory.decodeFile(baseDir+"/depth.jpg");
                uploadBackPhoto.setImageBitmap(myBitmap);


                try {
                    tflite = new Interpreter(loadModelFile(MainActivity.this, modelFile));
                }
                catch (IOException e) {
                    e.printStackTrace();
                }
                Bitmap contentImageLeft = ImageUtils.Companion.decodeBitmap(new File(Environment.getExternalStorageDirectory()+"/MulticameraDepth/left_rectified.jpg"));
                ByteBuffer contentArrayLeft =
                        ImageUtils.Companion.bitmapToByteBuffer(contentImageLeft, 640, 448, 0.0f, 255.0f);
                Bitmap contentImageRight = ImageUtils.Companion.decodeBitmap(new File(Environment.getExternalStorageDirectory()+"/MulticameraDepth/right_rectified.jpg"));
                ByteBuffer contentArrayRight =
                        ImageUtils.Companion.bitmapToByteBuffer(contentImageLeft, 640, 448, 0.0f, 255.0f);

                Object[] inputForPredict = new Object[]{contentArrayLeft, contentArrayRight};
                HashMap<Integer, Object> outputForPredict = new HashMap<>();
                float[][][][] styleBottleneck = ImageUtils.Companion.outputImage();
                float[][][][] output2 = ImageUtils.Companion.outputImage();
                float[][][][] output3 = ImageUtils.Companion.outputImage();
                outputForPredict.put(0, styleBottleneck);
                outputForPredict.put(1, output2);
                outputForPredict.put(2, output3);
                tflite.runForMultipleInputsOutputs(inputForPredict,outputForPredict);
                Bitmap img = ImageUtils.Companion.convertArrayToBitmap(styleBottleneck,640,448);
                uploadFrontPhoto.invalidate();
                uploadFrontPhoto.setImageBitmap(img);
            }
        });
    }

    private MappedByteBuffer loadModelFile(Activity activity, String MODEL_FILE) throws IOException {
        AssetFileDescriptor fileDescriptor = activity.getAssets().openFd(MODEL_FILE);
        FileInputStream inputStream = new FileInputStream(fileDescriptor.getFileDescriptor());
        FileChannel fileChannel = inputStream.getChannel();
        long startOffset = fileDescriptor.getStartOffset();
        long declaredLength = fileDescriptor.getDeclaredLength();
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength);
    }

    private void createDir(){
        baseDir = new File(Environment.getExternalStorageDirectory()+"/MulticameraDepth");
        File scacch = new File(baseDir.getPath()+"/scacchiera");
        if(!baseDir.exists()){
            baseDir.mkdir();
            scacch.mkdir();
        } else if(!scacch.exists()) {
            scacch.mkdir();
        }
    }

    private boolean checkCalibration(){
        File dir = new File(baseDir.getPath()+"/scacchiera");
        File stereoCam = new File(baseDir+"/stereo_cam.yml");
        if(stereoCam.exists()){
            return true;
        }
        if(dir.isDirectory()){
            if(dir.listFiles().length>=10 && !stereoCam.exists()){
                showToast("Rilevate foto scacchiera, calibrazione in corso");
                calibrazione();
                showToast("Calibrazione terminata");
                return true;
            } else {
                fotoCalibrazioneScattate=dir.listFiles().length/2;
                return false;
            }
        }
        return false;
    }

    private void calibrazione(){
        File scacchiera = new File(baseDir.getPath()+"/scacchiera");
        if (! Python.isStarted()) {
            Python.start(new AndroidPlatform(MainActivity.this));
        }
        showToast("Phyton avviato");
        Python obj = Python.getInstance();
        PyObject file = obj.getModule("single_camera_calibration");
        showToast("Avvio left");
        file.callAttr("single_camera_calibration",scacchiera.getPath(), "jpg", "left", 0.025, 9, 6, baseDir.getPath()+"/left_cam.yml");
        showToast("Avvio right");
        file.callAttr("single_camera_calibration",scacchiera.getPath(), "jpg", "right", 0.025, 9, 6, baseDir.getPath()+"/right_cam.yml");

        showToast("Avvio stereo");
        file = obj.getModule("stereo_camera_calibration");
        file.callAttr("stereo_camera_calibration", baseDir.getPath()+"/left_cam.yml", baseDir.getPath()+"/right_cam.yml", "left", "right", scacchiera.getPath(), scacchiera.getPath(), "jpg", 0.025, baseDir.getPath()+"/stereo_cam.yml" );
    }


    protected void takePicture(File fileDaScrivere) {
        if (null == cameraDevice) {
            Log.e(TAG, "cameraDevice is null");
            return;
        }
        CameraManager manager = (CameraManager) getSystemService(Context.CAMERA_SERVICE);
        try {
            CameraCharacteristics characteristics = manager.getCameraCharacteristics(cameraDevice.getId());
            Size[] jpegSizes = null;
            if (characteristics != null) {
                jpegSizes = characteristics.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP).getOutputSizes(ImageFormat.JPEG);
            }
            int width = 640;
            int height = 480;
            if (jpegSizes != null && 0 < jpegSizes.length) {
                width = jpegSizes[0].getWidth();
                height = jpegSizes[0].getHeight();
            }
            ImageReader reader = ImageReader.newInstance(width, height, ImageFormat.JPEG, 1);
            List<Surface> outputSurfaces = new ArrayList<Surface>(2);
            outputSurfaces.add(reader.getSurface());
            outputSurfaces.add(new Surface(textureView.getSurfaceTexture()));
            final CaptureRequest.Builder captureBuilder = cameraDevice.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE);
            captureBuilder.addTarget(reader.getSurface());
            captureBuilder.set(CaptureRequest.CONTROL_MODE, CameraMetadata.CONTROL_MODE_AUTO);
            // Orientation
            int rotation = getWindowManager().getDefaultDisplay().getRotation();
            captureBuilder.set(CaptureRequest.JPEG_ORIENTATION, ORIENTATIONS.get(rotation));
            final File file = new File(fileDaScrivere.getPath());
            ImageReader.OnImageAvailableListener readerListener = new ImageReader.OnImageAvailableListener() {
                @Override
                public void onImageAvailable(ImageReader reader) {
                    Log.e("SALVATAGGIO", "OK"+file.getPath());
                    Image image = null;
                    try {
                        image = reader.acquireLatestImage();
                        ByteBuffer buffer = image.getPlanes()[0].getBuffer();
                        byte[] bytes = new byte[buffer.capacity()];
                        buffer.get(bytes);
                        immagine1=bytes;
                        save(bytes);
                    } catch (FileNotFoundException e) {
                        e.printStackTrace();
                    } catch (IOException e) {
                        e.printStackTrace();
                    } finally {
                        if (image != null) {
                            image.close();
                        }
                    }
                }

                private void save(byte[] bytes) throws IOException {
                    OutputStream output = null;
                    try {
                        output = new FileOutputStream(file);
                        output.write(bytes);

                    } finally {
                        if (null != output) {
                            output.close();
                        }
                        closeCamera();
                    }
                }
            };
            reader.setOnImageAvailableListener(readerListener, mBackgroundHandler);
            final CameraCaptureSession.CaptureCallback captureListener = new CameraCaptureSession.CaptureCallback() {
                @Override
                public void onCaptureCompleted(CameraCaptureSession session, CaptureRequest request, TotalCaptureResult result) {
                    super.onCaptureCompleted(session, request, result);
                    Toast.makeText(MainActivity.this, "Saved:" + file, Toast.LENGTH_SHORT).show();
                }
            };
            cameraDevice.createCaptureSession(outputSurfaces, new CameraCaptureSession.StateCallback() {
                @Override
                public void onConfigured(CameraCaptureSession session) {
                    try {
                        session.capture(captureBuilder.build(), captureListener, mBackgroundHandler);
                    } catch (CameraAccessException e) {
                        e.printStackTrace();
                    }
                }

                @Override
                public void onConfigureFailed(CameraCaptureSession session) {
                }
            }, mBackgroundHandler);
        } catch (CameraAccessException e) {
            e.printStackTrace();
        }
    }

    private void showToast(final String text) {
        runOnUiThread(() ->
                Toast.makeText(getApplicationContext(), text, Toast.LENGTH_SHORT).show()
        );
    }


    @Override
    public void onDoneCapturingAllPhotos(TreeMap<String, byte[]> picturesTaken) {
        if(!calibrazioneAvvenuta){
            fotoCalibrazioneScattate++;
            calibrazioneAvvenuta = checkCalibration();
            if(calibrazioneAvvenuta){
                showToast("Calibrazione eseguita, puoi procedere");
            } else{
                showToast("Scatta "+ (5-fotoCalibrazioneScattate) + " foto per calibrare" );
            }
            return;
        }
        picturesTaken.put(baseDir + "/right.jpg", immagine1);
        if (picturesTaken != null && !picturesTaken.isEmpty()) {
            showToast("Done capturing all photos!");
            runOnUiThread(() ->{
                for (String s : picturesTaken.keySet()){
                    Bitmap bitmap = BitmapFactory.decodeByteArray(picturesTaken.get(s), 0, picturesTaken.get(s).length);
                    int nh = (int) (bitmap.getHeight() * (512.0 / bitmap.getWidth()));
                    Bitmap scaled = Bitmap.createScaledBitmap(bitmap, 512, nh, true);
                    if(s.contains("left.jpg")){
                        uploadBackPhoto.setImageBitmap(scaled);
                    } else if (s.contains("right.jpg")) {
                        uploadFrontPhoto.setImageBitmap(scaled);
                    }
                }
            });
            return;
        }
        showToast("No camera detected!");
    }


    @Override
    public void onCaptureDone(String pictureUrl, byte[] pictureData) {

    }

    @Override
    public void onRequestPermissionsResult(int requestCode,
                                           @NonNull String permissions[], @NonNull int[] grantResults) {
        switch (requestCode) {
            case MY_PERMISSIONS_REQUEST_ACCESS_CODE: {
                if (!(grantResults.length > 0
                        && grantResults[0] == PackageManager.PERMISSION_GRANTED)) {
                    checkPermissions();
                }
            }
        }
    }

    /**
     * controllo dei permessi.
     */
    @TargetApi(Build.VERSION_CODES.M)
    private void checkPermissions() {
        final List<String> neededPermissions = new ArrayList<>();
        for (final String permission : requiredPermissions) {
            if (ContextCompat.checkSelfPermission(getApplicationContext(),
                    permission) != PackageManager.PERMISSION_GRANTED) {
                neededPermissions.add(permission);
            }
        }
        if (!neededPermissions.isEmpty()) {
            requestPermissions(neededPermissions.toArray(new String[]{}),
                    MY_PERMISSIONS_REQUEST_ACCESS_CODE);
        }
    }
}

