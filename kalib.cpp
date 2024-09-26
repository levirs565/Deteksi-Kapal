#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <string>
#include <libgen.h>
#include <signal.h>
#include <math.h>
#include <vector>
#include <iostream>
#include "opencv2/opencv.hpp"
#include "opencv2/objdetect.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"

 
using namespace cv;
using namespace std;

//cek waktu
#include <time.h>
clock_t t;

//input
Mat ori; //gambar
VideoCapture cap(0); //video

//batas
int panjang = 320,
lebar = 240,
offsetM = 100, 			//offset mid
offsetT = 50,
mid = panjang / 2,
midL = mid - offsetM,
midR = mid + offsetM,
atas = offsetT,
bawah = lebar - offsetT;

//variable
String
markk = "relatif lurus ",
gerak = "maju",
arah = "lurus";

int x=1;

//erode
int erosion_size = 4;
Mat element_ero = getStructuringElement(MORPH_CROSS, Size(2 * erosion_size + 1, 2 * erosion_size + 1), Point(erosion_size, erosion_size));

//dilate
int dilate_size = 6;
Mat element_dila = getStructuringElement(MORPH_CROSS,Size(2 * dilate_size + 1, 2 * dilate_size + 1), Point(dilate_size, dilate_size));

//variabel mengahluskan contour
//ke semakin kecil ,deteksi semakin halus
double epsilon;
//double ke = 0.0171; //konstanta epsilon
double ke = 0.0280; //konstanta epsilon

// variabel tambahan
int
kon = 0,
MaxContour=12000,
counter=0;

//robot


//area contour 
int areaB,areaY;

int im=0;
string str; 
string str2 = ".jpg"; 

//tambahambil hsv
Rect c (panjang/2,lebar/2,7,7);
Scalar lowB,highB,hsvmean,lowY,highY;

//fungsi sortcontour
bool compareContourAreas ( vector<Point> contour1, vector<Point> contour2 ) {
    double i = fabs( contourArea(Mat(contour1)) );
    double j = fabs( contourArea(Mat(contour2)) );
    return ( i < j );
}

int main(int argc, char** argv){
	//awal Mat gray, mask, ero, dila, haar;
	
	
	Mat hsv, roi,maskB,maskY, eroB, dilaB,eroY, dilaY;
	Point cY,cB;
	
	//// start robot
	
	//// end robot
	
	//cap.set(CV_CAP_PROP_AUTO_EXPOSURE,0);
	cap.set(CV_CAP_PROP_FRAME_WIDTH,panjang);
	cap.set(CV_CAP_PROP_FRAME_HEIGHT,lebar);
	

	
	//lowY  = Scalar(23,184,88);
	//highY = Scalar(43,255,208);
	
	//lowB  = Scalar(94,158,44);
	//highB = Scalar(119,255,164);
	
	//pat 1 3 a
	//low Y = [23.0204, 184.776, 88.9184, 0]
	//high Y = [43.0204, 304.776, 208.918, 0]
	//low B = [94.2245, 158.673, 44.4082, 0]
	//high B = [119.224, 278.673, 164.408, 0]

	//labv robot 
	lowB = Scalar(96, 143, 154);
	highB = Scalar(121, 255, 255);

	lowY = Scalar(22, 150, 149);
	highY = Scalar(42, 255, 255);


	//loop kalibrasi awal
	while (true) {
		
		cap >> ori;
		
		
		//resize(ori, ori, Size(panjang, lebar));
			
		
		cvtColor (ori,hsv,COLOR_BGR2HSV);
		
        roi=hsv(c);
        rectangle (ori,c,Scalar(0,0,255),1);
        hsvmean=mean(roi);
        
		imshow("ori", ori);
        int result = waitKey(30);
        
        if(result == 98) //blue (key b)
        {	
			lowB= Scalar(hsvmean[0]-10,hsvmean[1]-70,hsvmean[2]-70);
			highB= Scalar(hsvmean[0]+15,hsvmean[1]+50,hsvmean[2]+50);
			cout<<"low B = "<<lowB<<endl;
			cout<<"high B = "<<highB<<endl;
		} 
		else if(result == 121) //yellow (key y)
        {	
			lowY= Scalar(hsvmean[0]-5,hsvmean[1]-70,hsvmean[2]-70);
			highY= Scalar(hsvmean[0]+15,hsvmean[1]+50,hsvmean[2]+50);	
			cout<<"low Y = "<<lowY<<endl;
			cout<<"high Y = "<<highY<<endl;
		}
		else if(result == 32) //space
        {	
			break;
			
			
		} 
       //cout<<hsvmean[0]<<endl;
	}
	


	
	/*pat 1 3 c
	 low B = [96.6122, 137.918, 63.8571, 0]
	high B = [116.612, 257.918, 133.857, 0]
	low Y = [26.0612, 157.02, 151.98, 0]
	high Y = [46.0612, 277.02, 271.98, 0]
	*/
	//lowB  = Scalar(96,131,185);
	//highB = Scalar(116,255,250);
	
	//lowY  = Scalar(25,161,185);
	//highY = Scalar(46,255,250);
	
	
	
	while (true) {
		
		/*
		////inisiasi robot awal
		
		////end inisiasi robot awal
		
		*/
		int result = waitKey(30);
		t = clock();
		
		cap >> ori;
		resize(ori, ori, Size(320, 240));
		//imshow("ori", ori);
		vector<vector<Point> > contours;
		vector<Vec4i> hierarchy;
		
		
		//visi
		
		cvtColor (ori ,hsv,COLOR_BGR2HSV); 
	
	//blue
		
		//mask 
		inRange (hsv,lowB,highB,maskB);
		
		erode(maskB, eroB, element_ero);
		dilate(eroB, dilaB, element_dila);
		
		//detek contour
		findContours(dilaB, contours, hierarchy, RETR_TREE, CHAIN_APPROX_SIMPLE);
		
		//cek contour
		if (contours.size()!=0){
			//sorting contour
			sort(contours.begin(),contours.end(),compareContourAreas);
			
			//menghaluskan contour
			epsilon = ke * arcLength(contours[contours.size()-1], true);		
			approxPolyDP(Mat(contours[contours.size()-1]), contours[contours.size()-1], epsilon, true);
			
			//gambar contour
			drawContours(ori, contours,contours.size()-1, Scalar(0, 0, 255), 2, 10, hierarchy, 0, Point());
	
			//area contour
			areaB = contourArea(contours[contours.size()-1]);
			
			//centroid
			Moments m= moments(contours[contours.size()-1],true);
			cB = Point (m.m10 / m.m00, m.m01 / m.m00);
			
			circle(ori,cB,3,Scalar(0,0,255));
			//cout<<center<<endl;
		}
		
	//yellow
		
		//mask 
		inRange (hsv,lowY,highY,maskY); 
		
		erode(maskY, eroY, element_ero);
		dilate(eroY, dilaY, element_dila);
		
		//detek contour
		findContours(dilaY, contours, hierarchy, RETR_TREE, CHAIN_APPROX_SIMPLE);
		
		//cek detek contour
		if (contours.size()!=0){

			//sorting contour
			sort(contours.begin(),contours.end(),compareContourAreas);
			
			//menghaluskan contour
			epsilon = ke * arcLength(contours[contours.size()-1], true);		
			approxPolyDP(Mat(contours[contours.size()-1]), contours[contours.size()-1], epsilon, true);
			
			//gambar contour
			drawContours(ori, contours,contours.size()-1, Scalar(0, 255, 0), 2, 10, hierarchy, 0, Point());

			//area contour
			areaY = contourArea(contours[contours.size()-1]);
			
			//centroid
			Moments m= moments(contours[contours.size()-1],true);
			cY= Point (m.m10 / m.m00, m.m01 / m.m00);
			
			circle(ori,cY,3,Scalar(0,0,255));
			
			//cout<<cY<<endl;
		}
		
		//kondisi penetuan gerakan robot
		if ( (cY.x > midL && cY.x < midR) || (cB.x > midL && cB.x < midR) ){
			arah = "lurus";
			markk = "relatif lurus ";
			kon = 1 * x;
			//Walking::GetInstance()->A_MOVE_AMPLITUDE = 0.0;	// jalan lurus
			}
		else if ( cY.x <= midL && cB.x <= mid ) {
			arah = "jalan ke kiri";
			markk = "relatif kiri ";
			kon = 2 * x;
			//Walking::GetInstance()->A_MOVE_AMPLITUDE = 5.0 * x ;	// jalan ke kiri
			}
		else if ( cY.x >= mid && cB.x >= midR ) {
			arah = "jalan ke kanan";
			markk = "relatif kanan ";
			kon = 3 * x;
			//Walking::GetInstance()->A_MOVE_AMPLITUDE = 5.0 * x ;	// jalan ke kiri
			}
		
		//posisi kepala
		if ( cY.y < atas || cB.y < atas ){
			//cout<<"kepala naik"<<endl;
			}
		else if ( cY.y > bawah || cB.y > bawah ){
			//cout<<"kepala turun"<<endl;
			}
		
		//posisi mundur
		if (areaY >= MaxContour || areaB>= MaxContour){
			x = -1 ;
			gerak = "mundur";
			//Walking::GetInstance()->X_MOVE_AMPLITUDE = 10.0 * x;//default maju
			}
		
		
		///// end visi
		
		
		
		imshow("ori", ori);
		//imshow("ori", mask);
		//imshow("kuning ", dilaY);
		//imshow("biru", dilaB);
		//input gambar
		//waitKey(0); 
		//return 0;
		
		//waktu
		t = clock() - t;
		
		//loop
		//cout<<endl;
		
		 if(result == 97) //a
        {	
			//sprintf_s(filename, "C:/Images/Frame_%d.jpg", c); 
			str+="datas/image";
			str+=to_string(im);
			str+=".jpg";
			cout<<str<<endl;
			//str.append(str2,);
			//imwrite(filename, frame);
			imwrite(str, ori);
			im++;
			str="";
			
			cout<<"x biru = "<<cB.x<<"  || y biru = "<<cB.y<<endl;
			cout<<"x kuning = "<<cY.x<<"  || y kuning = "<<cY.y<<endl;
			cout<<"posisi marker terhadap robot : "<<markk<<endl;
			cout << "arah gerakan : " << arah << endl << "kondisi : " << kon << endl << "status robot : " << gerak << endl;
			cout<<"area kuning = "<<areaY<<endl<<"area biru = "<<areaB<<endl;
			cout << "It took me " << t << " clicks (" << (float)t / CLOCKS_PER_SEC * 1000 << " miliseconds).\n"<<endl;
		
		} 
		
		
		 if(result == 32) 
			break;

	}
	
	cap.release();
	
	//video.release();	
	destroyAllWindows;
	return 0;
			
}

