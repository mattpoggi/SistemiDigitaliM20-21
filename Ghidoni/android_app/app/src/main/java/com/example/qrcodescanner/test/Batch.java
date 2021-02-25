package com.example.qrcodescanner.test;

import android.graphics.Bitmap;

import java.util.Collection;
import java.util.Collections;
import java.util.List;

public class Batch {
    private List<Bitmap> images;
    private String label;

    public Batch(List<Bitmap> im, String l) {
        images = im;
        label = l;
    }

    public List<Bitmap> getImages() {
        return images;
    }

    public String getLabel(){
        return label;
    }
}
