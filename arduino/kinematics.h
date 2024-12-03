#ifndef KINEMATICS_H
#define KINEMATICS_H

#include <Arduino.h>

bool inverse_kinematics(float x, float y, float z, float L1, float L2, float h0, float &theta0, float &theta1, float &theta2);

#endif
