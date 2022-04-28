package com.example.eq;


import android.content.Context;



import com.example.eq.ml.ConvertedModelV12;


import org.opencv.core.CvType;
import org.opencv.core.Mat;

import org.tensorflow.lite.DataType;

import org.tensorflow.lite.support.tensorbuffer.TensorBuffer;


import java.io.IOException;

import java.util.ArrayList;
import java.util.List;

public class Model {

    private List<Mat> images;
    private ConvertedModelV12 model;
    private String[] dic = {"!", "(", ")", "+", ",", "-", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "=", "[", "]", "a", "alpha", "ascii_124", "b", "beta", "c", "cos", "d", "delta", "div", "e", "exists", "f", "forall", "forward_slash", "g", "gamma", "geq", "gt", "h", "i", "in", "infty", "int", "j", "k", "l", "lambda", "leq", "lim", "log", "lt", "m", "mu", "n", "neq", "o", "p", "phi", "pi", "pm", "prime", "q", "r", "rightarrow", "s", "sigma", "sin", "sqrt", "sum", "t", "tan", "theta", "u", "v", "w", "x", "y", "z", "{", "}"};


    public Model(List<Mat> images, Context context) throws IOException {
        this.images = images;
        this.model = ConvertedModelV12.newInstance(context);
    }

    public String process(){
        String res = "";
        //int cont=0;
        long realStart = System.currentTimeMillis();
        for (Mat image : images){
            image.convertTo(image, CvType.CV_32S);
            int[] rgba = new int[(int)(image.total()*image.channels())];
            image.get(0,0,rgba);
            TensorBuffer input = TensorBuffer.createFixedSize(new int[]{1, 45, 45, 1}, DataType.FLOAT32);
            input.loadArray(rgba,new int[]{1, 45, 45, 1});
            ConvertedModelV12.Outputs outputs = model.process(input);
            TensorBuffer outputFeature = outputs.getOutputFeature0AsTensorBuffer();
            float[] results = outputFeature.getFloatArray();
            res+=""+dic[this.argMax(results)];
        }

        res = res.replace("--", "=");
        res = res.replace("==", "=");
        model.close();
        return res;
    }

    private int argMax(float []data){
        float max = -100;
        int argMax = -1;
        List<Integer> vals = new ArrayList<>();

        for (int i=0; i < data.length; ++i) {
            if (data[i] == max) {
                vals.add(i);
            }
            else if (data[i] > max) {
                vals.clear();
                vals.add(i);
                max = data[i];
                argMax = i;
            }
        }
        if(argMax==-1){
            argMax=0;
        }
        return argMax;
    }

}
