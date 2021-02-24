package com.example.qrcodescanner.test;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;

import com.example.qrcodescanner.Utils;
import com.example.qrcodescanner.test.Batch;
import com.example.qrcodescanner.tflite.ImagePreprocessing;
import com.example.qrcodescanner.tflite.Model;
import com.example.qrcodescanner.tflite.TensorflowLiteModel;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class TestNetwork {

    private final static String datasetFolder = "/storage/external_SD/test_dataset_25";

    private Model model;

    public TestNetwork(Model m) {
        model = m;
    }

    //for damaged qr
    private Batch getValidationBatch(String id, boolean t) {
        String mainDirPath = datasetFolder + File.separator + id;
        List<Bitmap> images = new ArrayList<>();

        for(int i = 0; i < 3; i++){
            images.add(BitmapFactory.decodeFile(mainDirPath+File.separator+i+".jpg"));
        }
        String label = null;
        try {
            BufferedReader buf = new BufferedReader(new FileReader(mainDirPath + File.separator + "label.txt"));
             label = buf.readLine();
             StringBuilder sb = new StringBuilder();
             for(int i=0;i < TensorflowLiteModel.MAX_SIZE - label.length(); i++){
                 sb.append('#');
             }
             label = label + sb.toString();
            buf.close();
        } catch(Exception e){
            System.out.println("Exception reading label file" + e.getMessage());
            System.exit(0);
        }
        return new Batch(images, label);
    }

    //for perfect qr
    private Batch getValidationBatch(String id) {
        String mainDirPath = datasetFolder + File.separator + id;
        List<Bitmap> images = new ArrayList<>();

        images.add(BitmapFactory.decodeFile(mainDirPath+File.separator+"original.jpg"));

        String label = null;
        try {
            BufferedReader buf = new BufferedReader(new FileReader(mainDirPath + File.separator + "label.txt"));
            label = buf.readLine();
            StringBuilder sb = new StringBuilder();
            for(int i=0;i < TensorflowLiteModel.MAX_SIZE - label.length(); i++){
                sb.append('#');
            }
            label = label + sb.toString();
            buf.close();
        } catch(Exception e){
            System.out.println("Exception reading label file " + e.getMessage());
            System.exit(0);
        }
        return new Batch(images, label);
    }



    private List<Bitmap>  convertToGray(Batch b){
        List<Bitmap> networkInput = new ArrayList<>();
        for(Bitmap img :  b.getImages()) {
            networkInput.add(ImagePreprocessing.binarize(img));
        }

        return networkInput;
    }

    public void test() {

        File datasetDir = new File(datasetFolder);

        int[] neterr = new int[TensorflowLiteModel.MAX_SIZE];
        Arrays.fill(neterr,0);
        List<Long> elapsedTimes = new ArrayList<>();

        File[] files = datasetDir.listFiles();
        int numFiles = files.length;
        int current = 0;

       /*Map<DecodeHintType, Object> hints = new EnumMap<>(DecodeHintType.class);
        //hints.put(DecodeHintType.POSSIBLE_FORMATS, Collections.unmodifiableList(Arrays.asList(BarcodeFormat.QR_CODE)));
       // hints.put(DecodeHintType.PURE_BARCODE, Boolean.TRUE);
        final MultiFormatReader reader = BarcodeUtils.createReader(hints);*/

        int zxing = 0;
        System.out.println("Testing in progress...");
        for(File f : files) {

            Batch batch = getValidationBatch(f.getName());
            List<Bitmap> netInput = convertToGray(batch);

            for(Bitmap input : netInput) {
                long start = System.currentTimeMillis();
                String decodedString = model.doInference(input);
                long elaps = System.currentTimeMillis() - start;
                elapsedTimes.add(elaps);
                for(int c = 0; c  < TensorflowLiteModel.MAX_SIZE; c++) {
                    if (decodedString.charAt(c) != batch.getLabel().charAt(c)) {
                        neterr[c]++;
                    }
                }

              /* Result r = BarcodeUtils.decodeBitmap(input,reader,true);
                if(r == null) {
                    zxing++;
                }
                else if(!r.getText().equals(batch.getLabel().split("#")[0])) {
                    zxing++;
                }*/

            }


            System.out.println("Tested "+current+" out of "+numFiles);
            current++;
        }
        System.out.println("Testing perfetti complete");

        Utils.printElapsed(elapsedTimes,"Mean time for inference: ");
        int pos = 0;
        for(int c : neterr) {
            System.out.println("Network error position "+pos+" = " + c);
            pos++;
        }
        System.out.println("zxing error = " + zxing);
    }

}
