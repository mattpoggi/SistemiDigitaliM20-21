package com.sistemidigitali.eyeDo_Android;

import android.content.Context;
import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.Handler;
import android.support.v7.app.AppCompatActivity;
import android.view.TextureView;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.util.ArrayList;

import static com.sistemidigitali.eyeDo_Android.Utils.assetFilePath;


public class MainActivity extends AppCompatActivity implements CameraEvent {

    Classifier classifier;
    Bitmap rotated;
    ArrayList<Long> elabTimes;
    ArrayList<Long> preElabTimes;
    private MyCamera camera;
    private TextureView textureView;
    private boolean waitFor = false;
    private TextView textView;
    private SoundThread sound;
    private String[] lastStates;
    private ImageView iv;

    @Override
    protected void onResume() {
        super.onResume();
        begin();
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Utils.need_requestCAMERAandWRITEPermissions(this);

        iv = findViewById(R.id.tlView);
        textView = findViewById(R.id.textView);
        textView.setVisibility(View.GONE);
        textureView = findViewById(R.id.texture);
        findViewById(R.id.settings).setVisibility(View.VISIBLE);

        iv.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                iv.setVisibility(View.GONE);
                textView.setVisibility(View.VISIBLE);
            }
        });
        textView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                textView.setVisibility(View.GONE);
                iv.setVisibility(View.VISIBLE);
            }
        });

        //after onCreate(), onResume() is always called
        //begin();
        elabTimes = new ArrayList<>();
        preElabTimes = new ArrayList<>();
        lastStates = new String[Constants.consecutiveElaborations];

    }

    private void begin() {
        //camera is not accessed, but it's necessary to instantiate it in order to activate the view
        camera = new Camera2(this, this, textureView);
        classifier = new Classifier(assetFilePath(this, Constants.CHOSEN_MODEL), this);
        sound = new SoundThread();
        sound.start();

        //Make tipsToast if it's the first time in the app :)
        Handler handler = new Handler();
        final Runnable r = new Runnable() {
            public void run() {
                handler.postDelayed(this, 10000);
                try {
                    File f = new File(getApplicationContext().getFilesDir() + "/notFirstTime");
                    if (!f.exists()) {
                        f.createNewFile();
                        Context context = getApplicationContext();

                        CharSequence text = "If you don't see the camera, please restart the app!";
                        int duration = Toast.LENGTH_LONG;
                        Toast toast = Toast.makeText(context, text, duration);
                        toast.show();
                        text = "You can click on the TrafficLight to see the stats (and vice-versa)! :)";
                        toast = Toast.makeText(context, text, duration);
                        toast.show();

                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        };
        handler.postDelayed(r, 5500);
    }

    public void buttonHandler(View view) {
        switch (view.getId()) {
            case R.id.settings:
                onPauseCapture();
                Intent i = new Intent(this, SettingsPage.class);
                startActivityForResult(i, 100);
                break;
        }
    }

    @Override
    protected void onStop() {
        //paying attention to bitmap recycling
        sound.setKeepGoing(false);
        super.onStop();
    }

    @Override
    protected void onPause() {
        //paying attention to bitmap recycling
        sound.setKeepGoing(false);
        super.onPause();
    }

    void onPauseCapture() {
        /*
        possibly useful
        */
    }

    @Override
    public void internalElaboration(Bitmap data, String imgFormat) {
        rotated = Utils.rotate(data, 270);

        String predicted = classifier.predict(rotated);
        rotated.recycle();
        data.recycle();
        data = null;
        rotated = null;

        showResults(predicted);
        endElab();
    }

    private void showResults(String predicted) {
        //Add state to lastStates and shift
        for (int i = 1; i < lastStates.length; i++) {
            lastStates[i] = lastStates[i - 1];
        }
        lastStates[0] = predicted;
        //Check if it's the right moment to change State (after 4 equal results)
        boolean allEquals = true;
        for (int i = 1; i < lastStates.length; i++) {
            if (lastStates[0] == null || lastStates[i] == null || !lastStates[i].equals(lastStates[0])) {
                allEquals = false;
                break;
            }
        }
        if (allEquals) {
            for (int i = 0; i < Constants.Classes.length; i++) {
                if (Constants.Classes[i].equals(lastStates[0])) {
                    //Change Traffic Light Image
                    if (i == 0)
                        runOnUiThread(() -> iv.setImageResource(R.drawable.tl_red));
                    else if (i == 1)
                        runOnUiThread(() -> iv.setImageResource(R.drawable.tl_green));
                    else if (i == 4)
                        runOnUiThread(() -> iv.setImageResource(R.drawable.tl_none));
                    else
                        runOnUiThread(() -> iv.setImageResource(R.drawable.tl_yellow));

                    //Set new Sound state
                    sound.setState(i);

                    break;
                }
            }
        }
        //Play sounds
        preElabTimes.add((Constants.endPreElab - Constants.startPreElab));
        elabTimes.add((Constants.endElab - Constants.startElab));


        runOnUiThread(() -> textView.setText(Constants.CHOSEN_MODEL + "\n" + "Predicted class: " + predicted + "\n" + "Pre-elaboration avg time: \n" + Utils.calculateAverage(preElabTimes) + "ms\n" +
                "Elaboration avg time: \n" + Utils.calculateAverage(elabTimes) + "ms\n "));
    }


    @Override
    public void startElab() {
        waitFor = true;
    }

    @Override
    public void endElab() {
        waitFor = false;
    }

    @Override
    public boolean isInElaboration() {
        return waitFor;
    }


}
