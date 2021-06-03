package com.example.qrcodescanner.tflite;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Matrix;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.Looper;
import android.util.Size;

import com.example.qrcodescanner.CodeScanner;
import com.example.qrcodescanner.PreviewCallback;
import com.example.qrcodescanner.Utils;

import java.util.ArrayList;
import java.util.List;

public class Inference {
    private PreviewCallback mPreviewCallback;
    private ModelFactory modelFactory;
    private Model currentModel;
    private Integer sensorOrientation;
    private Matrix frameToCropTransform;
    private Size halfScreenSize = null;
    private Size screenSize = null;
    private Bitmap originalFrame = null;
    private static final boolean MAINTAIN_ASPECT = true;
    private static float COLOR_SCALE_FACTOR =  10.5f;
    private static int NUMBER_THREADS = Runtime.getRuntime().availableProcessors();
    private int previewWidth;
    private int previewHeight;
    private HandlerThread backThread;
    private Handler looper;
    private int[] rgbBytes = null;

    private Runnable imageConverter;
    private Context mContext;
    private byte[] mYuvData;
    private CodeScanner scanner;
private Handler mMainHandler;
    private List<Long> elapsedTimesRotRescale = new ArrayList<>();
    List<Long> elapsedTimesBinarize= new ArrayList<>();
    private List<Long> elapsedTimesCutting= new ArrayList<>();
    private List<Long> elapsedTimesSampling= new ArrayList<>();

    public Inference(PreviewCallback prev, Context ctx) {
       backThread = new HandlerThread("inference");
        backThread.start();
        looper = new Handler(backThread.getLooper());

        mPreviewCallback = prev;
        mContext = ctx;
    }

    public Inference( Context ctx, CodeScanner s) {
        modelFactory = new ModelFactory(ctx);
        currentModel = modelFactory.getModel(0);

        mContext = ctx;
        scanner = s;

        // Get a handler that can be used to post to the main thread
        mMainHandler = new Handler(Looper.getMainLooper());
    }

    public void initialize(final Size size) {
        previewWidth = size.getWidth();
        previewHeight = size.getHeight();
        sensorOrientation = 90;
        originalFrame = Bitmap.createBitmap(previewWidth, previewHeight, Bitmap.Config.ARGB_8888);

        rgbBytes = new int[previewWidth * previewHeight];



    }

    public String processImageAndDoInference(Bitmap submap) throws Exception {
        if(mPreviewCallback == null) {
            throw new Exception("You must initialize preview callback inside Inference");
        }


       // Utils.saveReceivedImage(submap,694,            694,"original",mContext);
      //  final Canvas canvas = new Canvas(croppedFrame);
       // canvas.drawBitmap(submap, frameToCropTransform, null);
       //Utils.saveReceivedImage(croppedFrame,resolution.getWidth(),            resolution.getHeight(),"resized",mContext);
        Bitmap inputNetworkBitmap;
        try {
        //################    STAGE 2:  COLOR -> GRAY ###################

        Utils.saveReceivedImage(submap,submap.getWidth(), submap.getHeight(),"input",mContext);
        //wxe = 694x694
            long start = System.currentTimeMillis();
            Bitmap grayBitmap = ImagePreprocessing.binarize(submap);
            long elaps = System.currentTimeMillis() - start;

            elapsedTimesBinarize.add(elaps);
            Utils.printElapsed(elapsedTimesBinarize,"Mean time for binarize: ");

        Utils.saveReceivedImage(grayBitmap,grayBitmap.getWidth(), grayBitmap.getHeight(),"grayed",mContext);

        //################    STAGE 3: CUT WHITE BORDER AROUND QR ###################

             start = System.currentTimeMillis();
            Bitmap cutted = ImagePreprocessing.cutWhiteBorder(grayBitmap);
             elaps = System.currentTimeMillis() - start;
            elapsedTimesCutting.add(elaps);
            Utils.printElapsed(elapsedTimesCutting,"Mean time for cutting: ");

        Utils.saveReceivedImage(cutted,cutted.getWidth(), cutted.getHeight(),"cutted",mContext);

        //################    STAGE 4: SAMPLING ###################
        Bitmap p = null;

             start = System.currentTimeMillis();
            p=ImagePreprocessing.extractPureBits(cutted);
             elaps = System.currentTimeMillis() - start;
            elapsedTimesSampling.add(elaps);
            Utils.printElapsed(elapsedTimesSampling,"Mean time for sampling: ");

            Utils.saveReceivedImage(p,p.getWidth(), p.getHeight(),"matrix",mContext);

            // Bitmap pooled = pooling(cutted);
            // Utils.saveReceivedImage(pooled,pooled.getWidth(), pooled.getHeight(),"pooled",context);


        //#####################   STAGE 5:  90° ROTATION #################

             start = System.currentTimeMillis();
            inputNetworkBitmap =  ImagePreprocessing.applyRotationRescaling(p);
             elaps = System.currentTimeMillis() - start;
            elapsedTimesRotRescale.add(elaps);
            Utils.printElapsed(elapsedTimesRotRescale,"Mean time for rotationRescale: ");

        Utils.saveReceivedImage(inputNetworkBitmap,inputNetworkBitmap.getWidth(), inputNetworkBitmap.getHeight(),"inputNet",mContext);
        } catch(Exception e) {
            mPreviewCallback.readyForNextFrame();
            return "Not found";
        }

        final String  inference = currentModel.doInference(inputNetworkBitmap);

       //update view input net
        mMainHandler.post(() -> {
            Matrix frameToCropTransform = ImageUtils.getTransformationMatrix(
                    25, 25,
                    100, 100,
                    0, true);

            Bitmap h = Bitmap.createBitmap(100,100, Bitmap.Config.ARGB_8888);
            final Canvas canvas = new Canvas(h);

            canvas.drawBitmap(inputNetworkBitmap, frameToCropTransform, null);
            scanner.setInputNetBitmap(h);

        });


        mPreviewCallback.readyForNextFrame();

        return inference;
    }

    public Bitmap getOriginalBitmap() {
        return originalFrame;
    }



    public void setDataToInference(byte[] data) {
        mYuvData = data;

    }

    List<Long> elapsedTimesConversion = new ArrayList<>();
    public void runYuvRgbConversion() {

        long start = System.currentTimeMillis();
        ImageUtils.convertYUV420SPToARGB8888(mYuvData, previewWidth, previewHeight, rgbBytes);
        long elaps = System.currentTimeMillis() - start;
        elapsedTimesConversion.add(elaps);
        Utils.printElapsed(elapsedTimesConversion,"Mean time for yuv conversion: ");

        originalFrame.setPixels(rgbBytes, 0, previewWidth, 0, 0, previewWidth, previewHeight);
    }

    public void setPreviewCallback(PreviewCallback prev) {
        this.mPreviewCallback = prev;
    }

}
