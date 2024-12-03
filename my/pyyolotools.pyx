import numpy as np
cimport numpy as np
from libc.string cimport memcpy

cdef extern from "yolotools.h":
    void postprocess_yolov5(float*, int, 
                            int, int, 
                            float, float, 
                            float, float, float,
                            int*, signed int**, float**, signed int**)
    void free_postprocess_yolov5(signed int**, float**, signed int**)


def pypostprocess_yolov5(np.ndarray[np.float32_t, ndim=2] yolov5output, 
                        float fx, float fy,
                        float thre_cof, float thre_score, float thre_nms):
    cdef int rows = yolov5output.shape[0]
    cdef int dimensions = yolov5output.shape[1]
    
    cdef int classnum = dimensions - 5
    assert classnum > 0      #5

    cdef int datanum = rows * dimensions

    cdef int detected_num = 0
    cdef signed int *pclassids
    cdef float *pconfidences
    cdef signed int *pboxes

    postprocess_yolov5(&yolov5output[0, 0], datanum,
                       rows, classnum, fx, fy, 
                       thre_cof, thre_score, thre_nms,
                       &detected_num, &pclassids, &pconfidences, &pboxes)
    
    if detected_num == 0:
        return None
    
    cdef np.ndarray[np.int32_t, ndim=1] classids = np.zeros((detected_num, ), dtype = np.int32)
    cdef np.ndarray[np.float32_t, ndim=1] confidence = np.zeros((detected_num, ), dtype = np.float32)
    cdef np.ndarray[np.int32_t, ndim=2] boxes = np.zeros((detected_num, 4), dtype = np.int32)

    memcpy(&classids[0], pclassids, sizeof(int) * detected_num)
    memcpy(&confidence[0], pconfidences, sizeof(float) * detected_num)
    memcpy(&boxes[0, 0], pboxes, sizeof(int) * detected_num * 4)

    free_postprocess_yolov5(&pclassids, &pconfidences, &pboxes);

    return (classids, confidence, boxes)

