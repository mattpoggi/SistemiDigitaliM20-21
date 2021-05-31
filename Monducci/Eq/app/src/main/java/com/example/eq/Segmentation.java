package com.example.eq;

import android.graphics.Bitmap;

import org.opencv.android.Utils;
import org.opencv.core.*;
import org.opencv.imgproc.Imgproc;

import java.util.*;

public class Segmentation {

    private Mat img = new MatOfFloat();

    public Segmentation(Bitmap bmp32){
        Utils.bitmapToMat(bmp32, img);
    }

    public List<Mat> segment(){
        List<Mat> images = new ArrayList<Mat>();
        Mat gray = new Mat();
        Mat thresh = new Mat();
        Mat hierarchy = new Mat();
        double ret;
        List<MatOfPoint> contours = new ArrayList<MatOfPoint>();
        List<MatOfPoint> sorted_contours;
        Imgproc.cvtColor(img,gray,Imgproc.COLOR_BGR2GRAY);
        ret = Imgproc.threshold(gray,thresh,127,255,Imgproc.THRESH_BINARY_INV);
        Imgproc.findContours(thresh,contours,hierarchy, Imgproc.RETR_TREE, Imgproc.CHAIN_APPROX_SIMPLE);
        sorted_contours = this.sort(contours);


        for (MatOfPoint contour : sorted_contours){
            Rect dims;
            Mat image;
            dims = Imgproc.boundingRect(contour);
            image = img.submat(dims);
            image = this.makeSquare(image);
            Imgproc.resize(image, image, new Size(45,45));
            Imgproc.cvtColor(image,image,Imgproc.COLOR_RGBA2GRAY);
            images.add(image);
        }
        return images;
    }

    private List<MatOfPoint> sort(List<MatOfPoint> contours){
        Map<MatOfPoint,Rect> map = new HashMap<MatOfPoint,Rect>();
        for (MatOfPoint contour : contours){
            map.put(contour,Imgproc.boundingRect(contour));
        }
        List<Map.Entry<MatOfPoint, Rect>> list = new ArrayList<>(map.entrySet());
        list.sort(Map.Entry.comparingByValue(Comparator.comparing((Rect r)->r.x)));

        List<MatOfPoint> result = new ArrayList<>();
        for (Map.Entry<MatOfPoint, Rect> entry : list) {
            result.add(entry.getKey());
        }

        return result;

    }

    private Mat makeSquare(Mat image){
        int x = image.height();
        int y = image.width();
        double dif;
        Mat result = new Mat();
        if (x<y){
            dif = y-x;
            Core.copyMakeBorder(image, result, (int)Math.ceil(dif/2.0), (int)Math.floor(dif/2.0),
                    0,0,Core.BORDER_REPLICATE);
        }
        else if (x>y){
            dif = x-y;
            Core.copyMakeBorder(image, result, 0, 0, (int)Math.ceil(dif/2.0),
                    (int)Math.floor(dif/2.0),Core.BORDER_REPLICATE);
        }
        else{
            result = image;
        }
        return result;
    }

}
