#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <libgen.h>
#include <signal.h>
#include <math.h>
#include <vector>
#include <iostream>
#include "opencv2/opencv.hpp"
#include "opencv2/objdetect.hpp"
#include "opencv2/imgproc/imgproc.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "Camera.h"
#include "mjpg_streamer.h"
#include "LinuxDARwIn.h"
 
#ifdef AXDXL_1024
#define MOTION_FILE_PATH    ((char *)"../../../../Data/motion_1024.bin")
#else
#define MOTION_FILE_PATH    ((char *)"../../../../Data/motion_4096.bin")
#endif
#define INI_FILE_PATH       ((char *)"../../../../Data/config.ini")

#define M_INI   			((char *)"../../../Data/slow-walk.ini")
#define SCRIPT_FILE_PATH    "script.asc"

#define U2D_DEV_NAME0       "/dev/ttyUSB0"
#define U2D_DEV_NAME1       "/dev/ttyUSB1"

using namespace Robot;
 
using namespace cv;
using namespace std;

//cek waktu
//#include <time.h>;
//clock_t t;

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
int isRunning = 1;
LinuxArbotixPro linux_arbotixpro(U2D_DEV_NAME0);
ArbotixPro arbotixpro(&linux_arbotixpro);

void signal_callback_handler(int signum){
    printf("Exiting program; Caught signal %d\r\n", signum);
    isRunning = 0;
}

void change_current_dir(){
    char exepath[1024] = {0};
    if (readlink("/proc/self/exe", exepath, sizeof(exepath)) != -1)
        chdir(dirname(exepath));
}

/*
ambil video
//VideoWriter video("tes.avi",CV_FOURCC('M','J','P','G'),10,Size(panjang,lebar));
*/

//area contour 
int areaB,areaY;

//
int head=0;

//tambahambil hsv
Rect c (panjang/2,lebar/2,7,7);
Scalar lowB,highB,hsvmean,lowY,highY;

//fungsi sortcontour
/*bool compareContourAreas ( std::vector<cv::Point> contour1, std::vector<cv::Point> contour2 ) {
    double i = fabs( contourArea(cv::Mat(contour1)) );
    double j = fabs( contourArea(cv::Mat(contour2)) );
    return ( i < j );
}
*/

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
	cout<< "\n===== Walk Backward Tutorial for DARwIn =====\n\n";
    change_current_dir();
    minIni* ini = new minIni(INI_FILE_PATH);
    //////////////////// Framework Initialize ////////////////////////////
    LinuxArbotixPro linux_arbotixpro(U2D_DEV_NAME0);
        ArbotixPro arbotixpro(&linux_arbotixpro);
    if (MotionManager::GetInstance()->Initialize(&arbotixpro) == false)
        {
            linux_arbotixpro.SetPortName(U2D_DEV_NAME1);
            if (MotionManager::GetInstance()->Initialize(&arbotixpro) == false)
                {
                    printf("Fail to initialize Motion Manager!\n");
                    return 0;
                }
        }

    Walking::GetInstance()->LoadINISettings(ini);
    usleep(100);
    MotionManager::GetInstance()->LoadINISettings(ini);

    MotionManager::GetInstance()->AddModule((MotionModule*)Action::GetInstance());
    MotionManager::GetInstance()->AddModule((MotionModule*)Head::GetInstance());
    MotionManager::GetInstance()->AddModule((MotionModule*)Walking::GetInstance());
    LinuxMotionTimer linuxMotionTimer;
    linuxMotionTimer.Initialize(MotionManager::GetInstance());
    linuxMotionTimer.Start();
    MotionManager::GetInstance()->SetEnable(true);
    
    /////////////////////////Capture Motor Position//////////////////////
    int n = 0;
    int param[JointData::NUMBER_OF_JOINTS * 5];
    int wGoalPosition, wStartPosition, wDistance;
    for (int id = JointData::ID_R_SHOULDER_PITCH; id < JointData::NUMBER_OF_JOINTS; id++)
        {
            wStartPosition = MotionStatus::m_CurrentJoints.GetValue(id);
            wGoalPosition = Walking::GetInstance()->m_Joint.GetValue(id);
            if ( wStartPosition > wGoalPosition )
                wDistance = wStartPosition - wGoalPosition;
            else
                wDistance = wGoalPosition - wStartPosition;

            wDistance >>= 2;
            if ( wDistance < 8 )
                wDistance = 8;

            param[n++] = id;
            param[n++] = ArbotixPro::GetLowByte(wGoalPosition);
            param[n++] = ArbotixPro::GetHighByte(wGoalPosition);
            param[n++] = ArbotixPro::GetLowByte(wDistance);
            param[n++] = ArbotixPro::GetHighByte(wDistance);
        }

    arbotixpro.SyncWrite(AXDXL::P_GOAL_POSITION_L, 5, JointData::NUMBER_OF_JOINTS - 1, param);    
    cout<<"Ready .....";
    Walking::GetInstance()->m_Joint.SetAngle(3,25);
    Walking::GetInstance()->m_Joint.SetAngle(4,-25);
    
    Head::GetInstance()->m_Joint.SetEnableHeadOnly(true, true);
    Walking::GetInstance()->m_Joint.SetEnableBodyWithoutHead(true, true);
    MotionManager::GetInstance()->SetEnable(true);
	
	//// end robot
	
	
	//cap.set(CV_CAP_PROP_AUTO_EXPOSURE,0);
	//cap.set(CV_CAP_PROP_FRAME_WIDTH,panjang);
	//cap.set(CV_CAP_PROP_FRAME_HEIGHT,lebar);
	
	
	//loop kalibrasi 
	while (true) {
		
		cap >> ori;
		
		
		resize(ori, ori, Size(panjang, lebar));
			
		
		cvtColor (ori,hsv,COLOR_BGR2HSV);
		
        roi=hsv(c);
        rectangle (ori,c,Scalar(0,0,255),1);
        hsvmean=mean(roi);
        
		imshow("ori", ori);
        int result = waitKey(30);
        
        if(result == 98) //blue (key b)
        {	
			lowB= Scalar(hsvmean[0]-10,hsvmean[1]-70,hsvmean[2]-70);
			highB= Scalar(hsvmean[0]+10,hsvmean[1]+50,hsvmean[2]);
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
	
	/*
	
	low B = [97.2041, 127.898, 165.98, 0]
	high B = [117.204, 297.898, 295.98, 0]
	low Y = [18.9796, 88.245, 185, 0]
	high Y = [38.9796, 321.245, 315, 0]
		
	low Y = [20, 93.5102, 185, 0]
high Y = [40, 213.51, 255, 0]
low B = [94.6327, 119.388, 185, 0]
high B = [114.633, 239.388, 255, 0]


	hsv kalibrasi
	*/
	/*
	lowB  = Scalar(97,127,165);
	highB = Scalar(117,255,255);
	lowY  = Scalar(10,30,110);
	highY = Scalar(50,255,255);
	* 
	* 
	* pat 1 3c
	* pat 1 3 c
	 low B = [96.6122, 137.918, 63.8571, 0]
	high B = [116.612, 257.918, 133.857, 0]
	low Y = [26.0612, 157.02, 151.98, 0]
	high Y = [46.0612, 277.02, 271.98, 0]
	
	*/
	
	/*
	r seminar
	*/
	//lowB  = Scalar(103,135,134);
	//highB = Scalar(123,255,250);
	
	//lowY  = Scalar(26,131,150);
	//highY = Scalar(46,255,250);
	
	
	/*
	kelas
	lowB  = Scalar(103,135,134);
	highB = Scalar(123,255,250);
	lowY  = Scalar(26,131,150);
	highY = Scalar(46,255,250);
	
	*/
	
	//pat 1 3 a
	lowY  = Scalar(23,184,88);
	highY = Scalar(43,255,208);
	
	lowB  = Scalar(94,158,44);
	highB = Scalar(119,255,164);
	
	while (true) {
		
		
		////inisiasi robot awal
		if(Action::GetInstance()->IsRunning() == 0){
			Head::GetInstance()->m_Joint.SetEnableHeadOnly(true, true);
            Walking::GetInstance()->m_Joint.SetEnableBodyWithoutHead(true, true);
            if(Walking::GetInstance()->IsRunning() == false){
				//Start walking algorithm
                
				Walking::GetInstance()->A_MOVE_AMPLITUDE = 0.0; //default lurus
				Walking::GetInstance()->X_MOVE_AMPLITUDE = 15.0;//default maju
				Walking::GetInstance()->PERIOD_TIME = 1500.0;
				Walking::GetInstance()->Z_MOVE_AMPLITUDE = 30.0;
				Walking::GetInstance()->Y_OFFSET = 50.0;
				Walking::GetInstance()->R_OFFSET = 20.0;
				Walking::GetInstance()->Z_OFFSET = 60.0;
				Walking::GetInstance()->Y_SWAP_AMPLITUDE = 20.0;
				Walking::GetInstance()->Z_SWAP_AMPLITUDE = 3.0;
				Walking::GetInstance()->HIP_PITCH_OFFSET = 7.6;
				
				Walking::GetInstance()->Start();
				
				//Start walking algorithm
                
                //default
				
				
				
            }
		}	
		////end inisiasi robot awal
		
		
		
		//t = clock();
		
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
			kon = 1 * x;
			Walking::GetInstance()->A_MOVE_AMPLITUDE = 0.0;	// jalan lurus
			}
		else if ( cY.x <= midL && cB.x <= mid ) {
			arah = "jalan ke kiri";
			kon = 2 * x;
			Walking::GetInstance()->A_MOVE_AMPLITUDE = 5.0 * x ;	// jalan ke kiri
			}
		else if ( cY.x >= mid && cB.x >= midR ) {
			arah = "jalan ke kanan";
			kon = 3 * x;
			Walking::GetInstance()->A_MOVE_AMPLITUDE = 5.0 * x ;	// jalan ke kiri
			}
		
		//posisi kepala
		if ( cY.y < atas || cB.y < atas ){
			cout<<"kepala naik"<<endl;
			 Head::GetInstance()->MoveByAngle(0,10);
			}
		else if ( cY.y > bawah || cB.y > bawah ){
			cout<<"kepala turun"<<endl;
			 Head::GetInstance()->MoveByAngle(0,-10);
			}
		
		//posisi mundur
		if (areaY >= MaxContour || areaB>= MaxContour){
			x = -1 ;
			gerak = "mundur";
			Walking::GetInstance()->X_MOVE_AMPLITUDE = 10.0 * x;//default maju
			}
		
		cout << "arah gerakan : " << arah << endl << "kondisi : " << kon << endl << "status robot : " << gerak << endl;
		
		cout<<"kuning = "<<areaY<<endl<<"biru = "<<areaB<<endl;
		///// end visi
		
		
		//ambil video
		//video.write(ori);
		
		imshow("final", ori);
		//imshow("hsv", hsv);
		//imshow("kuning ", dilaY);
		//imshow("biru", dilaB);
		//input gambar
		//waitKey(0); 
		//return 0;
		
		//waktu
		//t = clock() - t;
		//cout << "It took me " << t << " clicks (" << (float)t / CLOCKS_PER_SEC * 1000 << " miliseconds).\n";
		
		//loop
		cout<<endl;
		if (waitKey(30) >= 0) 
			break;

	}
	
	cap.release();
	
	//video.release();	
	destroyAllWindows;
	return 0;
			
}

