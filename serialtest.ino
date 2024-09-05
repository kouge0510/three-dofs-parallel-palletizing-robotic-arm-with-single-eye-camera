#include<Servo.h>
#include <Arduino.h>
#include "CubicSpline.h"
Servo pump;       //气泵
Servo diancifa;   //电磁阀
const int numServos = 10; // 舵机数量
Servo servos[numServos]; // 舵机对象数组
int servoPins[numServos] = {0, 1, 2, 3, 4, 5,6,7,8,9}; // 舵机连接引脚....7号引脚坏了，，替换成9号引脚，但是舵机转动角度有问题
//5和9号舵机角度为40~90度，6和8号舵机角度为90~140度
const float tf = 3.0; // 时间总长
const int numPoints = 31; // 样条曲线点的数量 (tf / 0.1 + 1)
const float updateInterval = 20; // 更新间隔，单位为毫秒
float t[numPoints];
float theta[numPoints];

void ServoRotate(float start1, float end1, int j1, float start2 = -1, float end2 = -1, int j2 = -1) {
  computeCubicSpline(t, theta, start1, end1, tf, numPoints);
  float theta2[numPoints];
  if (start2 != -1 && end2 != -1 && j2 != -1) {
    computeCubicSpline(t, theta2, start2, end2, tf, numPoints);
  }
  
  for (int i = 0; i < numPoints; i++) {
    int servoPos1 = map(theta[i], 0, 180, 0, 180); // 将角度值映射到舵机的范围
    servos[j1].write(servoPos1);
    
    if (start2 != -1 && end2 != -1 && j2 != -1) {
      int servoPos2 = map(theta2[i], 0, 180, 0, 180);
      servos[j2].write(servoPos2);
    }

    delay(updateInterval);
  }
}



void setup() {  
  Serial.begin(9600); // 初始化硬件串口，波特率9600
  for (int i = 0; i < numServos; i++) {
    servos[i].attach(servoPins[i]);
  }
  pump.attach(A2);
  diancifa.attach(A1);
  pump.write(0);
  diancifa.write(0);
  for (int i = 0; i < numPoints; i++) {
    t[i] = i * 0.1;
  }
  servos[5].write(90);              //四个仓库位置初始化
  servos[6].write(90);
  servos[8].write(90);
  servos[9].write(90);
  servos[2].write(0);
  servos[3].write(88);               //机械臂初始位置，已加补偿  3号-2，4号+13
  servos[4].write(103);
  delay(500);
  //Serial.println("Arduino is ready");

}

void loop() {
  
  // 接收数据
  if (Serial.available()) {
    String receivedData = Serial.readStringUntil('\n'); // 读取直到换行符的数据
    receivedData.trim(); // 去除可能的空白字符
    //Serial.print("接收到的数据: ");
    //Serial.println(receivedData);

    if (receivedData == "go") { //启动机械臂至目标点
      Serial.println("get");
      ServoRotate(0, 42, 2);
      delay(500);
      ServoRotate(103, 140, 4, 88, 62, 3);
      delay(1000);
      // ServoRotate(115, 103, 4, 75, 88, 3);
      // ServoRotate(45, 0, 2);
      Serial.println("done");
    }
  
    if (receivedData == "Guangzhou") { //5号舵机对应1号位置：武汉
      Serial.println("get");

      ServoRotate(62, 55,3, 140, 88, 4);
      pump.write(180);
      ServoRotate(92, 81, 4);
      
      
      diancifa.write(0);
      delay(3500);
      MoveToWareHouse(8);
      Serial.println("finish");
    }

    if (receivedData == "Shanghai") { 
      Serial.println("get");
      ServoRotate(62, 50,3, 140, 70, 4);
      pump.write(180);
      ServoRotate(81, 70, 4);
      
      diancifa.write(0);
      delay(3500);
      MoveToWareHouse(9);
      Serial.println("finish");
    }
 
    if (receivedData == "position2") {
      Serial.println("get");
      WareHouseServo(8);
      Serial.println("complete");
      }
    if (receivedData == "position1") {
      Serial.println("get");
      WareHouseServo(9);
      Serial.println("complete");
      }

    if (receivedData == "reset") {
      Serial.println("get");
      ServoRotate(115, 103, 4, 75, 88, 3);
      ServoRotate(45, 0, 2);

      }

  }
}



void WareHouseServo(int i){                    //仓库舵机转动函数  舵机号5~12为仓库舵机
  if(i==8)
  {
    ServoRotate(90, 140, i);
    delay(2000);
    ServoRotate(140, 90, i);
  }

  if(i==9){
    ServoRotate(90, 40, i);
    delay(2000);
    ServoRotate(40, 90, i);
  }
}


void MoveToWareHouse(int i){
  int val1,val2,val3;
  if(i==5){
    val1=19;
  }
  if(i==6){
    val1=70;
  }
   if(i==9){
    val1=109;
  }
   if(i==8){
    val1=160;
  }
    val2=109;
    val3=90;
  ServoRotate(62,99, 3, 81, 99, 4);                    //移至仓库
  ServoRotate(99, 120, 4);



  delay(500);
  ServoRotate(99, val2, 3,42, val1, 2);     //2，3号舵机转动
  delay(500);
  //Serial.println(val1);    
  ServoRotate(120, val3, 4);
  delay(500);    
  pump.write(0);             //放下物体
  diancifa.write(180);
  delay(800);
  pump.write(0);
  diancifa.write(0);
  delay(2000);
  ServoRotate(val3, 120, 4, val2, 88, 3);          //机械臂回到初位置
  delay(500);
  ServoRotate(val1, 0, 2, 120, 103, 4);
  delay(500);
}



