package com.example.qrcodescanner;

import android.Manifest;
import android.content.Context;
import android.hardware.Camera;
import android.os.Handler;
import android.os.HandlerThread;
import android.util.Size;

import com.example.qrcodescanner.tflite.Inference;

public final class PreviewCallback implements Camera.PreviewCallback {
    private static final Logger LOGGER = new Logger();

    private static final int PERMISSIONS_REQUEST = 1;

    private static final String PERMISSION_CAMERA = Manifest.permission.CAMERA;
    private static final String PERMISSION_STORAGE = Manifest.permission.WRITE_EXTERNAL_STORAGE;

    private boolean debug = false;

    private Handler inferenceHandler;
    private HandlerThread inferenceHandlerThread;
    private Handler handler;
    private HandlerThread handlerThread;
    private boolean useCamera2API;
    private boolean isProcessingFrame = false;
    private byte[][] yuvBytes = new byte[3][];

    private int yRowStride;

    protected int previewWidth = 0;
    protected int previewHeight = 0;

    private Runnable postInferenceCallback;

    private Inference inf;
    private DecoderWrapper mDecoderWrapper;
    private Context mContext;
    private CodeScannerView mScannerView;
    public boolean init = false;


    public PreviewCallback(Inference inf,DecoderWrapper decoderWrapper,Context ctx,CodeScannerView view) {
        this.mDecoderWrapper = decoderWrapper;
        this.inf = inf;
        mContext = ctx;
        mScannerView = view;
    }

    @Override
    public void onPreviewFrame(final byte[] data, final Camera camera) {
        //see row 859 CodeScanner for the formats
       Utils.saveReceivedImage(data,1280,            960,"raw",mContext);


        if (isProcessingFrame) {
          //  LOGGER.w("Dropping frame!");
            return;
        }

        try {
            // Initialize the storage bitmaps once when the resolution is known.
            if (!init) {
                Camera.Size previewSize = camera.getParameters().getPreviewSize();
                previewHeight = previewSize.height;
                previewWidth = previewSize.width;

                inf.initialize(new Size(previewSize.width, previewSize.height));
                init = true;
            }
        } catch (final Exception e) {
            LOGGER.e(e, "Exception!");
            return;
        }

        isProcessingFrame = true;


        inf.setDataToInference(data);



        final DecoderWrapper decoderWrapper = mDecoderWrapper;
        if (decoderWrapper == null) {
            return;
        }




        final Decoder decoder = decoderWrapper.getDecoder();
        if (decoder.getState() != Decoder.State.IDLE && decoder.getState() != Decoder.State.INITIALIZED) {
            return;
        }
        final Rect frameRect = mScannerView.getFrameRect();
        if (frameRect == null || frameRect.getWidth() < 1 || frameRect.getHeight() < 1) {
            return;
        }

        decoder.scheduleDecodeTask(new DecodeTask(data, decoderWrapper.getImageSize(),
                decoderWrapper.getPreviewSize(), decoderWrapper.getViewSize(), frameRect,
                decoderWrapper.getDisplayOrientation(),
                decoderWrapper.shouldReverseHorizontal(),mContext,inf));
    }



    public void readyForNextFrame() {
        isProcessingFrame = false;
    }

}