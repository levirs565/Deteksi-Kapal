#include <SoftwareSerial.h>
#include <Servo.h>
#include <TinyGPS++.h>

#define GPS_TX 3
#define GPS_RX 2
#define MOTOR1_PIN 13
#define MOTOR2_PIN 12

Servo esc1, esc2;
TinyGPSPlus gps;

void setup() {
  Serial.println("Setup");
  esc1.attach(MOTOR1_PIN);
  esc2.attach(MOTOR2_PIN);
  Serial.begin(2000000);
  Serial1.begin(9600);

  // Signal for 'Ready'
  esc1.writeMicroseconds(800);
  esc2.writeMicroseconds(800);
  delay(3000);
  ss.begin(9600);

  
  Serial.println("M-READY");
  Serial.setTimeout(10);
}

String input_string, motor_command;
int base_speed = 2200, motor1_speed, motor2_speed;
float value;

long last_gps_update = 0;

void loop() {
  extract_command();
  while (Serial1.available() > 0) {
    char c = Serial1.read();
    gps.encode(c);  // Encode GPS data
  }
  if (milis()-last_gps_update >= 1000 || last_gps_update == 0) 
    if (gps.location.isUpdated() && gps.location.isValid()) {
      Serial.print(gps.location.lat(), 6);
      Serial.print(",");
      Serial.print(gps.location.lng(), 6);
      Serial.print(",");
      Serial.println(gps.speed.mps());
      last_gps_update = milis();
    }
  // put your main code here, to run repeatedly:
  
  motor_command.trim();
  if (motor_command == "b") {
      base_speed = value;
      motor_command = "";
  }
  if (motor_command == "ml") {
      Serial.print("Set left ");
      Serial.print(value);
      motor1_speed = base_speed - (base_speed - 800) * ((100.0-value)/100.0);
      Serial.print(",");
      Serial.println(motor1_speed);
      esc1.writeMicroseconds(motor1_speed);
      motor_command = "";
  }
  if (motor_command == "mr") {
      Serial.print("Set right ");
      Serial.print(value);
      motor2_speed = base_speed - (base_speed - 800) * ((100.0-value)/100.0);
      Serial.print(",");
      Serial.println(motor2_speed);
      esc2.writeMicroseconds(motor2_speed);
      
      motor_command = "";
  }
  if (motor_command == "ms") {
    esc2.writeMicroseconds(800);
      
    motor_command = "";
  }
}

String last_buffer = ""
void extract_command(){
  last_buffer += Serial.readStringUntil('\n');

  int new_line_index = last_buffer.indexOf('\n');
  
  if (new_line_index == -1) {
    input_string = "";
  } else {
    input_string = last_buffer.substring(0, new_line_index);

    if (new_line_index + 1 == (int) last_buffer.length()) {
      last_buffer = ""
    } else {
      last_buffer = last_buffer.substring(new_line_index + 1);
    }
  }

  input_string.trim();
  int delimiterIndex = input_string.indexOf('-');
  if (delimiterIndex != -1 ) {
    motor_command = input_string.substring(0, delimiterIndex);
    String tmp = input_string.substring(delimiterIndex+1);
    tmp.trim();
    value = tmp.toFloat();
  }
}