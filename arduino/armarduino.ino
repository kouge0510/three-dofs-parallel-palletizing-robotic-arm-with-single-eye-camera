#include <Arduino.h>
#include <Servo.h>
#include "CubicSpline.h"
#include "kinematics.h"

float L1 = 29.0;       //逆运动学机械臂参数
float L2 = 25.0;
float h0 = 8.0;

const int numServos = 6; // 舵机数量
Servo servos[numServos]; // 舵机对象数组
int servoPins[numServos] = {0, 1, 2, 3, 4, 5}; // 舵机连接引脚
float alpha1, alpha2;   //逆运动学计算用到的角度变量
float theta0, theta1, theta2;
Servo pump; // 气泵
Servo diancifa; // 电磁阀

const float tf = 2.0; // 时间总长
const int numPoints = 21; // 样条曲线点的数量 (tf / 0.1 + 1)
const float updateInterval = 30; // 更新间隔，单位为毫秒
float t[numPoints];
float theta[numPoints];


void setup() {
    Serial.begin(9600);
    Serial.println("请输入三个逗号分隔的数字 (例如: 10,15,30):");
    // 初始化舵机引脚
  for (int i = 0; i < numServos; i++) {
    servos[i].attach(servoPins[i]);
  }
  pump.attach(A0);
  diancifa.attach(A1);
  pump.write(0);
  diancifa.write(0);

  // 生成时间点数组
  for (int i = 0; i < numPoints; i++) {
    t[i] = i * 0.1;
  }

  servos[5].write(0);
  servos[2].write(0);
  servos[3].write(88);
  servos[4].write(103);
  delay(2000);
}

void loop() {
  if (Serial.available()) {
        String input = Serial.readStringUntil('\n'); // 读取一行输入
        input.trim(); // 去除首尾空白字符
        
        int firstComma = input.indexOf(','); // 第一个逗号的位置
        int secondComma = input.indexOf(',', firstComma + 1); // 第二个逗号的位置
        
        if (firstComma != -1 && secondComma != -1) { // 确保有两个逗号
            String xStr = input.substring(0, firstComma);
            String yStr = input.substring(firstComma + 1, secondComma);
            String zStr = input.substring(secondComma + 1);
            
            float x = xStr.toFloat();
            float y = yStr.toFloat();
            float z = zStr.toFloat();
            
            Serial.print("x = ");
            Serial.println(x);
            Serial.print("y = ");
            Serial.println(y);
            Serial.print("z = ");
            Serial.println(z);
            
            // 调用逆运动学函数
            
            if (inverse_kinematics(x, y, z, L1, L2, h0, theta0, theta1, theta2)) {
                
                if (0 <= theta0 && theta0 <= 90) {
                    alpha1 = theta0 / 2;
                } else if (90 < theta0 && theta0 <= 180 || -90 <= theta0 && theta0 < 0) {
                    alpha1 = (theta0 + 180) / 2;
                } else if (-180 <= theta0 && theta0 < -90) {
                    alpha1 = (theta0 + 360) / 2;
                }
                
                alpha2=180-theta1;
                
                Serial.print("θ0 = ");
                Serial.print((int)alpha1);
                Serial.println("°");
                
                Serial.print("θ1 = ");
                Serial.print((int)alpha2);
                Serial.println("°");
                
                Serial.print("θ2 = ");
                Serial.print((int)theta2);
                Serial.println("°");
            } else {
                Serial.println("末端点不可达");
            }
        } else {
            Serial.println("输入格式错误，请重新输入:");
        }
        ServoRotate(0, alpha1, 2);
         delay(1000);
        ServoRotate(90, alpha2, 3);
        ServoRotate(90, theta2, 4);
        delay(2000);
  pump.write(180);
  diancifa.write(0);
  delay(3000);
  pump.write(0);
  diancifa.write(0);

  ServoRotate(alpha1, 22, 2);
  delay(1000);
  ServoRotate(alpha2, 75, 3);
  delay(1000);
  ServoRotate(theta2, 132, 4);
  delay(1000);
  pump.write(0);
  diancifa.write(180);
  delay(800);
  pump.write(0);
  diancifa.write(0);
  delay(2000);

  ServoRotate(70, 90, 3);
  delay(500);
  ServoRotate(132, 90, 4);
  delay(500);
  ServoRotate(0, 0, 2);
  delay(500);

  ServoRotate(0, 50, 5);
  delay(1000);
  ServoRotate(50, 0, 5);
  delay(5000);
}

    
}

void ServoRotate(float start, float end, int j) {
  computeCubicSpline(t, theta, start, end, tf, numPoints);
  for (int i = 0; i < numPoints; i++) {
    int servoPos = map(theta[i], 0, 180, 0, 180); // 将角度值映射到舵机的范围
    servos[j].write(servoPos);
    delay(updateInterval);
  }
}
/*



void setup() {
  Serial.begin(9600);
  Serial.println("请输入目标坐标 (x y z):");
  
  // 初始状态
  Serial.println("Setting initial position...");
  servos[5].write(0);
  ServoRotate(0, 0, 2);
  servos[3].write(90);
  servos[4].write(90);
  delay(2000);

  // 其他动作


void loop() {}


}*/
