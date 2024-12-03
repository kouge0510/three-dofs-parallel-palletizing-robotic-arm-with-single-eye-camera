#include <iostream>
#include <vector>
#include <opencv2/opencv.hpp>
#include <mutex>
#include "yolotools.h"

std::vector<std::string> load_class_list()
{
  std::vector<std::string> class_list;
  std::ifstream ifs("coco_classes.names");
  std::string line;
  while (getline(ifs, line))
  {
    class_list.push_back(line);
  }
  return class_list;
}

// the following codes are referenced to https://github.com/ultralytics/yolov5/issues/239
void postprocess_yolov5(float *_data, int datanum, 
                        int rows, int classnum,
                        float x_factor, float y_factor, 
                        float thre_cof, float thre_score, float thre_nms,
                        int *_detected_num, signed int **_classids, float **_confidences, signed int **_boxes)
{
  float *data = (float*)_data;
  int dimensions = classnum + 5;
  CV_Assert(datanum == rows * dimensions);
  
  std::vector<cv::Rect> boxes;
  std::vector<int> class_ids;
  std::vector<float> confidences;

  std::mutex mtx;
  cv::parallel_for_(cv::Range(0, rows), [&](const cv::Range& range)
  {
    for (int r = range.start; r < range.end; r++) //
    {
		  float *usage_data = data + r * (classnum + 5);
      float confidence = usage_data[4];
      if (confidence >= thre_cof)
      {
        float *classes_scores  = usage_data + 5;
        cv::Mat scores(1, classnum, CV_32FC1, classes_scores);
        cv::Point class_id;
        double max_class_score;
        cv::minMaxLoc(scores, 0, &max_class_score, 0, &class_id);
        if (max_class_score > thre_score)
        {
          float x = usage_data[0], y = usage_data[1], w = usage_data[2], h = usage_data[3];
          int left = int((x - 0.5 * w) * x_factor);
          int top = int((y - 0.5 * h) * y_factor);
          int width = int(w * x_factor);
          int height = int(h * y_factor);

          mtx.lock();
          confidences.push_back(confidence);
          class_ids.push_back(class_id.x);
          boxes.push_back(cv::Rect(left, top, width, height));
          mtx.unlock();
        }
      }
    }
  });

  // for(float each_cfd: confidences)
  // {
  //   std::cout << each_cfd << ", ";
  // }
  // std::cout << std::endl;
  // for(auto each_box: boxes)
  // {
  //   std::cout << each_box << ", ";
  // }
  // std::cout << std::endl;

  
  std::vector<int> nms_result;
  // std::cout << "thre_score: " << thre_score << std::endl;
  // std::cout << "thre_nms: " << thre_nms << std::endl;
  cv::dnn::NMSBoxes(boxes, confidences, thre_score, thre_nms, nms_result);

  // int *_detected_num, int **_classids, float **confidences, float **boxes
  *_detected_num = nms_result.size();
  *_classids = new signed int[*_detected_num];
  *_confidences = new float[*_detected_num];
  *_boxes = new signed int[*_detected_num * 4];
  //std::cout << *_detected_num << std::endl;
  for(int i = 0; i < *_detected_num; i++)
  {
    int idx = nms_result[i];
    (*_classids)[i] = class_ids[idx];
    (*_confidences)[i] = confidences[idx];
    (*_boxes)[i * 4] = boxes[idx].x;
    (*_boxes)[i * 4 + 1] = boxes[idx].y;
    (*_boxes)[i * 4 + 2] = boxes[idx].width;
    (*_boxes)[i * 4 + 3] = boxes[idx].height;
  }

}

void free_postprocess_yolov5(signed int **_classids, float **_confidences, signed int **_boxes)
{
  if (*_classids)
  {
    delete[] *_classids;
    *_classids = nullptr;
  }
  if (*_confidences)
  {
    delete[] *_confidences;
    *_confidences = nullptr;
  }
  if (*_boxes)
  {
    delete[] *_boxes;
    *_boxes = nullptr;
  }
}