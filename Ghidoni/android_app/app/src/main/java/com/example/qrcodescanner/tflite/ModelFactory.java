/*
Copyright 2019 Filippo Aleotti

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

* Author: Filippo Aleotti
* Mail: filippo.aleotti2@unibo.it
*/

package com.example.qrcodescanner.tflite;

import android.content.Context;

import java.util.ArrayList;
import java.util.List;


public class ModelFactory {

    private final Context context;

    private List<Model> models;



    public ModelFactory(Context context){
       this.context = context;
       this.models = new ArrayList<>();
       models.add(createLiteQRNetChar());
    }

    public Model getModel(int index ){
        return models.get(index);
    }



    private Model createLiteQRNetChar(){
        Model qrnet;
        qrnet = new TensorflowLiteModel(context, "QRNet", "tflite");
        qrnet.addInputNode("image", "input/x_image");
        qrnet.addOutputNodes(0, "char_output/output");

        return qrnet;
    }


}


