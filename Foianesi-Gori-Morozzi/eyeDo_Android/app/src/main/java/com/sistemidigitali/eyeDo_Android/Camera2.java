package com.sistemidigitali.eyeDo_Android;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Matrix;
import android.graphics.RectF;
import android.graphics.SurfaceTexture;
import android.hardware.camera2.CameraAccessException;
import android.hardware.camera2.CameraCaptureSession;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraDevice;
import android.hardware.camera2.CameraManager;
import android.hardware.camera2.CameraMetadata;
import android.hardware.camera2.CaptureRequest;
import android.hardware.camera2.params.StreamConfigurationMap;
import android.os.Handler;
import android.os.HandlerThread;
import android.support.annotation.NonNull;
import android.support.design.widget.CoordinatorLayout;
import android.util.Log;
import android.util.Size;
import android.view.Surface;
import android.view.TextureView;
import android.widget.Toast;

import java.util.Arrays;


public class Camera2 extends MyCamera {

    private final String TAG = "Camera2";
    private final Activity mActivity;
    private final TextureView mTextureView;
    private final CameraEvent mCameraEvent;
    private CameraDevice cameraDevice;
    private String cameraId;
    private Size imageDimension;
    private Handler mBackgroundHandler;
    private HandlerThread mBackgroundThread;

    private CameraCaptureSession cameraCaptureSessions;
    //protected CaptureRequest captureRequest;
    private CaptureRequest.Builder captureRequestBuilder;
    private final CameraDevice.StateCallback stateCallback = new CameraDevice.StateCallback() {
        @Override
        public void onOpened(CameraDevice camera) {
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
    private Bitmap frame;
    private CameraManager manager;
    private final TextureView.SurfaceTextureListener textureListener = new TextureView.SurfaceTextureListener() {

        @Override
        public void onSurfaceTextureAvailable(SurfaceTexture surface, int width, int height) {
            //the camera opens here
            open();
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
            if (!mCameraEvent.isInElaboration()) {
                mCameraEvent.startElab();
                frame = Bitmap.createBitmap(mTextureView.getWidth(), mTextureView.getHeight(), Bitmap.Config.ARGB_8888);
                mTextureView.getBitmap(frame);
                mActivity.runOnUiThread(() -> {
                    //For a fluid camera preview we create a Thread
                    Runnable myRunnable = () -> mCameraEvent.internalElaboration(frame, "JPEG");
                    new Thread(myRunnable).start();
                });
            }
        }
    };

    public Camera2(Activity activity, CameraEvent cameraEvent, TextureView textureView) {
        mActivity = activity;
        mCameraEvent = cameraEvent;
        mTextureView = textureView;
        //mTextureView.setRotation(270);

        assert textureView != null;
        textureView.setSurfaceTextureListener(textureListener);
    }

    @Override
    public void open() {
        startBackgroundThread();
        if (mTextureView.isAvailable()) {
            openCam();
        } else {
            mTextureView.setSurfaceTextureListener(textureListener);
        }
    }

    @SuppressLint("MissingPermission")
    private void openCam() {
        manager = (CameraManager) mActivity.getSystemService(Context.CAMERA_SERVICE);
        try {
            cameraId = manager.getCameraIdList()[0];
            boolean preferredRatio = false;
            //Find the right resolution, possibly in 4:3
            CameraCharacteristics characteristics = manager.getCameraCharacteristics(cameraId);
            StreamConfigurationMap map = characteristics.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP);
            assert map != null;
            Size[] sizes = map.getOutputSizes(SurfaceTexture.class);
            CoordinatorLayout.LayoutParams cl;
            for (Size size : sizes) {
                imageDimension = size;
                if (((float) imageDimension.getWidth() / (float) imageDimension.getHeight()) == (4f / 3f) &&
                        (imageDimension.getHeight() * imageDimension.getWidth()) >= (Constants.inputWidth * Constants.inputHeight)) {
                    preferredRatio = true;
                    break;
                }
            }
            float w;
            float h = mTextureView.getMeasuredHeight();
            //Set the found resolution with respect to the ratio that has been found: if there is no 4:3 option, then select the higher resolution in any other ratio
            if (!preferredRatio) {
                imageDimension = map.getOutputSizes(SurfaceTexture.class)[0];
                float ratio = (float) imageDimension.getWidth() / (float) imageDimension.getHeight();
                w = (int) (float) (h * ratio);
            } else {
                w = (int) (float) ((h * ((float) 4 / (float) 3)));
            }
            cl = new CoordinatorLayout.LayoutParams((int) w, (int) (h));
            transformImage((int) w, (int) h);
            mTextureView.setLayoutParams(cl);
            // Ask permissions for the camera
            if (!Utils.need_requestCAMERAandWRITEPermissions(mActivity)) {
                manager.openCamera(cameraId, stateCallback, null);
            }
        } catch (CameraAccessException e) {
            e.printStackTrace();
        }
    }

    private void transformImage(int width, int height) {
        if (mTextureView == null) {
            return;
        }
        Matrix matrix = new Matrix();
        int rotation = 270;
        RectF textureRectF = new RectF(0, 0, width, height);
        float centerX = textureRectF.centerX();
        float centerY = textureRectF.centerY();
        float scale = (float) 4 / (float) 3;
        matrix.postScale(1 / scale, scale, centerX, centerY);
        matrix.postRotate(rotation, centerX, centerY);
        mTextureView.setTransform(matrix);
    }

    private void createCameraPreview() {
        try {
            SurfaceTexture texture = mTextureView.getSurfaceTexture();
            assert texture != null;

            texture.setDefaultBufferSize(imageDimension.getWidth(), imageDimension.getHeight());
            Surface surface = new Surface(texture);
            captureRequestBuilder = cameraDevice.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW);
            captureRequestBuilder.addTarget(surface);
            //captureRequestBuilder.set(CaptureRequest.JPEG_ORIENTATION, 270);
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
                    Toast.makeText(mActivity, "Configuration Failed!", Toast.LENGTH_SHORT).show();
                }
            }, null);
        } catch (CameraAccessException e) {
            e.printStackTrace();
        }
    }

    private void updatePreview() {
        if (null == cameraDevice) {
            Log.e(TAG, "Error: preview is null");
        }
        captureRequestBuilder.set(CaptureRequest.CONTROL_MODE, CameraMetadata.CONTROL_MODE_AUTO);
        try {
            cameraCaptureSessions.setRepeatingRequest(captureRequestBuilder.build(), null, mBackgroundHandler);
        } catch (CameraAccessException e) {
            e.printStackTrace();
        }
    }

    private void startBackgroundThread() {
        mBackgroundThread = new HandlerThread("Camera-Background");
        mBackgroundThread.start();
        mBackgroundHandler = new Handler(mBackgroundThread.getLooper());
    }
}
