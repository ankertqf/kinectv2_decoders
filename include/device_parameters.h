#ifndef DEVICE_PARAMETERS_H
#define DEVICE_PARAMETERS_H

#include "hdf5.h"
#include "hdf5_hl.h"
#include <string>
#include <vector>

struct Relative_Pose_To_Save
{
	public:
		Relative_Pose_To_Save() {}

		~Relative_Pose_To_Save()
		{
		}

		hvl_t rotation;
		hvl_t translation;
};


struct Camera_Device_To_Save {

	Camera_Device_To_Save()
	{

	}

	~Camera_Device_To_Save()
	{

	}

	hvl_t distortion_coefficients;
	int num_distortion_coefficients;
	hvl_t intrinsic_camera_matrix;

	int camera_type;
};

struct tmp_ir_struct
{
	float fx, fy, cx, cy, k1, k2, k3, p1, p2;
};

class DeviceParametersHandler
{
    public:
        DeviceParametersHandler();
        ~DeviceParametersHandler();
        void init(std::string filename);
        std::vector<float> ztable, xtable;
        std::vector<short> lut;
    private:
        void readCameraParametersFromFile(double** ir_dist, double** rgb_dist, double** ir_intr, double** rgb_intr, double** rotation, double** translation, std::string filename);
        void initializeCameraFromFile(double** dist, double** intr, std::string filename, std::string datastname);
        void initializeRelativePoseFromFile(double** rotation, double** translation, std::string filename);
        bool undistort(double x, double y, double &xu, double &yu, double k1, double k2, double k3, double p1, double p2);
        void distort(double x, double y, double &xd, double &yd, double k1, double k2, double k3, double p1, double p2);

        //Depth decoding
        
        //intrinsics
        double *ir_distortion_parameters, *rgb_distortion_parameters, *ir_camera_matrix, *rgb_camera_matrix;
        //extrinsics
        double* rotation, *translation;
};




#endif
