#include "opencv-utils.h"
#include <android/log.h>

void process(Mat src1,float *ml,float *ma,float *mb,int p,int m) {

    *ma=0;
    *mb=0;
    *ml=0;

    for(int i=0;i<src1.rows;i++){
        for(int j=0;j<src1.cols;j++){
            //img_power = np.power(img, power)
            Vec3b v1=src1.at<cv::Vec3b>(i,j);
            float lc=pow(v1.val[0],p);
            float ac=pow(v1.val[1],p);
            float bc=pow(v1.val[2],p);
            *ma=*ma+ac;
            *mb=*mb+bc;
            *ml=*ml+lc;
        }
    }
    //rgb_vec = np.power(np.mean(img_power, (0,1)), 1/power)
    *ma=pow((float)*ma/(src1.cols*src1.rows),(float)1/p);
    *mb=pow((float)*mb/(src1.cols*src1.rows),(float)1/p);
    *ml=pow((float)*ml/(src1.cols*src1.rows),(float)1/p);

    //(*ma)=128+(0.5*255 *(*ma));
    //(*mb)=128+(0.5*255 *(*mb));
    //(*ml)=128+(0.5*255 *(*ml));

    float r=0;

    if(m==0) {
        r=(*ma+*mb+*ml)/3;

        *ma=r/(*ma);
        *mb=r/(*mb);
        *ml=r/(*ml);
    }

    if(m==1) {
        r=(*ma+*mb+*ml)/3;
        r=max(*ma,*mb);
        r=max(r,*ml);

        *ma=r/(*ma);
        *mb=r/(*mb);
        *ml=r/(*ml);
    }

    if(m==2) {
        //rgb_norm = np.sqrt(np.sum(np.power(rgb_vec, 2.0)))
        r=sqrt((*ma)*(*ma)+(*mb)*(*mb)+(*ml)*(*ml));
        //rgb_vec = rgb_vec/rgb_norm
        *ma=(float)(*ma)/(float)r;
        *mb=(float)(*mb)/(float)r;
        *ml=(float)(*ml)/(float)r;

        /*cerr <<  *ml << endl;
        cerr <<  *ma << endl;
        cerr <<  *mb << endl;*/

        /*r=max(*ma,*mb);
        r=max(r,*ml);

        *ma=(float)r/(float)(*ma);
        *mb=(float)r/(float)(*mb);
        *ml=(float)r/(float)(*ml);*/

        //rgb_vec = 1/(rgb_vec*np.sqrt(3))
        *ma = (float)1 / ((float)(*ma) * sqrt(3));
        *mb = (float)1 / ((float)(*mb) * sqrt(3));
        *ml = (float)1 / ((float)(*ml) * sqrt(3));

    }
}
//apply shades of grey to rgba image. Return rgb image
Mat run2(Mat src,int p,int m) {

    Mat src1;
    src.copyTo(src1);
    Mat dst;
    src1.copyTo(dst);

    cv::Mat_<cv::Vec3b>::const_iterator it= src1.begin<cv::Vec3b>();
    cv::Mat_<cv::Vec3b>::const_iterator itend= src1.end<cv::Vec3b>();
    cv::Mat_<cv::Vec3b>::iterator itout= dst.begin<cv::Vec3b>();

    float ma=0,mb=0,ml=0;
    process(src1,&ml,&ma,&mb,p,m);
    //cerr << ":" << ml << ":" << ma <<":" << mb << endl;
    for ( ; it!= itend; ++it, ++itout) {

        cv::Vec3b v1=*it;

        float l=v1.val[0];
        float a=v1.val[1];
        float b=v1.val[2];

        if(m==1) {
            a=a*(ma);
            b= b*(mb);
            l= l*(ml);
        } else {
            //if(a<(float)85*255/100 && a>10*255/100)
            a=a*(ma);
            //if(b<(float)85*255/100 && a>10*255/100)
            b= b*(mb);
            //if(l<(float)85*255/100 && a>10*255/100)
            l= l*(ml);
        }

        if(a>255) a=255;
        if(b>255) b=255;
        if(l>255) l=255;

        v1.val[0]=l;
        v1.val[1]=a;
        v1.val[2]=b;
        *itout=v1;
    }
    return dst;
}

Mat applyShades(Mat src){
    __android_log_print(ANDROID_LOG_DEBUG, "print", "apply shades of gray");
    return run2(src, 6, 2);
}
