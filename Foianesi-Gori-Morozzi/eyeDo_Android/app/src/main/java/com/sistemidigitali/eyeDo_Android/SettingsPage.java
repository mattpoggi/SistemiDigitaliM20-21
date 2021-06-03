package com.sistemidigitali.eyeDo_Android;

import android.os.Bundle;
import android.support.annotation.Nullable;
import android.support.v7.app.AppCompatActivity;
import android.widget.CompoundButton;
import android.widget.RadioButton;

public class SettingsPage extends AppCompatActivity {

    private RadioButton nof32;
    private RadioButton ptnof32;
    private RadioButton oi8;
    private RadioButton of32;

    private CompoundButton.OnCheckedChangeListener checkedChangeListener = (buttonView, isChecked) -> {
        if (isChecked) {
            if (buttonView.getId() == R.id.nof32) {
                Constants.CHOSEN_MODEL = Constants.nof32;
            } else if (buttonView.getId() == R.id.ptnof32) {
                Constants.CHOSEN_MODEL = Constants.normOptF32;
            } else if (buttonView.getId() == R.id.oi8) {
                Constants.CHOSEN_MODEL = Constants.oi8;
            } else if (buttonView.getId() == R.id.of32) {
                Constants.CHOSEN_MODEL = Constants.of32;
            }
        }
    };

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.settingspage);

        //Model choice
        nof32 = findViewById(R.id.nof32);
        ptnof32 = findViewById(R.id.ptnof32);
        oi8 = findViewById(R.id.oi8);
        of32 = findViewById(R.id.of32);

        if (Constants.CHOSEN_MODEL.equals(Constants.nof32))
            nof32.setChecked(true);
        else if (Constants.CHOSEN_MODEL.equals(Constants.normOptF32))
            ptnof32.setChecked(true);
        else if (Constants.CHOSEN_MODEL.equals(Constants.oi8))
            oi8.setChecked(true);
        else if (Constants.CHOSEN_MODEL.equals(Constants.of32))
            of32.setChecked(true);

        nof32.setOnCheckedChangeListener(checkedChangeListener);
        ptnof32.setOnCheckedChangeListener(checkedChangeListener);
        oi8.setOnCheckedChangeListener(checkedChangeListener);
        of32.setOnCheckedChangeListener(checkedChangeListener);

    }

}
