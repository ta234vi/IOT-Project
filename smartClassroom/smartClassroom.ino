#include <SoftwareSerial.h>  // Add this library for debugging on SoftwareSerial

const int trigPinLeft = 13;
const int echoPinLeft = 12;
const int fanPinLeft = 9;

const int trigPinMiddle = 8;
const int echoPinMiddle = 7;
const int fanPinMiddle = 10;

const int trigPinRight = 5;
const int echoPinRight = 6;
const int fanPinRight = 11;

const int tempPin = A3;

long duration;
float distance;
float temperature;
int fanSpeed;

void setup() {
  Serial.begin(9600);  // Use the same port for COMPIM and debugging

  // Setup pins for ultrasonic and fan control
  pinMode(trigPinLeft, OUTPUT);
  pinMode(echoPinLeft, INPUT);
  pinMode(fanPinLeft, OUTPUT);

  pinMode(trigPinMiddle, OUTPUT);
  pinMode(echoPinMiddle, INPUT);
  pinMode(fanPinMiddle, OUTPUT);

  pinMode(trigPinRight, OUTPUT);
  pinMode(echoPinRight, INPUT);
  pinMode(fanPinRight, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String regions = Serial.readString();  // Read multiple characters from Python ("LMR")

    Serial.print("Received regions: ");  // Debugging: Print received regions
    Serial.println(regions);  // Send it back to Python or terminal

    // Control fans for each region detected
    if (regions.indexOf('L') >= 0) {
      controlFan(trigPinLeft, echoPinLeft, fanPinLeft);
    }
    if (regions.indexOf('M') >= 0) {
      controlFan(trigPinMiddle, echoPinMiddle, fanPinMiddle);
    }
    if (regions.indexOf('R') >= 0) {
      controlFan(trigPinRight, echoPinRight, fanPinRight);
    }

    if (regions == "0") {  // No person detected
      turnOffFans();
    }
  }
  delay(1000);  // Wait 1 second before next check
}

void controlFan(int trigPin, int echoPin, int fanPin) {
  distance = getDistance(trigPin, echoPin);
  temperature = getTemperature();

  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.print(" cm, Temperature: ");
  Serial.print(temperature);
  Serial.print(" C, Fan Speed: ");

  if (distance > 0 && distance <= 500) {
    fanSpeed = mapTemperatureToFanSpeed(temperature);
    analogWrite(fanPin, fanSpeed);
    Serial.println(fanSpeed);  // Debugging: Print fan speed
  } else {
    analogWrite(fanPin, 0);
    Serial.println("0 (Fan Off)");
  }
}

void turnOffFans() {
  analogWrite(fanPinLeft, 0);
  analogWrite(fanPinMiddle, 0);
  analogWrite(fanPinRight, 0);
  Serial.println("Fans turned off");
}

float getDistance(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  duration = pulseIn(echoPin, HIGH);
  float distanceCm = (duration * 0.0343) / 2;
  return distanceCm;
}

float getTemperature() {
  int tempValue = analogRead(tempPin);
  float millivolts = (tempValue / 1024.0) * 5000;
  float tempC = millivolts / 10;
  return tempC;
}

int mapTemperatureToFanSpeed(float temp) {
  if (temp < 25) {
    return 100;
  } else if (temp >= 25 && temp <= 30) {
    return map(temp, 25, 30, 100, 255);
  } else {
    return 255;
  }
}
