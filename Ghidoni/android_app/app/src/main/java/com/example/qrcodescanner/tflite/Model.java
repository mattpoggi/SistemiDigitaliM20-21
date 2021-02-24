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
import android.graphics.Bitmap;

import java.util.HashMap;
import java.util.Map;


public abstract class Model{

    protected final String checkpoint;
   protected Map<Integer,String> outputNodes;
    protected String name;
    protected HashMap<String, String> inputNodes;
    protected Context context;

    public Model(Context context,  String name, String checkpoint){
        this.name = name;
        this.outputNodes = new HashMap<>();
        this.inputNodes = new HashMap<>();
        this.checkpoint = checkpoint;
        this.context = context;


    }


    public void addOutputNodes(Integer string_index, String node){
            this.outputNodes.put(string_index,node);
    }

    public void addInputNode(String name, String node){
        if(!this.inputNodes.containsKey(name))
            this.inputNodes.put(name, node);
    }

    public String getInputNode(String name){
        return this.inputNodes.get(name);
    }

    public abstract String doInference(Bitmap input);


}


