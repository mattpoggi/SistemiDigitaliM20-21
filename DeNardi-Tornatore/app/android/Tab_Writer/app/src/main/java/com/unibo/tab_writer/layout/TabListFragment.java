package com.unibo.tab_writer.layout;

import android.content.pm.ActivityInfo;
import android.database.Cursor;
import android.os.Bundle;
import android.util.Log;
import android.view.ContextMenu;
import android.view.LayoutInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.unibo.tab_writer.R;
import com.unibo.tab_writer.database.DbAdapter;

import java.util.ArrayList;


public class TabListFragment extends Fragment implements TabListAdapter.onItemListClick {

    private NavController navController;

    private RecyclerView tabList;
    private TabListAdapter tabListAdapter;

    private DbAdapter dbHelper;
    private Cursor cursor;

    private ArrayList<String> tab_title = new ArrayList<String>();
    private ArrayList<String> tab_date = new ArrayList<String>();

    private int pos;


    public TabListFragment() {
        // Required empty public constructor
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        dbHelper = new DbAdapter(getContext());
        dbHelper.open();
        cursor = dbHelper.fetchAllTabs();

        while(cursor.moveToNext()) {
            String title = cursor.getString(cursor.getColumnIndex(DbAdapter.KEY_TITLE));
            String date = cursor.getString(cursor.getColumnIndex(DbAdapter.KEY_DATE));
            tab_title.add(title);
            tab_date.add(date);
        }
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        dbHelper.close();
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        getActivity().setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED);

        return inflater.inflate(R.layout.fragment_tab_list, container, false);
    }

    @Override
    public void onViewCreated(@NonNull View view, @Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);

        navController = Navigation.findNavController(view);

        tabList = view.findViewById(R.id.tab_list_view);
        registerForContextMenu(tabList);

        // Initialize ArrayAdapter
        tabListAdapter = new TabListAdapter(tab_title, tab_date, this);
        cursor.close();

        // Set ArrayAdapter to tabListAdapter
        tabList.setHasFixedSize(true);
        tabList.setLayoutManager(new LinearLayoutManager(getContext()));
        tabList.setAdapter(tabListAdapter);
    }

    @Override
    public void onClickListener(int position) {
        Bundle bundle = new Bundle();
        bundle.putString("tab_title", String.valueOf(tab_title.get(position)));
        navController.navigate(R.id.action_fragment_tab_list_to_fragment_tab_view, bundle);
    }

    @Override
    public void onLongClickListener(int position) {
        pos = position;
    }

    @Override
    public void onCreateContextMenu(@NonNull ContextMenu menu, @NonNull View v, @Nullable ContextMenu.ContextMenuInfo menuInfo) {
        super.onCreateContextMenu(menu, v, menuInfo);

        getActivity().getMenuInflater().inflate(R.menu.list_menu, menu);
    }

    @Override
    public boolean onContextItemSelected(MenuItem item){
        switch (item.getItemId()){
            case R.id.menu_delete:
                dbHelper.deleteTab(tab_title.get(pos));
                tabListAdapter.removeAt(pos);
//                Toast.makeText(getActivity(), tab_title.get(pos) + " eliminato", Toast.LENGTH_SHORT).show();
                return true;
            default:
                return super.onContextItemSelected(item);
        }
    }
}