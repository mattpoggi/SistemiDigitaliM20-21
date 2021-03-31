package com.unibo.tab_writer.database;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.SQLException;
import android.database.sqlite.SQLiteDatabase;

public class DbAdapter {
    @SuppressWarnings("unused")
    private static final String LOG_TAG = DbAdapter.class.getSimpleName();
    private Context context;
    private SQLiteDatabase database;
    private DatabaseHelper dbHelper;

    // Database fields
    private static final String DATABASE_TABLE = "tab_list";
    public static final String KEY_ID = "id";
    public static final String KEY_TITLE = "title";
    public static final String KEY_DATE = "date";
    public static final String KEY_TAB = "tab";

    public DbAdapter(Context context) {
        this.context = context;
    }

    public DbAdapter open() throws SQLException {
        dbHelper = new DatabaseHelper(context);
        database = dbHelper.getWritableDatabase();
        return this;
    }

    public void close() {
        dbHelper.close();
    }

    private ContentValues createContentValues(String title, String date, String tab) {
        ContentValues values = new ContentValues();
        values.put(KEY_TITLE, title);
        values.put(KEY_DATE, date);
        values.put(KEY_TAB, tab);
        return values;
    }

    //create a tab
    public long createTab(String title, String date, String tab) {
        ContentValues initialValues = createContentValues(title, date, tab);
        return database.insertOrThrow(DATABASE_TABLE, null, initialValues);
    }

    //update a tab
    public boolean updateTab(long id, String title, String date, String tab) {
        ContentValues updateValues = createContentValues(title, date, tab);
        return database.update(DATABASE_TABLE, updateValues, KEY_TITLE + "=" + title, null) > 0;
    }

    //delete a tab
    public boolean deleteTab(String title) {
        return database.delete(DATABASE_TABLE, KEY_TITLE + " like '%" + title + "%'", null) > 0;
    }

    //fetch all tabs
    public Cursor fetchAllTabs() {
        return database.query(DATABASE_TABLE, new String[]{KEY_ID, KEY_TITLE, KEY_DATE, KEY_TAB}, null, null, null, null, null);
    }

    //fetch tabs filter by a string
    public Cursor fetchTabsByFilter(String filter) {
        Cursor mCursor = database.query(true, DATABASE_TABLE, new String[]{
                        KEY_ID, KEY_TITLE, KEY_DATE, KEY_TAB},
                KEY_TITLE + " like '%" + filter + "%'", null, null, null, null, null);
        return mCursor;
    }
}