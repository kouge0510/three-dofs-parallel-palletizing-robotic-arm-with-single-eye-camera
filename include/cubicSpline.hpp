#ifndef CUBIC_SPLINE_HPP
#define CUBIC_SPLINE_HPP

#include <cassert>

template<typename T>
void computeCubicSpline(T theta[], const T t[], const T theta_start, const T theta_end, T tf, const size_t numPoints);

#endif // CUBIC_SPLINE_HPP
