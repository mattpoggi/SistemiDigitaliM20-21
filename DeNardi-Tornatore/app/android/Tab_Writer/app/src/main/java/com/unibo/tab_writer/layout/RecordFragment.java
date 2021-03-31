package com.unibo.tab_writer.layout;

import android.Manifest;
import android.content.pm.ActivityInfo;
import android.content.pm.PackageManager;
import android.media.AudioFormat;
import android.media.MediaRecorder;
import android.os.Bundle;
import android.os.Handler;
import android.os.SystemClock;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Chronometer;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.app.ActivityCompat;
import androidx.fragment.app.Fragment;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;

import com.arthenica.mobileffmpeg.FFmpeg;
import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.unibo.tab_writer.R;
import com.unibo.tab_writer.database.DbAdapter;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;


public class RecordFragment extends Fragment implements View.OnClickListener{

    private NavController navController;

    private ImageView recordBtn;
    private TextView recordText;

    private boolean isRecording = false;

    private String recordPermission = Manifest.permission.RECORD_AUDIO;
    private int PERMISSION_CODE = 21;

    private MediaRecorder mediaRecorder;
    private String recordFile;

    private Chronometer timer;

    private String path;

    private DbAdapter dbHelper;
    private long cursor;

    private Handler handlerAscolto;
    private Runnable runnableAscolto;
    private Handler handlerPensando;
    private Runnable runnablePensando;


    public RecordFragment() {
        // Required empty public constructor
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        dbHelper = new DbAdapter(getContext());
        dbHelper.open();
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        getActivity().setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);

        return inflater.inflate(R.layout.fragment_record, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        navController = Navigation.findNavController(view);

        recordBtn = view.findViewById(R.id.record_btn);
        timer = view.findViewById(R.id.record_timer);
        recordText = view.findViewById(R.id.record_text);

        recordBtn.setOnClickListener(this);
    }

    @Override
    public void onClick(View v){
        switch (v.getId()){
            case R.id.record_btn:
                if(isRecording){
                    stopRecording();
                    recordBtn.setImageDrawable(getResources().getDrawable(R.drawable.rec_button_off));
                    isRecording = false;
                } else {
                    if(checkPermissions()){
                        startRecording();
                        recordBtn.setImageDrawable(getResources().getDrawable(R.drawable.rec_button_on));
                        isRecording = true;
                    }
                }
        }
    }

    private void startRecording(){
        timer.setBase(SystemClock.elapsedRealtime());
        timer.start();

        String recordPath = getActivity().getExternalFilesDir("/").getAbsolutePath();
        SimpleDateFormat formatter = new SimpleDateFormat("yyyy_MM_dd_HH_mm_ss", Locale.ITALIAN);
        Date now = new Date();

        recordFile = "Tab_" + formatter.format(now) + ".aac";

        handlerAscolto = new Handler();
        runnableAscolto = new Runnable() {
            int count = 0;

            @Override
            public void run() {
                count++;

                if (count == 1) {
                    recordText.setText("STO ASCOLTANDO.");
                } else if (count == 2) {
                    recordText.setText("STO ASCOLTANDO..");
                } else if (count == 3) {
                    recordText.setText("STO ASCOLTANDO...");
                }

                if (count == 3) {
                    count = 0;
                }
                handlerAscolto.postDelayed(this, 2 * 300);
            }
        };
        handlerAscolto.postDelayed(runnableAscolto, 1 * 300);


        mediaRecorder = new MediaRecorder();
        mediaRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
        mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
        mediaRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AAC);
        mediaRecorder.setAudioChannels(1);
        mediaRecorder.setAudioEncodingBitRate(128000);
        mediaRecorder.setAudioSamplingRate(44100);
        mediaRecorder.setOutputFile(recordPath + "/" + recordFile);

        path = recordPath + "/" + recordFile;

        try {
            mediaRecorder.prepare();
        } catch (IOException e){
            e.printStackTrace();
        }

        mediaRecorder.start();
    }

    private void stopRecording(){
        handlerAscolto.removeCallbacks(runnableAscolto);

        timer.stop();

        mediaRecorder.stop();
        mediaRecorder.release();
        mediaRecorder = null;


        handlerPensando = new Handler();
        runnablePensando = new Runnable() {
            int count = 0;

            @Override
            public void run() {
                count++;

                if (count == 1) {
                    recordText.setText("STO PENSANDO.");
                } else if (count == 2) {
                    recordText.setText("STO PENSANDO..");
                } else if (count == 3) {
                    recordText.setText("STO PENSANDO...");
                }

                if (count == 3) {
                    count = 0;
                }
                handlerPensando.postDelayed(this, 2 * 300);
            }
        };
        handlerPensando.postDelayed(runnablePensando, 1 * 300);


        recordBtn.setClickable(false);

        new Thread(new Runnable() {
            public void run() {
                process(path);
            }
        }).start();
    }

    private boolean checkPermissions(){
        if(ActivityCompat.checkSelfPermission(getContext(), recordPermission) == PackageManager.PERMISSION_GRANTED) {
            return true;
        } else {
            ActivityCompat.requestPermissions(getActivity(), new String[]{recordPermission}, PERMISSION_CODE);
            return false;
        }

    }

    private void process(String path){
        FFmpeg.execute("-i " + path + " -acodec pcm_u8 -ar 44100 " + path + ".wav");

        File fileAcc = new File(path);
        File fileWav = new File(path + ".wav");

        long date = fileWav.lastModified();


        Python py = Python.getInstance();
        final PyObject pyobj = py.getModule("main");

        PyObject obj = pyobj.callAttr("main", path + ".wav");
        Log.d("LOGGO-RecordFragment", obj.toString());


        fileAcc.delete();
        fileWav.delete();

        cursor = dbHelper.createTab(recordFile, String.valueOf(date), obj.toString());

        Bundle bundle = new Bundle();
        bundle.putString("tab_title", String.valueOf(recordFile));
        navController.navigate(R.id.action_fragment_record_to_fragment_tab_view, bundle);

        recordBtn.setClickable(true);
        handlerPensando.removeCallbacks(runnablePensando);
    }
}