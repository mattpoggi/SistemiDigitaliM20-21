package com.MSL.multicameradepth.listeners;

import java.util.TreeMap;


public interface PictureCapturingListener {


    void onCaptureDone(String pictureUrl, byte[] pictureData);

    /**
     * il callback viene chiamato quando sono state acquisite le immagini da tutte le camere
     */
    void onDoneCapturingAllPhotos(TreeMap<String, byte[]> picturesTaken);

}
