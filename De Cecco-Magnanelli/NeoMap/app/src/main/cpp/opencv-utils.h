#pragma once
#include <opencv2/core.hpp>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>
#include <android/log.h>

using namespace cv;
void process(Mat src1,float *ml,float *ma,float *mb,int p,int m);
Mat run2(Mat src,int p,int m);
Mat applyShades(Mat src);
