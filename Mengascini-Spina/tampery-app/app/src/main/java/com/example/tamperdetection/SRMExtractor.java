package com.example.tamperdetection;

import android.graphics.Bitmap;

import org.opencv.core.Core;
import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.imgproc.Imgproc;
import org.opencv.android.Utils;

public class SRMExtractor {

    public static Bitmap extract(Bitmap img){
        //Loading the OpenCV core library
        System.loadLibrary( Core.NATIVE_LIBRARY_NAME );

        //Convert the bitmap image into a Mat object
        Mat src = new Mat();
        Mat srcRgb = new Mat();

        Utils.bitmapToMat(img, src);
        Imgproc.cvtColor(src, srcRgb, Imgproc.COLOR_RGBA2RGB);


        float[][] filter1 = {{0, 0, 0, 0, 0},{0, -1, 2, -1, 0},{0, 2, -4, 2, 0},{0, -1, 2, -1, 0},{0, 0, 0, 0, 0}};
        float[][] filter2 = {{-1, 2, -2, 2, -1},{2, -6, 8, -6, 2},{-2, 8, -12, 8, -2},{2, -6, 8, -6, 2},{-1, 2, -2, 2, -1}};
        float[][] filter3 = {{0, 0, 0, 0, 0}, {0, 0, 0, 0, 0}, {0, 1, -2, 1, 0}, {0, 0, 0, 0, 0}, {0, 0, 0, 0, 0}};

        //Create the kernels
        Mat kernel = new Mat(5, 5, CvType.CV_32F);
        for(int i=0; i<5; i++){
            for(int j=0; j<5; j++) {
                kernel.put(i, j, (filter1[i][j] / 4) + (filter2[i][j] / 12) + (filter3[i][j] / 2));
            }
        }

        Mat dst = new Mat();
        Imgproc.filter2D(srcRgb, dst, -1, kernel);

        Bitmap result = Bitmap.createBitmap(img.getWidth(), img.getHeight(), Bitmap.Config.ARGB_8888);
        Utils.matToBitmap(dst, result);

        return result;
    }

}
