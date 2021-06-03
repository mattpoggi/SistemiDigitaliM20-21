package com.example.neomap;

import android.content.Intent;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.SystemClock;
import android.provider.MediaStore;
import android.util.Log;
import android.view.View;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.CompoundButton;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.Spinner;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.UiThread;
import androidx.appcompat.app.AppCompatActivity;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;

import lib_support.Classifier;

public class ClassifierActivity extends AppCompatActivity {

    private ImageView imageView;
    private Button btn;
    private Bitmap photo;
    private Switch aSwitch;
    private LinearLayout linearLayout;
    private ListView listView;
    protected TextView recognitionTextView,
            recognition1TextView,
            recognition2TextView,
            recognitionValueTextView,
            recognition1ValueTextView,
            recognition2ValueTextView;
    protected TextView inferenceTimeTextView;
    private ImageView plusImageView, minusImageView;
    private Spinner modelSpinner;
    private Spinner deviceSpinner;
    private TextView threadsTextView;
    private Classifier classifier;
    private long lastProcessingTimeMs;

    private Classifier.Model model = Classifier.Model.INT8_MOBILENET;
    private Classifier.Device device = Classifier.Device.CPU;
    private int numThreads = 4;
    private Handler handler;
    private TextView inferenceInfo;
    private String[] names;
    private String[] links;
    private LinearLayout detected_itemLayout;
    private LinearLayout detected_item1Layout;
    private LinearLayout detected_item2Layout;
    private LinearLayout inferenceLayout;


    public native void applyShadesJNI(Bitmap bitmap, Bitmap out);
    Bitmap shaded;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_classifier);
        getSupportActionBar().setDisplayHomeAsUpEnabled(true);
        initializeUIElements();

    }

    private void initializeUIElements() {

        names = this.getResources().getStringArray(R.array.names);
        links = this.getResources().getStringArray(R.array.links);

        imageView = findViewById(R.id.imageView);
        aSwitch = findViewById(R.id.settings);
        linearLayout = findViewById(R.id.settingsLayout);
        threadsTextView = findViewById(R.id.threads);
        plusImageView = findViewById(R.id.plus);
        minusImageView = findViewById(R.id.minus);
        modelSpinner = findViewById(R.id.model_spinner);
        deviceSpinner = findViewById(R.id.device_spinner);

        detected_itemLayout = findViewById(R.id.detected_itemLayout);
        detected_item1Layout = findViewById(R.id.detected_item1Layout);
        detected_item2Layout = findViewById(R.id.detected_item2Layout);
        inferenceLayout = findViewById(R.id.inferenceLayout);


        recognitionTextView = findViewById(R.id.detected_item);
        recognitionValueTextView = findViewById(R.id.detected_item_value);
        recognition1TextView = findViewById(R.id.detected_item1);
        recognition1ValueTextView = findViewById(R.id.detected_item1_value);
        recognition2TextView = findViewById(R.id.detected_item2);
        recognition2ValueTextView = findViewById(R.id.detected_item2_value);
        inferenceInfo = findViewById(R.id.inference);
        inferenceTimeTextView = findViewById(R.id.inference_info);

        btn = findViewById(R.id.scan);

        Bundle bundle = getIntent().getExtras();
        if (bundle != null) {
            String uriString = bundle.getString("imageUri");
            Uri uri = Uri.parse(uriString);
            Log.d("print", "ClassifierActivity, onCreate, path to file " + String.valueOf(uri));
            //imageView.setImageURI(uri);
            try {
                photo = MediaStore.Images.Media.getBitmap(this.getContentResolver(),uri);
                Log.d("print", "photo config: " + photo.getConfig() + ";dim height width: " + photo.getHeight() + " " + photo.getWidth());
            } catch (IOException e) {
                e.printStackTrace();
                Log.d("print", "ClassifierActivity, onCreate, error loading bitmap");
            }

            shaded=photo.copy(photo.getConfig(), true);
            applyShadesJNI(photo, shaded);
            Log.d("print", "shaded config: " + shaded.getConfig() + ";dim height width: " + shaded.getHeight() + " " + shaded.getWidth());
            Log.d("print", "shades of gray applied");
            imageView.setImageBitmap(photo);

        } else {
            Log.d("print", "ClassifierActivity, onCreate, error passing string from MainActivity");
            Toast.makeText(this, "Something went wrong :(", Toast.LENGTH_LONG);
            Intent intent = new Intent(ClassifierActivity.this, MainActivity.class);
            startActivity(intent);
        }

        aSwitch.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                if(isChecked){
                    linearLayout.setVisibility(View.VISIBLE);
                }else{
                    linearLayout.setVisibility(View.INVISIBLE);
                }
            }
        });

        plusImageView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                onClickSettings(v);
            }
        });

        minusImageView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                onClickSettings(v);
            }
        });

        modelSpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                onItemSelectedSettings(parent, view, position, id);
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {

            }
        });

        deviceSpinner.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                onItemSelectedSettings(parent, view, position, id);
            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {

            }
        });


        btn.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                Scan();
                //ScanTestAccuracy();
            }
        });
    }

    //only for testing
    private void ScanTestAccuracy() {
        if(linearLayout.getVisibility() == View.VISIBLE){
            model = Classifier.Model.valueOf(modelSpinner.getSelectedItem().toString().toUpperCase());
            device = Classifier.Device.valueOf(deviceSpinner.getSelectedItem().toString());
            String text = threadsTextView.getText().toString().trim();
            if (text != "N/A")
                numThreads = Integer.parseInt(text);

        } else{
            model = Classifier.Model.MOBILENET;
            device = Classifier.Device.XNNPACK;
            numThreads = 4;
        }
        Log.d("print", "model: " + model + ", device: " + device + ", numThreads: " + numThreads);

        recreateClassifier(model, device, numThreads);

        if (classifier!=null) {

            float accurate_count = 0;
            int count = 0;
            float accuracy = 0;

            float inferecnceTime;
            float meanInferenceTime;
            float totInference = 0;

            String filesFolder = "file://" + getFilesDir().getPath();
            Log.d("test", "files folder: " + filesFolder);
            String testFolderString = filesFolder + "/test";
            Uri uriTest = Uri.parse(testFolderString);
            File testFolder = new File(uriTest.getPath());

            if (testFolder.exists() && testFolder.isDirectory()) {
                for (File dirCategory : testFolder.listFiles()) {
                    for(File img : dirCategory.listFiles()) {

                        String categoryName = dirCategory.getName();
                        String imgPath = img.getAbsolutePath();
                        String imgName = img.getName();
                        Uri uriImg = Uri.parse("file://" + getFilesDir().getPath() + "/test/" + categoryName + "/" + imgName);
                        Bitmap imgBitmap = null;
                        try {
                            imgBitmap = MediaStore.Images.Media.getBitmap(this.getContentResolver(),uriImg);
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                        if (imgBitmap != null) {

                            long startTime = SystemClock.uptimeMillis();
                            List<Classifier.Recognition> results =
                                    classifier.recognizeImage(imgBitmap);
                            inferecnceTime = SystemClock.uptimeMillis() - startTime;
                            String predicted = results.get(0).getTitle();
                            if (predicted.equals(categoryName))
                                accurate_count += 1;

                            count++;
                            totInference += inferecnceTime;
                            Log.d("test", "Category: " + categoryName + "; img: " + imgName + "; predicted: " + predicted + "; accurate_count: " + accurate_count + "; count: " + count + "; inference: " + inferecnceTime);
                        }
                    }
                }
            }

            accuracy = accurate_count / count;
            meanInferenceTime = totInference / count;
            Log.d("test", "accuracy: " + accuracy + "; meanInferenceTime: " + meanInferenceTime);
        }
    }

    public void Scan(){

        if(linearLayout.getVisibility() == View.VISIBLE){
            model = Classifier.Model.valueOf(modelSpinner.getSelectedItem().toString().toUpperCase());
            device = Classifier.Device.valueOf(deviceSpinner.getSelectedItem().toString());
            String text = threadsTextView.getText().toString().trim();
            if (text != "N/A")
                numThreads = Integer.parseInt(text);

        } else{
            model = Classifier.Model.MOBILENET;
            device = Classifier.Device.XNNPACK;
            numThreads = 4;
        }
        Log.d("print", "model: " + model + ", device: " + device + ", numThreads: " + numThreads);

        recreateClassifier(model, device, numThreads);

        if (classifier!=null) {
            final long startTime = SystemClock.uptimeMillis();
            final List<Classifier.Recognition> results =
                    classifier.recognizeImage(shaded);
            lastProcessingTimeMs = SystemClock.uptimeMillis() - startTime;
            Log.d("print", "Detect: " + results);

            showResultsInBottomSheet(results);

            showInference(lastProcessingTimeMs + "ms");
        }
    }

    private void recreateClassifier(Classifier.Model model, Classifier.Device device, int numThreads) {
        if (classifier != null) {
            Log.d("print","Closing classifier.");
            classifier.close();
            classifier = null;
        }
        //comment first if when android version is higher than 9
        if (device == Classifier.Device.GPU
                && (model == Classifier.Model.INT8_MOBILENET || model == Classifier.Model.INT8_XCEPTION)) {
            Log.d("print", "Not creating classifier: GPU doesn't support quantized models.");
            Toast.makeText(this, R.string.tfe_ic_gpu_quant_error, Toast.LENGTH_LONG).show();
            return;
        }
        if (device == Classifier.Device.NNAPI &&  model == Classifier.Model.INT8_XCEPTION) {
            Log.d("print", "Not creating classifier: NNAPI doesn't support quantized Xception.");
            Toast.makeText(this, "Not creating classifier: NNAPI doesn't support quantized Xception.", Toast.LENGTH_LONG).show();
            return;
        }
        try {
            Log.d( "print","Creating classifier (model=" + model + ", device=" + device + ", numThreads=" + numThreads + ")");
            classifier = Classifier.create(this, model, device, numThreads);
        } catch (IOException | IllegalArgumentException e) {
            Log.e("print", e.getMessage());
            Toast.makeText(this, e.getMessage(), Toast.LENGTH_LONG).show();
        }

    }

    @UiThread
    protected void showResultsInBottomSheet(List<Classifier.Recognition> results) {
        if (results != null && results.size() >= 3) {
            Classifier.Recognition recognition = results.get(0);
            if (recognition != null) {
                if (recognition.getTitle() != null) {
                    recognitionTextView.setText(recognition.getTitle());
                    Log.d("print", "rec1" + recognition.getTitle());
                    setClickable(recognitionTextView);
                }
                if (recognition.getConfidence() != null)
                    recognitionValueTextView.setText(
                            String.format("%.2f", (100 * recognition.getConfidence())) + "%");
            }

            Classifier.Recognition recognition1 = results.get(1);
            if (recognition1 != null) {
                if (recognition1.getTitle() != null) {
                    recognition1TextView.setText(recognition1.getTitle());
                    Log.d("print", "rec2" + recognition1.getTitle());
                    setClickable(recognition1TextView);
                }
                if (recognition1.getConfidence() != null)
                    recognition1ValueTextView.setText(
                            String.format("%.2f", (100 * recognition1.getConfidence())) + "%");
            }

            Classifier.Recognition recognition2 = results.get(2);
            if (recognition2 != null) {
                if (recognition2.getTitle() != null) {
                    recognition2TextView.setText(recognition2.getTitle());
                    Log.d("print", "rec3" + recognition2.getTitle());
                    setClickable(recognition2TextView);
                }
                if (recognition2.getConfidence() != null)
                    recognition2ValueTextView.setText(
                            String.format("%.2f", (100 * recognition2.getConfidence())) + "%");
            }
        }
    }

    public void setClickable(TextView recognitionTextView){
       String name = recognitionTextView.getText().toString();
       int pos = Arrays.asList(names).indexOf(name);
       if (pos >= 0 && pos < names.length){
           String link = links[pos];
           Log.d("print", "label: " + name + ", link: " + link);
           recognitionTextView.setOnClickListener(null);
           recognitionTextView.setOnClickListener(new View.OnClickListener() {
               @Override
               public void onClick(View v) {
                   Uri uri = Uri.parse(link);
                   Intent intent = new Intent(Intent.ACTION_VIEW, uri);
                   startActivity(intent);
               }
           });

       }

    }

    protected void showInference(String inferenceTime) {
        inferenceInfo.setText("Inference time");
        inferenceTimeTextView.setText(inferenceTime);
    }

    protected Classifier.Model getModel() {
        return model;
    }

    private void setModel(Classifier.Model model) {
        if (this.model != model) {
            Log.d("print", "Updating model: " + model);
            this.model = model;
        }
    }

    protected Classifier.Device getDevice() {
        return device;
    }

    private void setDevice(Classifier.Device device) {
        if (this.device != device) {
            Log.d("print", "Updating  device: " + device);
            this.device = device;
            final boolean threadsEnabled = device == Classifier.Device.CPU || device == Classifier.Device.XNNPACK;
            plusImageView.setEnabled(threadsEnabled);
            minusImageView.setEnabled(threadsEnabled);
            threadsTextView.setText(threadsEnabled ? String.valueOf(numThreads) : "N/A");
        }
    }

    protected int getNumThreads() {
        return numThreads;
    }

    private void setNumThreads(int numThreads) {
        if (this.numThreads != numThreads) {
            Log.d("print", "Updating numThreads: " + numThreads);
            this.numThreads = numThreads;
        }
    }


    public void onClickSettings(View v) {
        if (v.getId() == R.id.plus) {
            String threads = threadsTextView.getText().toString().trim();
            int numThreads = Integer.parseInt(threads);
            if (numThreads >= 9) return;
            setNumThreads(++numThreads);
            threadsTextView.setText(String.valueOf(numThreads));
        } else if (v.getId() == R.id.minus) {
            String threads = threadsTextView.getText().toString().trim();
            int numThreads = Integer.parseInt(threads);
            if (numThreads == 1) {
                return;
            }
            setNumThreads(--numThreads);
            threadsTextView.setText(String.valueOf(numThreads));
        }
    }


    public void onItemSelectedSettings(AdapterView<?> parent, View view, int pos, long id) {
        if (parent == modelSpinner) {
            setModel(Classifier.Model.valueOf(parent.getItemAtPosition(pos).toString().toUpperCase()));
        } else if (parent == deviceSpinner) {
            setDevice(Classifier.Device.valueOf(parent.getItemAtPosition(pos).toString()));
        }
    }





}
