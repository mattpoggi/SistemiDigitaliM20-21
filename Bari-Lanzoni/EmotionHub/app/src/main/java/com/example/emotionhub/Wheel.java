package com.example.emotionhub;

import java.util.HashMap;

public class Wheel {

    private HashMap<String, float[]> wheel = new HashMap<String, float[]>();
    private String[] emotions = new String[3];

    public Wheel(){

        wheel.put("Bellicose",new float[2]);
        wheel.get("Bellicose")[0]=-0.11f;
        wheel.get("Bellicose")[1]=0.96f;

        wheel.put("Alarmed",new float[2]);
        wheel.get("Alarmed")[0]=-0.08f;
        wheel.get("Alarmed")[1]=0.89f;

        wheel.put("Tense",new float[2]);
        wheel.get("Tense")[0]=-0.02f;
        wheel.get("Tense")[1]=0.85f;

        wheel.put("Hostile",new float[2]);
        wheel.get("Hostile")[0]=-0.27f;
        wheel.get("Hostile")[1]=0.89f;

        wheel.put("Envious",new float[2]);
        wheel.get("Envious")[0]=-0.27f;
        wheel.get("Envious")[1]=0.82f;

        wheel.put("Afraid",new float[2]);
        wheel.get("Afraid")[0]=-0.11f;
        wheel.get("Afraid")[1]=0.79f;

        wheel.put("Angry",new float[2]);
        wheel.get("Angry")[0]=-0.41f;
        wheel.get("Angry")[1]=0.79f;

        wheel.put("Hateful",new float[2]);
        wheel.get("Hateful")[0]=-0.58f;
        wheel.get("Hateful")[1]=0.85f;

        wheel.put("Defiant",new float[2]);
        wheel.get("Defiant")[0]=-0.61f;
        wheel.get("Defiant")[1]=0.72f;

        wheel.put("Contemptous",new float[2]);
        wheel.get("Contemptous")[0]=-0.57f;
        wheel.get("Contemptous")[1]=0.65f;

        wheel.put("Annoyed",new float[2]);
        wheel.get("Annoyed")[0]=-0.44f;
        wheel.get("Annoyed")[1]=0.66f;

        wheel.put("Jealous",new float[2]);
        wheel.get("Jealous")[0]=-0.08f;
        wheel.get("Jealous")[1]=0.56f;

        wheel.put("Indignant",new float[2]);
        wheel.get("Indignant")[0]=-0.24f;
        wheel.get("Indignant")[1]=0.46f;

        wheel.put("Impatient",new float[2]);
        wheel.get("Impatient")[0]=-0.04f;
        wheel.get("Impatient")[1]=0.29f;

        wheel.put("Enraged",new float[2]);
        wheel.get("Enraged")[0]=-0.17f;
        wheel.get("Enraged")[1]=0.72f;

        wheel.put("Distressed",new float[2]);
        wheel.get("Distressed")[0]=-0.7f;
        wheel.get("Distressed")[1]=0.56f;

        wheel.put("Disgusted",new float[2]);
        wheel.get("Disgusted")[0]=-0.67f;
        wheel.get("Disgusted")[1]=0.49f;

        wheel.put("Loathing",new float[2]);
        wheel.get("Loathing")[0]=-0.8f;
        wheel.get("Loathing")[1]=0.42f;

        wheel.put("Frustrated",new float[2]);
        wheel.get("Frustrated")[0]=-0.6f;
        wheel.get("Frustrated")[1]=0.39f;

        wheel.put("Discontented",new float[2]);
        wheel.get("Discontented")[0]=-0.67f;
        wheel.get("Discontented")[1]=0.33f;

        wheel.put("Bitter",new float[2]);
        wheel.get("Bitter")[0]=-0.8f;
        wheel.get("Bitter")[1]=0.26f;

        wheel.put("Insulted",new float[2]);
        wheel.get("Insulted")[0]=-0.74f;
        wheel.get("Insulted")[1]=0.2f;

        wheel.put("Suspicious",new float[2]);
        wheel.get("Suspicious")[0]=-0.32f;
        wheel.get("Suspicious")[1]=0.26f;

        wheel.put("Distrustful",new float[2]);
        wheel.get("Distrustful")[0]=-0.47f;
        wheel.get("Distrustful")[1]=0.1f;

        wheel.put("Startled",new float[2]);
        wheel.get("Startled")[0]=-0.92f;
        wheel.get("Startled")[1]=0.03f;

        wheel.put("Disappointed",new float[2]);
        wheel.get("Disappointed")[0]=-0.8f;
        wheel.get("Disappointed")[1]=-0.04f;

        wheel.put("Miserable",new float[2]);
        wheel.get("Miserable")[0]=-0.93f;
        wheel.get("Miserable")[1]=-0.13f;

        wheel.put("Dissatisfied",new float[2]);
        wheel.get("Dissatisfied")[0]=-0.6f;
        wheel.get("Dissatisfied")[1]=-0.17f;

        wheel.put("Taken aback",new float[2]);
        wheel.get("Taken aback")[0]=-0.41f;
        wheel.get("Taken aback")[1]=-0.23f;

        wheel.put("Apathetic",new float[2]);
        wheel.get("Apathetic")[0]=-0.2f;
        wheel.get("Apathetic")[1]=-0.13f;

        wheel.put("Uncomfortable",new float[2]);
        wheel.get("Uncomfortable")[0]=-0.67f;
        wheel.get("Uncomfortable")[1]=-0.37f;

        wheel.put("Sad",new float[2]);
        wheel.get("Sad")[0]=-0.82f;
        wheel.get("Sad")[1]=-0.4f;

        wheel.put("Despondent",new float[2]);
        wheel.get("Despondent")[0]=-0.57f;
        wheel.get("Despondent")[1]=-0.43f;

        wheel.put("Depressed",new float[2]);
        wheel.get("Depressed")[0]=-0.81f;
        wheel.get("Depressed")[1]=-0.46f;

        wheel.put("Gloomy",new float[2]);
        wheel.get("Gloomy")[0]=-0.87f;
        wheel.get("Gloomy")[1]=-0.46f;

        wheel.put("Desperate",new float[2]);
        wheel.get("Desperate")[0]=-0.8f;
        wheel.get("Desperate")[1]=-0.5f;

        wheel.put("Worried",new float[2]);
        wheel.get("Worried")[0]=-0.08f;
        wheel.get("Worried")[1]=-0.33f;

        wheel.put("Feel guilt",new float[2]);
        wheel.get("Feel guilt")[0]=-0.4f;
        wheel.get("Feel guilt")[1]=-0.43f;

        wheel.put("Ashamed",new float[2]);
        wheel.get("Ashamed")[0]=-0.44f;
        wheel.get("Ashamed")[1]=-0.5f;

        wheel.put("Languid",new float[2]);
        wheel.get("Languid")[0]=-0.23f;
        wheel.get("Languid")[1]=-0.5f;

        wheel.put("Embarassed",new float[2]);
        wheel.get("Embarassed")[0]=-0.32f;
        wheel.get("Embarassed")[1]=-0.6f;

        wheel.put("Wavering",new float[2]);
        wheel.get("Wavering")[0]=-0.57f;
        wheel.get("Wavering")[1]=-0.69f;

        wheel.put("Anxious",new float[2]);
        wheel.get("Anxious")[0]=-0.73f;
        wheel.get("Anxious")[1]=-0.8f;

        wheel.put("Dejected",new float[2]);
        wheel.get("Dejected")[0]=-0.5f;
        wheel.get("Dejected")[1]=-0.86f;

        wheel.put("Hesitant",new float[2]);
        wheel.get("Hesitant")[0]=-0.31f;
        wheel.get("Hesitant")[1]=-0.73f;

        wheel.put("Melancholic",new float[2]);
        wheel.get("Melancholic")[0]=-0.04f;
        wheel.get("Melancholic")[1]=-0.66f;

        wheel.put("Bored",new float[2]);
        wheel.get("Bored")[0]=-0.34f;
        wheel.get("Bored")[1]=-0.79f;

        wheel.put("Droopy",new float[2]);
        wheel.get("Droopy")[0]=-0.32f;
        wheel.get("Droopy")[1]=-0.92f;

        wheel.put("Doubtful",new float[2]);
        wheel.get("Doubtful")[0]=-0.28f;
        wheel.get("Doubtful")[1]=-0.96f;

        wheel.put("Tired",new float[2]);
        wheel.get("Tired")[0]=-0.02f;
        wheel.get("Tired")[1]=-0.99f;

        wheel.put("Sleepy",new float[2]);
        wheel.get("Sleepy")[0]=0.02f;
        wheel.get("Sleepy")[1]=-0.99f;

        wheel.put("Reverent",new float[2]);
        wheel.get("Reverent")[0]=0.22f;
        wheel.get("Reverent")[1]=-0.96f;

        wheel.put("Compassionate",new float[2]);
        wheel.get("Compassionate")[0]=0.38f;
        wheel.get("Compassionate")[1]=-0.92f;

        wheel.put("Conscientious",new float[2]);
        wheel.get("Conscientious")[0]=0.32f;
        wheel.get("Conscientious")[1]=-0.79f;

        wheel.put("Peaceful",new float[2]);
        wheel.get("Peaceful")[0]=0.55f;
        wheel.get("Peaceful")[1]=-0.79f;

        wheel.put("Polite",new float[2]);
        wheel.get("Polite")[0]=0.37f;
        wheel.get("Polite")[1]=-0.66f;

        wheel.put("Serious",new float[2]);
        wheel.get("Serious")[0]=0.22f;
        wheel.get("Serious")[1]=-0.66f;

        wheel.put("Pensive",new float[2]);
        wheel.get("Pensive")[0]=0.03f;
        wheel.get("Pensive")[1]=-0.6f;

        wheel.put("Contemplative",new float[2]);
        wheel.get("Contemplative")[0]=0.58f;
        wheel.get("Contemplative")[1]=-0.6f;

        wheel.put("Attentive",new float[2]);
        wheel.get("Attentive")[0]=0.48f;
        wheel.get("Attentive")[1]=-0.46f;

        wheel.put("Longing",new float[2]);
        wheel.get("Longing")[0]=0.22f;
        wheel.get("Longing")[1]=-0.43f;

        wheel.put("Impressed",new float[2]);
        wheel.get("Impressed")[0]=0.39f;
        wheel.get("Impressed")[1]=-0.07f;

        wheel.put("Confident",new float[2]);
        wheel.get("Confident")[0]=0.51f;
        wheel.get("Confident")[1]=-0.2f;

        wheel.put("Hopeful",new float[2]);
        wheel.get("Hopeful")[0]=0.62f;
        wheel.get("Hopeful")[1]=-0.3f;

        wheel.put("Calm",new float[2]);
        wheel.get("Calm")[0]=0.71f;
        wheel.get("Calm")[1]=-0.66f;

        wheel.put("Friendly",new float[2]);
        wheel.get("Friendly")[0]=0.76f;
        wheel.get("Friendly")[1]=-0.59f;

        wheel.put("Satisfied",new float[2]);
        wheel.get("Satisfied")[0]=0.77f;
        wheel.get("Satisfied")[1]=-0.63f;

        wheel.put("At ease",new float[2]);
        wheel.get("At ease")[0]=0.78f;
        wheel.get("At ease")[1]=-0.59f;

        wheel.put("Content",new float[2]);
        wheel.get("Content")[0]=0.82f;
        wheel.get("Content")[1]=-0.56f;

        wheel.put("Solemn",new float[2]);
        wheel.get("Solemn")[0]=0.82f;
        wheel.get("Solemn")[1]=-0.46f;

        wheel.put("Amorous",new float[2]);
        wheel.get("Amorous")[0]=0.85f;
        wheel.get("Amorous")[1]=-0.13f;

        wheel.put("Serene",new float[2]);
        wheel.get("Serene")[0]=0.84f;
        wheel.get("Serene")[1]=-0.5f;

        wheel.put("Pleased",new float[2]);
        wheel.get("Pleased")[0]=0.88f;
        wheel.get("Pleased")[1]=-0.1f;

        wheel.put("Feel well",new float[2]);
        wheel.get("Feel well")[0]=0.91f;
        wheel.get("Feel well")[1]=-0.07f;

        wheel.put("Glad",new float[2]);
        wheel.get("Glad")[0]=0.95f;
        wheel.get("Glad")[1]=-0.17f;

        wheel.put("Expectant",new float[2]);
        wheel.get("Expectant")[0]=0.32f;
        wheel.get("Expectant")[1]=0.06f;

        wheel.put("Passionate",new float[2]);
        wheel.get("Passionate")[0]=0.32f;
        wheel.get("Passionate")[1]=0.13f;

        wheel.put("Light hearted",new float[2]);
        wheel.get("Light hearted")[0]=0.42f;
        wheel.get("Light hearted")[1]=0.29f;

        wheel.put("Amused",new float[2]);
        wheel.get("Amused")[0]=0.55f;
        wheel.get("Amused")[1]=0.2f;

        wheel.put("Enthusiastic",new float[2]);
        wheel.get("Enthusiastic")[0]=0.5f;
        wheel.get("Enthusiastic")[1]=0.33f;

        wheel.put("Interested",new float[2]);
        wheel.get("Interested")[0]=0.65f;
        wheel.get("Interested")[1]=0.03f;

        wheel.put("Determined",new float[2]);
        wheel.get("Determined")[0]=0.74f;
        wheel.get("Determined")[1]=0.26f;

        wheel.put("Delighted",new float[2]);
        wheel.get("Delighted")[0]=0.88f;
        wheel.get("Delighted")[1]=0.36f;

        wheel.put("Happy",new float[2]);
        wheel.get("Happy")[0]=0.9f;
        wheel.get("Happy")[1]=0.17f;

        wheel.put("Joyous",new float[2]);
        wheel.get("Joyous")[0]=0.95f;
        wheel.get("Joyous")[1]=0.13f;

        wheel.put("Convinced",new float[2]);
        wheel.get("Convinced")[0]=0.42f;
        wheel.get("Convinced")[1]=0.42f;

        wheel.put("Corageous",new float[2]);
        wheel.get("Corageous")[0]=0.81f;
        wheel.get("Corageous")[1]=0.59f;

        wheel.put("Self-confident",new float[2]);
        wheel.get("Self-confident")[0]=0.82f;
        wheel.get("Self-confident")[1]=0.66f;

        wheel.put("Feeling superior",new float[2]);
        wheel.get("Feeling superior")[0]=0.32f;
        wheel.get("Feeling superior")[1]=0.56f;

        wheel.put("Conceited",new float[2]);
        wheel.get("Conceited")[0]=0.19f;
        wheel.get("Conceited")[1]=0.65f;

        wheel.put("Ambitious",new float[2]);
        wheel.get("Ambitious")[0]=0.42f;
        wheel.get("Ambitious")[1]=0.65f;

        wheel.put("Lusting",new float[2]);
        wheel.get("Lusting")[0]=0.22f;
        wheel.get("Lusting")[1]=0.85f;

        wheel.put("Astonished",new float[2]);
        wheel.get("Astonished")[0]=0.42f;
        wheel.get("Astonished")[1]=0.89f;

        wheel.put("Aroused",new float[2]);
        wheel.get("Aroused")[0]=0.38f;
        wheel.get("Aroused")[1]=0.92f;

        wheel.put("Adventourous",new float[2]);
        wheel.get("Adventourous")[0]=0.49f;
        wheel.get("Adventourous")[1]=0.92f;

        wheel.put("Triumphant",new float[2]);
        wheel.get("Triumphant")[0]=0.65f;
        wheel.get("Triumphant")[1]=0.79f;

        wheel.put("Excited",new float[2]);
        wheel.get("Excited")[0]=0.7f;
        wheel.get("Excited")[1]=0.73f;

    }

    public HashMap<String,Float> getNear (float x, float y){
        String[] result = new String[3];
        for(int i=0;i<3;i++){
            result[i]="";
        }
        float[] min = new float[3];
        for(int i=0;i<3;i++){
            min[i]=4;
        }
        float dst = 0;
        float sum = 0;
        float tot = 0;
        HashMap<String,Float> r = new HashMap<>();

        for(String emotion : wheel.keySet()){
            dst=(float) Math.sqrt((wheel.get(emotion)[0]-x)*(wheel.get(emotion)[0]-x)+(wheel.get(emotion)[1]-y)*(wheel.get(emotion)[1]-y));
            if(dst<min[0]){
                min[2]=min[1];
                min[1]=min[0];
                min[0]=dst;
                result[2]=result[1];
                result[1]=result[0];
                result[0]=emotion;
            }else if(dst<min[1]){
                min[2]=min[1];
                min[1]=dst;
                result[2]=result[1];
                result[1]=emotion;
            }else if(dst<min[2]){
                min[2]=dst;
                result[2]=emotion;
            }
        }

        for(float f : min){
            sum+=f;
        }

        for(float c : min){
            tot+=sum-c;
        }

        for(int i=0;i<3;i++){
            r.put(result[i],( ((sum-(min[i])) / tot ) * 100 ));
        }

        this.emotions=result;

        return r;
    }

    public String[] getEmotions(){
        return this.emotions;
    }




}
