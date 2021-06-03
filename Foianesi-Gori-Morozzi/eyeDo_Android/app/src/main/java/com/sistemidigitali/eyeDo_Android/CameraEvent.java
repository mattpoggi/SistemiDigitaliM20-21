package com.sistemidigitali.eyeDo_Android;

import android.graphics.Bitmap;

public interface CameraEvent {
    void internalElaboration(Bitmap data, String imgFormat);
    //void onChangeSizeCapture(int width, int height);
    void startElab();
    void endElab();
    boolean isInElaboration();
}
