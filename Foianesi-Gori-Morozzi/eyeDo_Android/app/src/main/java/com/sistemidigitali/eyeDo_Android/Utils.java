package com.sistemidigitali.eyeDo_Android;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Matrix;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.util.Log;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

public class Utils {

    public static int argMax(float[] inputs) {
        int maxIndex = -1;
        float maxvalue = 0.0f;
        for (int i = 0; i < inputs.length; i++) {
            if (inputs[i] > maxvalue) {
                maxIndex = i;
                maxvalue = inputs[i];
            }
        }
        return maxIndex;
    }

    public static String assetFilePath(Context context, String assetName) {
        File file = new File(context.getFilesDir(), assetName);
        try (InputStream is = context.getAssets().open(assetName)) {
            try (OutputStream os = new FileOutputStream(file)) {
                byte[] buffer = new byte[4 * 1024];
                int read;
                while ((read = is.read(buffer)) != -1) {
                    os.write(buffer, 0, read);
                }
                os.flush();
            }
            return file.getAbsolutePath();
        } catch (IOException e) {
            Log.e("test", "Error process asset " + assetName + " to file path");
        }
        return null;
    }

    //Permissions
    public static boolean need_requestCAMERAandWRITEPermissions(Activity activity) {
        int permission2 = ContextCompat.checkSelfPermission(activity, Manifest.permission.CAMERA);
        if (permission2 != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(activity, new String[]{Manifest.permission.CAMERA, Manifest.permission.WRITE_EXTERNAL_STORAGE}, Constants.CODE_CAMERA_PERMISSION);
            return true;
        }
        return false;
    }

    /**
     * Funzione che produce in uscita un Bitmap che viene ridimensionato a qualsiasi nuova altezza e larghezza, mantenendo le proporzioni
     * Se le nuove altezza e larghezza risultino essere non proporzionali rispetto al Bitmap in entrata, allora si mantiene comunque la proporzione
     * riempendo di nero gli spazi in eccesso.
     * Attenzione: testata solo per far entrare in QUADRATI qualsiasi immagine in ingresso. Mantiene le proporzioni e 'fa entrare' in quadrati qualsiasi immagine
     * TIME < 1ms
     *
     * @param in   Bitmap in ingresso
     * @param newH Nuova altezza
     * @param newW Nuova larghezza
     * @return Nuovo Bitmap ridimensionato
     */
    public static Bitmap resize(Bitmap in, int newH, int newW) {

        Bitmap out = Bitmap.createBitmap(newH, newW, Bitmap.Config.ARGB_4444);
        int inW = in.getWidth();
        int inH = in.getHeight();
        int H;
        int W;

        Bitmap resized = null;

        /*
        1) RIDIMENSIONIAMO L'IMMAGINE ALLA DIMENSIONE MASSIMA VOLUTA MANTENENDO L'ASPECT RATIO
        */
        if (inH < inW) {
            float ratio = (float) inW / newW;
            H = (int) (inH / ratio);
            resized = Bitmap.createScaledBitmap(in, newW, H, true);

            //se filter=false , l'immagine non viene filtrata--> maggiori performance, peggiore qualità
        }
        if (inH > inW) {
            float ratio = (float) inH / newH;
            W = (int) (inW / ratio);
            resized = Bitmap.createScaledBitmap(in, W, newH, true);

            //se filter=false , l'immagine non viene filtrata--> maggiori performance, peggiore qualità
        }
        if (inH == inW) {
            resized = Bitmap.createScaledBitmap(in, newW, newH, true);

        }

        /*
        2) Creiamo il contenitore finale della nostra immagine e riempiamo manualmente i pixel
         */
        out = Bitmap.createBitmap(newW, newH, resized.getConfig());
        Canvas canvas = new Canvas(out);
        canvas.drawBitmap(resized, new Matrix(), null);

        return out;
    }


    public static String pathCombine(String... paths) {

        File finalPath = new File(paths[0]);

        for (int i = 1; i < paths.length; i++) {
            finalPath = new File(finalPath, paths[i]);
        }

        return finalPath.getPath();
    }

    public static Long calculateAverage(List<Long> nums) {
        Long sum = 0l;
        if (!nums.isEmpty()) {
            for (Long mark : nums) {
                sum += mark;
            }
            return sum / nums.size();
        }
        return sum;
    }

    public static Bitmap rotate(Bitmap bitmap, float degrees) {
        Matrix matrix = new Matrix();
        matrix.postRotate(degrees);
        float scale = (float) 4 / (float) 3;
        int centerX = bitmap.getWidth() / 2;
        int centerY = bitmap.getHeight() / 2;
        matrix.postScale(scale, 1 / scale, centerX, centerY);
        return Bitmap.createBitmap(bitmap, 0, 0, bitmap.getWidth(), bitmap.getHeight(), matrix, true);
    }
}
