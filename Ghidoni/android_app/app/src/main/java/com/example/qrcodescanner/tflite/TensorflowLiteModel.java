package com.example.qrcodescanner.tflite;

import android.content.Context;
import android.content.res.AssetFileDescriptor;
import android.content.res.AssetManager;
import android.graphics.Bitmap;

import androidx.annotation.NonNull;

import com.example.qrcodescanner.Utils;

import org.tensorflow.lite.Interpreter;

import java.io.FileInputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;
import java.nio.IntBuffer;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;


public class TensorflowLiteModel extends Model {
    public final static Integer MAX_SIZE = 15;

    public final static String CHARACTER_SET = "abcdefghijklmnopqrstuvwxyz./:#";



    protected Map<Integer,Interpreter> tfLite;


    private ByteBuffer outputByteBuffer;

    private List<Long> elapsedTimesInference = new ArrayList<>();
    private List<Long> elapsedTimesFill= new ArrayList<>();
    private List<List<Long>> elapsForChar = new ArrayList<>();


    public TensorflowLiteModel(Context context, String name, String checkpoint){
        super(context, name, checkpoint);

        for(int i=0;i<MAX_SIZE;i++){
            elapsForChar.add(new ArrayList<>());
        }

        tfLite = new HashMap();

        Interpreter.Options tfliteOptions = new Interpreter.Options();

        try {
            for(int i = 0; i < MAX_SIZE; i++) {

                String tflitePath = checkpoint+'_'+i+"_quant8.tflite";
                MappedByteBuffer m1 = loadModelFile(context.getAssets(), tflitePath);

                tfLite.put(i,new Interpreter(m1, tfliteOptions));

            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    private MappedByteBuffer loadModelFile(AssetManager assets, String modelFilename)
            throws IOException {
        AssetFileDescriptor fileDescriptor = assets.openFd(modelFilename);
        FileInputStream inputStream = new FileInputStream(fileDescriptor.getFileDescriptor());
        FileChannel fileChannel = inputStream.getChannel();
        long startOffset = fileDescriptor.getStartOffset();
        long declaredLength = fileDescriptor.getDeclaredLength();
        return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength);
    }





    @NonNull
    public String doInference(Bitmap input){

        //Utils.saveReceivedImage(input,input.getWidth(), input.getHeight(),"input",context);


        ByteBuffer inputByteBuffer = null;
        try {
            long start = System.currentTimeMillis();
            inputByteBuffer = fillNetworkInputBuffer(input);
            long elaps = System.currentTimeMillis() - start;
            elapsedTimesFill.add(elaps);
            Utils.printElapsed(elapsedTimesFill,"Mean time for filling input buffer: ");

        } catch (Exception e) {
            return "Not found";
        }
        inputByteBuffer.rewind();
        Object[] inputArray = new Object[tfLite.get(0).getInputTensorCount()];
        inputArray[tfLite.get(0).getInputIndex(getInputNode("image"))] = inputByteBuffer;
        IntBuffer[] nets_output = new  IntBuffer[MAX_SIZE];
        FloatBuffer[] nums = new  FloatBuffer[MAX_SIZE];

     //   long start = System.currentTimeMillis();
        for(int  i = 0; i < MAX_SIZE; i++) {
            inputByteBuffer.rewind();
             Map<Integer, Object> outputMap = new HashMap<>();

            outputByteBuffer = ByteBuffer.allocateDirect(8);
            outputByteBuffer.order(ByteOrder.nativeOrder());
            outputByteBuffer.rewind();
            outputMap.put(tfLite.get(i).getOutputIndex(outputNodes.get(0)), outputByteBuffer);

            ByteBuffer outputPred = ByteBuffer.allocateDirect(4*CHARACTER_SET.length());
            outputPred.order(ByteOrder.nativeOrder());
            outputPred.rewind();
            outputMap.put(tfLite.get(i).getOutputIndex("char_output/Softmax"), outputPred);

           long startchar = System.nanoTime();
            tfLite.get(i).runForMultipleInputsOutputs(inputArray, outputMap);
            long elapschar = System.nanoTime() - startchar;
            elapsForChar.get(i).add(elapschar);
            Utils.printElapsed(elapsForChar.get(i),"Mean time for inference char "+i+": ","ns");

            outputByteBuffer.rewind();
            nets_output[i] = outputByteBuffer.asIntBuffer();
            outputPred.rewind();
            nums[i] = outputPred.asFloatBuffer();

        }
        String decodedString = convertInferenceToString(nets_output);
      /*  long elaps = System.currentTimeMillis() - start;
        elapsedTimesInference.add(elaps);
        Utils.printElapsed(elapsedTimesInference,"Mean time for inference: ");*/
        System.out.println(decodedString);
        nets_output[0].rewind();
        nums[0].rewind();

       return decodedString; //+ " pred: " + nums[0].get(nets_output[0].get());
    }





    public ByteBuffer fillNetworkInputBuffer(Bitmap input) {
        int width = input.getWidth();
        int height = input.getHeight();

        int[] intInputPixels = new int[width*height];

        input.getPixels(intInputPixels, 0, width, 0, 0, width, height);

        int pixel = 0;
        ByteBuffer inputByteBuffer = ByteBuffer.allocateDirect(width*height* 4);
        inputByteBuffer.order(ByteOrder.nativeOrder());
        for (int i = 0; i < width; ++i) {

            for (int j = 0; j <height; ++j) {

                int val = intInputPixels[pixel++];


                if(val == -1) {

                    inputByteBuffer.putFloat(1.0f);
                } else {
                    inputByteBuffer.putFloat(0.0f);
                }


            }
        }

        return inputByteBuffer;
    }

    private char convertInferenceToChar(IntBuffer in){
        return TensorflowLiteModel.CHARACTER_SET.charAt(in.get());
    }

    private String convertInferenceToString(IntBuffer[] in){
        StringBuilder sb = new StringBuilder();
        for(IntBuffer i : in) {
            char charConverted = convertInferenceToChar(i);
           /* if(charConverted == '#' && sb.length() == 0) {
               return "No Qr code found";
            } else if (charConverted == '#') {
                break;
            } else {
                sb.append(charConverted);
            }*/
            sb.append(charConverted);
        }
        return sb.toString();
    }
}
