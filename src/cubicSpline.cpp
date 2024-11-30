#include "../include/cubicSpline.hpp"

template<typename T>
void computeCubicSpline(T theta[], const T t[], const T theta_start, const T theta_end, T tf, const size_t numPoints) {

    assert( static_cast<T>((tf * tf) * (theta_end - theta_start)) != static_cast<T>(0));
    assert( static_cast<T>((tf * tf * tf) * (theta_end - theta_start)) != static_cast<T>(0));

    T a0 = theta_start;
    T a1 = std::static_cast<T>(0);
    T a2 = static_cast<T>(3.0 / (tf * tf) * (theta_end - theta_start));
    T a3 = static_cast<T>(-2.0 / (tf * tf * tf) * (theta_end - theta_start));
    
    for (int i = 0; i < numPoints; i++) {
        theta[i] = a0 + a1 * t[i] + a2 * t[i] * t[i] + a3 * t[i] * t[i] * t[i];
    }
};
