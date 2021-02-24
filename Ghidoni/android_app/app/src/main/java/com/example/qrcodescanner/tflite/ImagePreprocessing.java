package com.example.qrcodescanner.tflite;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Matrix;

import java.nio.IntBuffer;
import java.util.ArrayList;
import java.util.List;

public class ImagePreprocessing {
    public final static Integer CENTRAL_QUAD_RESOLUTION = 25;
    public final static Integer NET_INPUT_RESOLUTION = 25;
    private static final int BLACK_TH = 10;

    /**
     * This method detects a code in a "pure" image -- that is, pure monochrome image
     * which contains only an unrotated, unskewed, image of a code, with some white border
     * around it. This is a specialized method that works exceptionally fast in this special
     * case.
     */
    public static Bitmap extractPureBits(Bitmap image) {
        float height = image.getHeight();
        float width = image.getWidth();
        float moduleSize = ((height + width) / 2.0f) / 25.0f;

        int top = 0;
        int bottom = (int) height;
        int left = 0;
        int right = (int) width;

        // Sanity check!
        if (left >= right || top >= bottom) {
            throw new RuntimeException("Exception");
        }


        int matrixWidth = Math.round((right - left + 1) / moduleSize);
        int matrixHeight = Math.round((bottom - top + 1) / moduleSize);
        if (matrixWidth <= 0 || matrixHeight <= 0) {
            throw new RuntimeException("Exception");
        }
        if (matrixHeight != matrixWidth) {
            // Only possibly decode square regions
            throw new RuntimeException("Exception");
        }

        // Push in the "border" by half the module width so that we start
        // sampling in the middle of the module. Just in case the image is a
        // little off, this will help recover.
        int nudge = (int) (moduleSize / 2.0f);
        top += nudge;
        left += nudge;

        // But careful that this does not sample off the edge
        // "right" is the farthest-right valid pixel location -- right+1 is not necessarily
        // This is positive by how much the inner x loop below would be too large
        int nudgedTooFarRight = left + (int) ((matrixWidth - 1) * moduleSize) - right;
        if (nudgedTooFarRight > 0) {
            if (nudgedTooFarRight > nudge) {
                // Neither way fits; abort
                throw new RuntimeException("Exception");
            }
            left -= nudgedTooFarRight;
        }
        // See logic above
        int nudgedTooFarDown = top + (int) ((matrixHeight - 1) * moduleSize) - bottom;
        if (nudgedTooFarDown > 0) {
            if (nudgedTooFarDown > nudge) {
                // Neither way fits; abort
                throw new RuntimeException("Exception");
            }
            top -= nudgedTooFarDown;
        }

        // Now just read off the bits
        IntBuffer out = IntBuffer.allocate(matrixWidth*matrixHeight);
        for (int y = 0; y < matrixHeight; y++) {
            int iOffset = top + (int) (y * moduleSize);
            for (int x = 0; x < matrixWidth; x++) {
                if (image.getPixel(left + (int) (x * moduleSize), iOffset) ==  -1) {
                    out.put(-1);
                } else {
                    out.put(0xff000000);
                }
            }
        }
        Bitmap b = Bitmap.createBitmap(out.array(),matrixWidth,matrixHeight, Bitmap.Config.ARGB_8888);
        return b;
    }



    public static Bitmap cutWhiteBorder(Bitmap grayBitmap) {
        int width = grayBitmap.getWidth();
        int height = grayBitmap.getHeight();
        int[] intInputPixels = new int[width*height];

        grayBitmap.getPixels(intInputPixels, 0, width, 0, 0, width, height);

        List<List<Integer>> cuttedRowImage = new ArrayList<>();

        int pixel = 0;

        for (int i = 0; i < height; ++i) {
            List<Integer> row = new ArrayList<>();
            int black = 0;
            for (int j = 0; j < width; ++j) {
                int val = intInputPixels[pixel++];
                if(val != -1) {
                    black++;
                }
                row.add(val);
            }
            if(black >= BLACK_TH) {
                cuttedRowImage.add(row);
            }
        }


        List<List<Integer>> cuttedImage = new ArrayList<>();
        for(int u = 0; u < cuttedRowImage.size(); u++){
            cuttedImage.add(new ArrayList<>());
        }

        for (int i = 0; i < width; ++i) {
            List<Integer> col = new ArrayList<>();
            int black = 0;
            for (int j = 0; j < cuttedRowImage.size(); ++j) {
                int val = cuttedRowImage.get(j).get(i);
                if(val != -1) {
                    black++;
                }
                col.add(val);
            }
            if(black >= BLACK_TH) {
                for(int u = 0; u < cuttedRowImage.size(); u++){
                    cuttedImage.get(u).add(col.get(u));
                }
            }
        }

        int[] finalCuttedImage = new int[cuttedImage.get(0).size()*cuttedImage.size()];
        for(int h = 0; h < cuttedImage.size(); h++){
            for(int f = 0; f < cuttedImage.get(0).size(); f++) {
                try {
                    finalCuttedImage[h * cuttedImage.get(0).size() + f] = cuttedImage.get(h).get(f);
                }catch(Exception e){
                    System.out.println(e);
                }
            }
        }

        return Bitmap.createBitmap(finalCuttedImage,cuttedImage.get(0).size(),cuttedImage.size(), Bitmap.Config.ARGB_8888);
    }


    public static Bitmap binarize(Bitmap input) {
        int width = input.getWidth();
        int height = input.getHeight();
        int[] intInputPixelsColored = new int[width*height];

        input.getPixels(intInputPixelsColored, 0, width, 0, 0, width, height);


        IntBuffer gray_image = IntBuffer.allocate(width*height);
        // Convert the image to floating point.
        int pixel = 0;
        int white = 0;
        int black = 0;
        int too_white = 0;
        for (int i = 0; i < width; ++i) {

            for (int j = 0; j < height; ++j) {

                int val = intInputPixelsColored[pixel++];
                if(val == 0) {
                    too_white++;
                }
                float b = (val >> 16) & 0xFF;
                float g = (val >> 8) & 0xFF;
                float r = (val) & 0xFF;

                float gray = (r+g+b)/3;

                if(gray < 127) {
                    //32 zeri = 0
                    gray_image.put(0xff << 24 + 0);
                    black++;
                } else {
                    // 32 uni = -1
                    gray_image.put((0xff << 24) + (0xff << 16)+(0xff << 8)+(0xff));
                    white++;
                }

            }
        }
        return Bitmap.createBitmap(gray_image.array(),width,height, Bitmap.Config.ARGB_8888);
    }

    public static Bitmap crop(Bitmap input,int top, int left, int width, int height) {
        return Bitmap.createBitmap(input,top, left,width,height);
    }

    public static Bitmap applyRotationRescaling(Bitmap input) {
        Matrix matrix = ImageUtils.getTransformationMatrix(
                CENTRAL_QUAD_RESOLUTION, CENTRAL_QUAD_RESOLUTION,
                NET_INPUT_RESOLUTION, NET_INPUT_RESOLUTION,
                90, true);

        Bitmap inputNetworkBitmap = Bitmap.createBitmap(NET_INPUT_RESOLUTION,NET_INPUT_RESOLUTION, Bitmap.Config.ARGB_8888);
        final Canvas canvas = new Canvas(inputNetworkBitmap);
        canvas.drawBitmap(input, matrix, null);

        return inputNetworkBitmap;
    }


}
