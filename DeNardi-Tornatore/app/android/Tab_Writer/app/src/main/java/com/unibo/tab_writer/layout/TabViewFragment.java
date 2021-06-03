package com.unibo.tab_writer.layout;

import android.content.pm.ActivityInfo;
import android.database.Cursor;
import android.graphics.Color;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.github.mikephil.charting.charts.BubbleChart;
import com.github.mikephil.charting.components.XAxis;
import com.github.mikephil.charting.components.YAxis;
import com.github.mikephil.charting.data.BubbleData;
import com.github.mikephil.charting.data.BubbleDataSet;
import com.github.mikephil.charting.data.BubbleEntry;
import com.github.mikephil.charting.formatter.DefaultValueFormatter;
import com.github.mikephil.charting.formatter.IndexAxisValueFormatter;
import com.unibo.tab_writer.R;
import com.unibo.tab_writer.database.DbAdapter;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;

public class TabViewFragment extends Fragment {

    private BubbleChart bubbleChart;
    private String tab_title;
    private String tab_tab;

    private DbAdapter dbHelper;
    private Cursor cursor;

    private JSONArray jsonarray;
    private JSONObject jsonobject;

    public TabViewFragment() {
        // Required empty public constructor
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        tab_title = getArguments().getString("tab_title");

        dbHelper = new DbAdapter(getContext());
        dbHelper.open();
        cursor = dbHelper.fetchTabsByFilter(tab_title);

        if (cursor.moveToFirst()){
            tab_tab = cursor.getString(cursor.getColumnIndex(DbAdapter.KEY_TAB));
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        getActivity().setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE);

        return inflater.inflate(R.layout.fragment_tab_view, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        ArrayList<BubbleEntry> tab = new ArrayList<>();

        Log.d("LOGGO-Tab-ViewFragment", tab_tab);

        try {
            jsonarray = new JSONArray(tab_tab);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        BubbleChart bubbleChart = view.findViewById(R.id.bubbleChart);
        bubbleChart.setTouchEnabled(true);
        bubbleChart.setDrawGridBackground(false);
        bubbleChart.setPinchZoom(false);
        bubbleChart.setDragEnabled(true);
        bubbleChart.getXAxis().setEnabled(false);
        bubbleChart.getAxisLeft().setEnabled(true);
        bubbleChart.getAxisRight().setEnabled(false);
        bubbleChart.getDescription().setEnabled(false);
        bubbleChart.getLegend().setEnabled(false);

        for(int i=0; i < jsonarray.length(); i++) {
            try {
                jsonobject = jsonarray.getJSONObject(i);
                JSONArray value = jsonobject.getJSONArray("value");
                for (int j = 0; j < value.length(); j++) {
                    if (value.getInt(j) == 0) {
                        continue;
                    } else if (value.getInt(j) == 1) {
                        tab.add(new BubbleEntry(Float.parseFloat(jsonobject.getString("tab_x")), 5 - j, 0));
                    } else {
                        tab.add(new BubbleEntry(Float.parseFloat(jsonobject.getString("tab_x")), 5 - j, Float.parseFloat(value.getString(j))-1));
                    }
                }
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }

        XAxis xAxis = bubbleChart.getXAxis();
        xAxis.setAxisMinimum(-0.5f);
        if(jsonarray.length() < 10){
            xAxis.setAxisMaximum(9f);
        } else {
            xAxis.setAxisMaximum(jsonarray.length());
        }

        YAxis yAxis = bubbleChart.getAxisLeft();
        yAxis.setValueFormatter(new IndexAxisValueFormatter(new String[]{"E","A","D","G","B","e"}));
        yAxis.setTextColor(Color.WHITE);
        yAxis.setTextSize(15f);
        yAxis.setDrawGridLines(true);
        yAxis.setGranularity(1f);
        yAxis.setGranularityEnabled(true);
        yAxis.setDrawZeroLine(false);
        yAxis.setAxisMinimum(0f);
        yAxis.setAxisMaximum(5f);

        BubbleDataSet bubbleDataSet = new BubbleDataSet(tab, "tab");
        bubbleDataSet.setColor(Color.WHITE, 0);
        bubbleDataSet.setValueTextColor(Color.WHITE);
        bubbleDataSet.setValueTextSize(16f);
        bubbleDataSet.setValueFormatter(new DefaultValueFormatter(0));

        BubbleData bubbleData = new BubbleData(bubbleDataSet);

        bubbleChart.setData(bubbleData);
        bubbleChart.setVisibleXRangeMaximum(9.5f);

        bubbleChart.animateXY(1000,1000);
    }

}