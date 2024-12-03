from setuptools import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import numpy as np

opencv_include = '/usr/include/opencv4/'
opencv_lib_dirs = "/usr/lib/aarch64-linux-gnu/"
opencv_libs = ['opencv_core', 'opencv_highgui', 'opencv_imgproc', 'opencv_imgcodecs', 'opencv_dnn']

print('opencv_include: ', opencv_include)
print('opencv_lib_dirs: ', opencv_lib_dirs)
print('opencv_libs: ', opencv_libs)

# python3 setup.py build_ext --inplace

class custom_build_ext(build_ext):
    def build_extensions(self):
        build_ext.build_extensions(self)

# Obtain the numpy include directory.  This logic works across numpy versions.
try:
    numpy_include = np.get_include()
except AttributeError:
    numpy_include = np.get_numpy_include()


ext_modules = [
    Extension(
        "lib.pyyolotools",
        ["./yolov5postprocess.cpp",
         "./pyyolotools.pyx",],
        include_dirs = [numpy_include, opencv_include],
        language='c++',
        libraries=opencv_libs,
        library_dirs=[opencv_lib_dirs]
        ),
    ]

setup(
    name='pyyolotools',
    ext_modules=ext_modules,
    cmdclass={'build_ext': custom_build_ext},
)

print('Build done')