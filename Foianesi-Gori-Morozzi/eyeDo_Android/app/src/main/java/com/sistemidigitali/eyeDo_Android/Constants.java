package com.sistemidigitali.eyeDo_Android;

public class Constants {

    //Pytorch Shapes
    public static final int inputWidth = 768;
    public static final int inputHeight = 576;
    public static final int inputChannels = 3;
    public static final int batchSize = 1;
    public static final float ratio = 4f / 3f;
    //Variables
    public static final int CODE_CAMERA_PERMISSION = 111;
    public static final int consecutiveElaborations = 4;
    //Models
    public static final String normOptF32 = "normalized_opt_float32.pt";
    public static final String nof32 = "not_optimized_float32.pt";
    public static final String oi8 = "optimized_int8.pt";
    public static final String of32 = "optimized_float32.pt";
    //Classes
    public static String[] Classes = new String[]{
            "red", "green", "cGreen", "cBlank", "none"
    };
    public static String CHOSEN_MODEL = oi8;

    //Testing
    public static long startPreElab;
    public static long endPreElab;
    public static long startElab;
    public static long endElab;
}

