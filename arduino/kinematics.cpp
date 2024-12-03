#include "kinematics.h"

bool inverse_kinematics(float x, float y, float z, float L1, float L2, float h0, float &theta0, float &theta1, float &theta2) {
    theta0 = degrees(atan2(y, x));
    
    float r = sqrt(x * x + y * y);
    float z_prime = z - h0;
    
    if (r > L1 + L2 || r < fabs(L1 - L2)) {
        return false; // 不可达
    }

    float alpha = degrees(atan2(z_prime,r));
    
    float cos_beta = (r * r + z_prime * z_prime + L1 * L1 - L2 * L2) / (2 * sqrt(r * r + z_prime * z_prime) * L1);
    if (cos_beta < -1 || cos_beta > 1) {
        return false; // 不可达
    }
    float beta = degrees(acos(cos_beta));
    theta1 = alpha + beta;

    float cos_theta2 = (r * r + z_prime * z_prime - L1 * L2 - L2 * L2) / (2 * L1 * L2);
    if (cos_theta2 < -1 || cos_theta2 > 1) {
        return false; // 不可达
    }
    theta2 = degrees(acos(cos_theta2))- (theta1-90) ;
    
    
    
    return true;
}
