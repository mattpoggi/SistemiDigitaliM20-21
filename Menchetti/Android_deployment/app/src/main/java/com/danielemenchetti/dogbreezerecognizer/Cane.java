package com.danielemenchetti.dogbreezerecognizer;



public class Cane {

    public enum TipoCane {
        INVALIDO,
        PURO,
        MISTO
    }

    private TipoCane tipo;
    private String razza1;
    private float percent1;
    private String razza2;
    private float percent2;

    public Cane(TipoCane tipo, String razza1, float percent1, String razza2, float percent2 ){
        this.tipo = tipo;
        this.razza1 = razza1;
        this.percent1 = percent1;
        this.razza2 = razza2;
        this.percent2 = percent2;
    }

    public float getPercent1() {
        return percent1;
    }

    public float getPercent2() {
        return percent2;
    }

    public TipoCane getTipo() {
        return tipo;
    }

    public String getRazza1() {
        return razza1;
    }

    public String getRazza2() {
        return razza2;
    }

    public void setPercent1(float percent1) {
        this.percent1 = percent1;
    }

    public void setPercent2(float percent2) {
        this.percent2 = percent2;
    }

    public void setRazza1(String razza1) {
        this.razza1 = razza1;
    }

    public void setRazza2(String razza2) {
        this.razza2 = razza2;
    }

    public void setTipo(TipoCane tipo) {
        this.tipo = tipo;
    }

    public String print_human_readable_dog(){
        if (this.tipo == TipoCane.INVALIDO){
            return ("In questa immagine non è stato riconosciuto un cane oppure non è stata riconosciuta una razza di cane nota.");
        } else {
            if (this.tipo == TipoCane.PURO){
                return ("In questa immagine c'è un cane di razza pura.\n\nRazza: " + this.razza1 + ".\nPrecisione: " + String.format("%.1f", this.percent1*100));
            }else{
                return ("In questa immagine c'è un cane di razza mista.\n\nRazza 1: " + this.razza1 +".\nPrecisione: " + String.format("%.1f", this.percent1*100)
                        + ".\n\nRazza 2: " + this.razza2 + ".\nPrecisione: " + String.format("%.1f", this.percent2*100));
            }
        }
    }
}
