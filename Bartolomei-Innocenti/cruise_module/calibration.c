#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <float.h>

float percentualeIncremento = 0.0f;
float minScaleFactor = 0.0f;
float maxScaleFactor = 0.0f;
float minShiftFactor = 0.0f;
float maxShiftFactor = 0.0f;

void calculateScaleRange(const float _percentualeIncremento, const float depthMin, const float depthCap, const float minOutputValue, const float maxOutputValue, const int isDisparityOutput){
    float myMin;
    float myMax;

    if (isDisparityOutput == 1){
        myMin = 1.0 / depthCap;
        myMax = 1.0 / depthMin;
    }else{
        myMin = depthMin;
        myMax = depthCap;
    }

    percentualeIncremento = _percentualeIncremento;
    minScaleFactor = 0.0f;
    maxScaleFactor = (100.0 / percentualeIncremento) * (myMax-myMin) / (maxOutputValue - minOutputValue); 
    minShiftFactor = myMin - (minOutputValue * maxScaleFactor);
    maxShiftFactor = myMax;
}

void setScaleRange(const float _percentualeIncremento, const float _minScaleFactor, const float _maxScaleFactor, const float _minShiftfactor, const float _maxShiftFactor){
    percentualeIncremento = _percentualeIncremento;
    minScaleFactor = _minScaleFactor;
    maxScaleFactor = _maxScaleFactor; 
    minShiftFactor = _minShiftfactor;
    maxShiftFactor = _maxShiftFactor;
}

int _checkScaleRange(const float scaleFactor, const float shiftFactor){
    int validScaleFactor = minScaleFactor <= scaleFactor && scaleFactor <= maxScaleFactor;
    int validShiftFactor = minShiftFactor <= shiftFactor && shiftFactor <= maxShiftFactor;

    return validScaleFactor && validShiftFactor;
}

void initSeed(){
    srand((unsigned) time(0));
}

float _assoluto(float a){
    if (a < 0.0){
        return -a;
    }
    return a;
}

typedef struct{
    float scaleFactor;
    float shiftfactor;
    int valid;
} cal_t;

void ransacMethod(const void* prediction, const void* projPoints,
 const int h, const int w, const int N,
 const int nIterations, const float normalizedThreshold, void* result){
    
    int *consensusSet = (int*) calloc(N, sizeof(int));
    int consensusSetSize = 0;
    int migliorConsensusSetSize = 0;

    //printf("TEST: predicton[0] %f, projPoints[0,1,2]: %f,%f,%f\n", ((float*)prediction)[0], ((float*)projPoints)[0], ((float*)projPoints)[1], ((float*)projPoints)[2]);

    for (int i = 0; i < nIterations; i++){   
        float possibileScaleFactor = 0.0f;
        float possibileShiftFactor = 0.0f;
        int possibileValid = 0;

        //Controllo intrinseco: Ho dei range in cui lo scale factor e lo shift factor si devono collocare
        //Esco comunque dopo un periodo
        for (int k = 0; k < nIterations && !possibileValid; k++){
            int i0 = rand() % N;
            int i1 = rand() % N;

            float zGt0 = ((float*)projPoints)[3*i0+2];
            int x0 = (int)(((float*)projPoints)[3*i0+0]);
            int y0 = (int)(((float*)projPoints)[3*i0+1]);
            float z0 = ((float*)prediction)[y0*w + x0];

            float zGt1 = ((float*)projPoints)[3*i1+2];
            int x1 = (int)(((float*)projPoints)[3*i1+0]);
            int y1 = (int)(((float*)projPoints)[3*i1+1]);
            float z1 = ((float*)prediction)[y1*w + x1];

            if (_assoluto(z1-z0) > (percentualeIncremento/100.0)){
                //Sono dei candidati a diventare migliori. Devo verificare rispetto al migliore attuale
                possibileScaleFactor = (zGt0 - zGt1) / (z0 - z1);
                possibileShiftFactor = zGt0 - (z0 * possibileScaleFactor);
                possibileValid = _checkScaleRange(possibileScaleFactor, possibileShiftFactor);
            }
        }

        //Controllo il check intrinseco: se non ho trovato uno scale factor nel range esco
        if(!possibileValid){
            //printf("%s - not valid PSC: %f, PSH: %f\n", "C Calibration RANSAC", possibileScaleFactor, possibileShiftFactor);
            ((cal_t*)result)->scaleFactor = possibileScaleFactor;
            ((cal_t*)result)->shiftfactor = possibileShiftFactor;
            ((cal_t*)result)->valid = 0;
            free(consensusSet);
            return;
        }

        //Resetto il consensus set.
        consensusSetSize = 0;

        float minError = FLT_MAX;
        float maxError = FLT_MIN;

        //Ricerca min/max per normalizzazione
        for (int k = 0; k < N; k++){
            float zGtP = ((float*)projPoints)[3*k+2];
            int xP = (int)(((float*)projPoints)[3*k+0]);
            int yP = (int)(((float*)projPoints)[3*k+1]);
            float zP = ((float*)prediction)[yP*w + xP];   

            float thisError = (float) pow((zP * possibileScaleFactor + possibileShiftFactor) - zGtP, 2.0);
            if (thisError < minError) minError = thisError;
            if (thisError > maxError) maxError = thisError;
        }

        //Popolamento del consensus set
        for(int k = 0; k < N; k++){
            float zGtP = ((float*)projPoints)[3*k+2];
            int xP = (int)(((float*)projPoints)[3*k+0]);
            int yP = (int)(((float*)projPoints)[3*k+1]);
            float zP = ((float*)prediction)[yP*w + xP]; 

            float thisError = (float) pow((zP * possibileScaleFactor + possibileShiftFactor) - zGtP, 2.0);
            float normalizedError = (thisError - minError) / (maxError - minError);

            if(normalizedError < normalizedThreshold){
                consensusSet[consensusSetSize++] = k;
            }
        }

        //Confronto con il miglior consensus set
        if(consensusSetSize > migliorConsensusSetSize){
            ((cal_t*)result)->scaleFactor = possibileScaleFactor;
            ((cal_t*)result)->shiftfactor = possibileShiftFactor;
            ((cal_t*)result)->valid = 1;
            migliorConsensusSetSize = consensusSetSize;
        }
    }

    free(consensusSet);
}