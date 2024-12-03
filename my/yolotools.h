#ifndef YOLOV5_TOOLS_H
#define YOLOV5_TOOLS_H

void postprocess_yolov5(float *_data, int datanum, 
                        int rows, int classnum,
                        float x_factor, float y_factor, 
                        float thre_cof, float thre_score, float thre_nms,
                        int *_detected_num, signed int **_classids, float **_confidences, signed int **_boxes);
void free_postprocess_yolov5(signed int **_classids, float **_confidences, signed int **_boxes);
#endif