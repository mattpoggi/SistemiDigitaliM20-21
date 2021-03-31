package com.unibo.tab_writer.utils;

import java.util.Date;
import java.util.concurrent.TimeUnit;

public class TimeAgo {

    public String getTimeAgo(long duration){

        // Guitar_Tab_2021_02_14_06_29_49.aac
        // 1580484044000

        Date now = new Date();

        long seconds = TimeUnit.MILLISECONDS.toSeconds(now.getTime() - duration);
        long minutes = TimeUnit.MILLISECONDS.toMinutes(now.getTime() - duration);
        long hours = TimeUnit.MILLISECONDS.toHours(now.getTime() - duration);
        long days = TimeUnit.MILLISECONDS.toDays(now.getTime() - duration);

        if(seconds < 60){
            return "ora";
        } else if(minutes == 1){
            return "un minuto fa";
        } else if (minutes > 1 && minutes < 60){
            return minutes + " minuti fa";
        } else if (hours == 1){
            return "un'ora fa";
        } else if (hours > 1 && hours < 24){
            return hours + " ore fa";
        } else if (days == 1){
            return "un giorno fa";
        } else {
            return days + " giorni fa";
        }
    }
}
