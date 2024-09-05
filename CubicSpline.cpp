#include "CubicSpline.h"

void computeCubicSpline(float t[], float theta[], float theta_start, float theta_end, float tf, int numPoints) {
    float a0 = theta_start;
    float a1 = 0;
    float a2 = 3.0 / (tf * tf) * (theta_end - theta_start);
    float a3 = -2.0 / (tf * tf * tf) * (theta_end - theta_start);

    for (int i = 0; i < numPoints; i++) {
        theta[i] = a0 + a1 * t[i] + a2 * t[i] * t[i] + a3 * t[i] * t[i] * t[i];
    }
}
