#include "Servo.h"
#include <PS2X_lib.h>

#define PS2_DAT        24
#define PS2_CMD        28
#define PS2_SEL        22
#define PS2_CLK        26

#define pressures   false
#define rumble      false

#define pwm1 3
#define pwm2 4
#define dir1MA 16
#define dir2MA 14
#define dir1MB 15
#define dir2MB 2
#define servoCameraYaw 5
#define servoCameraPitch 6
#define voltage A0
#define accel 48

#define sharp1 A4
#define sharp2 A5
#define sharp3 A6
#define sharp4 A7
#define sharp5 A8
#define sharp6 A9

#define threshold_h 400
#define threshold_v 300

#define servo_pin 10

String received_message = "";
String action = "";
String answer = "";
String args = "";
int speedL = 0;
int speedR = 0;
int targetSpeedL = 0;
int targetSpeedR = 0;
double accelTime = 0;
double move_time = 0;
int flag_wait = 0;
int manual_speed = 50;

int error = 0;
byte type = 0;
byte vibrate = 0;
int mode = 0;
double time_controller = 0;



const int numReadings = 2;

int readings1[numReadings];
int readings2[numReadings];
int readings3[numReadings];
int readings4[numReadings];
int readings5[numReadings];
int readings6[numReadings];

int total1 = 0;
int total2 = 0;
int total3 = 0;
int total4 = 0;
int total5 = 0;
int total6 = 0;

int index = 0;


int s1 = 0, s2  = 0, s3 = 0, s4 = 0, s5 = 0, s6 = 0;


Servo servo;

PS2X ps2x;

void ports_initializing() {
  pinMode(pwm1, OUTPUT);
  pinMode(pwm2, OUTPUT);
  pinMode(dir1MA, OUTPUT);
  pinMode(dir2MA, OUTPUT);
  pinMode(dir1MB, OUTPUT);
  pinMode(dir2MB, OUTPUT);
  pinMode(voltage, INPUT);
  pinMode(23, OUTPUT);
  pinMode(25, OUTPUT);

  pinMode(sharp1, INPUT);
  pinMode(sharp2, INPUT);
  pinMode(sharp3, INPUT);
  pinMode(sharp4, INPUT);
  pinMode(sharp5, INPUT);
  pinMode(sharp6, INPUT);


  digitalWrite(pwm1, LOW);
  digitalWrite(pwm2, LOW);
  digitalWrite(dir1MA, LOW);
  digitalWrite(dir2MA, LOW);
  digitalWrite(dir1MB, LOW);
  digitalWrite(dir2MB, LOW);
  digitalWrite(23, LOW);
  //  digitalWrite(25, HIGH);
  //  delay(100000);
  //  digitalWrite(25, LOW);

  servo.attach(servo_pin);
  //servoYaw.attach(servoCameraYaw);
}

void gamepad_initializing() {
  while (true) {
    error = ps2x.config_gamepad(PS2_CLK, PS2_CMD, PS2_SEL, PS2_DAT, pressures, rumble);
    if (error == 0) {
      Serial.println("controller_ok");
      digitalWrite(25, HIGH);
      delay(200);
      digitalWrite(25, LOW);
      delay(200);
      digitalWrite(25, HIGH);
      delay(200);
      digitalWrite(25, LOW);
      break;
      //Serial.print("Found Controller, configured successful ");
      //Serial.println("Try out all the buttons, X will vibrate the controller, faster as you press harder;");
      //Serial.println("holding L1 or R1 will print out the analog stick values.");
      //Serial.println("Note: Go to www.billporter.info for updates and to report bugs.");
    }
    else if (error == 1) {
      //Serial.println("No controller found, check wiring, see readme.txt to enable debug. visit www.billporter.info for troubleshooting tips");
      Serial.println("controller_fail");

      digitalWrite(25, HIGH);
      delay(300);
      digitalWrite(25, LOW);
      delay(300);

    }
    else if (error == 2) {
      //Serial.println("Controller found but not accepting commands. see readme.txt to enable debug. Visit www.billporter.info for troubleshooting tips");
      Serial.println("controller_fail");

      digitalWrite(25, HIGH);
      delay(300);
      digitalWrite(25, LOW);
      delay(300);
    }
    else if (error == 3) {
      //Serial.println("Controller refusing to enter Pressures mode, may not support it. ");
      Serial.println("controller_fail");
      digitalWrite(25, HIGH);
      delay(300);
      digitalWrite(25, LOW);
      delay(300);
    }
    //  Serial.print(ps2x.Analog(1), HEX);

    type = ps2x.readType();
  }
}

double get_vcc() {
  double vcc = analogRead(voltage) * 0.0301;
  return vcc;
}

void accelerate() {
  if ((micros() - accelTime * 1000) > (100000 / accel)) {
    accelTime = micros() / 1000;
    speedR += constrain((targetSpeedR - speedR), -1, 1);
    speedL += constrain((targetSpeedL - speedL), -1, 1);
  }
}

void motors() {
  if ((move_time != 0) && (millis() - move_time > 0)) {
    String mmmm = String(move_time);
    move_time = 0;
    targetSpeedR = 0;
    targetSpeedL = 0;
    if (flag_wait == 1) {
      Serial.println("DONE " + mmmm);
      flag_wait = 0;
    }
  }
  digitalWrite(dir1MA, speedR >= 0 ? HIGH : LOW);
  digitalWrite(dir2MA, speedR < 0 ? HIGH : LOW);
  digitalWrite(dir1MB, speedL >= 0 ? HIGH : LOW);
  digitalWrite(dir2MB, speedL < 0 ? HIGH : LOW);
  analogWrite(pwm1, abs(speedR));
  analogWrite(pwm2, abs(speedL));
}

void move(int speed1, int speed2) {
  sensors_read();
  //10.5 50
  int a = threshold_h * float(map(float(speed1), 0, 255, 9, 0)) * 0.1;
  if (s1 > a || s2 < threshold_v || s3 > a || s4 < threshold_v || s5 > a || s6 < threshold_v) {
    if (speed1 < 0 && speed2 < 0) {
      targetSpeedR = speed1;
      targetSpeedL = speed2;
    } else {
      targetSpeedR = 0;
      targetSpeedL = 0;
    }
  } else {
    targetSpeedR = speed1;
    targetSpeedL = speed2;
  }
}

void act(String action, String args) {
  if (action.equals("CONNECT")) {
    Serial.print(" CONNECTED");
    delay(500);
  }
  if (action.equals("MOVE")) {
    move_time = 0;
    int ind1 = args.indexOf('|'); //finds location of second ,
    int speed1 = args.substring(0, ind1).toInt(); //captures second data String
    int ind2 = args.indexOf('|', ind1 + 1);
    int speed2 = args.substring(ind1 + 1, ind2 + 1).toInt();
    move(speed1, speed2);
  }
  if (action.equals("MOVE_TIME")) {
    int ind1 = args.indexOf('|'); //finds location of second ,
    int speed1 = args.substring(0, ind1).toInt(); //captures second data String
    int ind2 = args.indexOf('|', ind1 + 1);
    int speed2 = args.substring(ind1 + 1, ind2 + 1).toInt();
    int ind3 = args.indexOf('|', ind2 + 1);
    move_time = args.substring(ind2 + 1, ind3 + 1).toInt();
    move_time = millis() + move_time;
    move(speed1, speed2);
    if (args.indexOf("WAIT") > 0) {
      flag_wait = 1;
    }
  }
  if (action.equals("SERVO_YAW")) {
    int ind1 = args.indexOf('|');
    int servo = args.substring(0, ind1).toInt();
    //servoYaw.write(constrain(servo, 0, 180));
  }
  if (action.equals("SERVO_PITCH")) {
    int ind1 = args.indexOf('|');
    int servo = args.substring(0, ind1).toInt();
    //servoPitch.write(constrain(servo, 0, 180));
  }
  if (action.equals("VCC")) {
    Serial.print("|" + String(get_vcc()));
  }
  Serial.println();
}


void sensors_read() {
  total1 -= readings1[index];
  readings1[index] = analogRead(sharp1);
  total1 += readings1[index];
  s1 = abs(total1 / numReadings);

  total2 -= readings2[index];
  readings2[index] = analogRead(sharp2);
  total2 += readings2[index];
  s2 = abs(total2 / numReadings);

  total3 -= readings3[index];
  readings3[index] = analogRead(sharp3);
  total3 += readings3[index];
  s3 = abs(total3 / numReadings);

  total4 -= readings4[index];
  readings4[index] = analogRead(sharp4);
  total4 += readings4[index];
  s4 = abs(total4 / numReadings);

  total5 -= readings5[index];
  readings5[index] = analogRead(sharp5);
  total5 += readings5[index];
  s5 = abs(total5 / numReadings);

  total6 -= readings6[index];
  readings6[index] = analogRead(sharp6);
  total6 += readings6[index];
  s6 = abs(total6 / numReadings);


  index++;
  if (index == numReadings)
    index = 0;
}


void setup() {
  Serial.begin(500000); //50 microseconds per symbol
  Serial.println("begin");
  delay(3000);
  ports_initializing();
  servo.write(100);
  servo.write(40);
  delay(500);
  servo.write(100);
  gamepad_initializing();
  ps2x.read_gamepad(false, 0);
  ps2x.ButtonReleased(PSB_START);
  mode = 0;
  digitalWrite(25, LOW);
}

void loop() {
  double xxx = millis();
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c != '\n') {
      received_message += c;
    }
    else {
      if (received_message.length() > 0) {
        int ind1 = received_message.indexOf('|');  //finds location of first |
        if (ind1 != -1) {
          action = received_message.substring(0, ind1);   //captures first data String (action)
          args = received_message.substring(ind1 + 1);
        } else action = received_message;
        Serial.print("OK " + action + " " + args + "  ");
        act(action, args);
        args = "";
        action = "";
        received_message = "";
      }
    }
  }
  double t = millis();
  if (error != 1 && (t - time_controller) > 50) {
    time_controller = t;
    ps2x.read_gamepad(false, 0);
    if (ps2x.ButtonReleased(PSB_START)) {
      mode = 1 - mode;
      if (mode == 0) {
        move(0, 0);
        digitalWrite(25, LOW);
      } else {
        digitalWrite(25, HIGH);
      }
      //Serial.println(mode == 1 ? "on" : "off");
    }

    if (ps2x.ButtonReleased(PSB_TRIANGLE))
      manual_speed = constrain(manual_speed + 20, 0, 255);
    if (ps2x.ButtonReleased(PSB_CROSS))
      manual_speed = constrain(manual_speed - 20, 0, 255);

    if (mode == 1) {
      if (ps2x.Button(PSB_PAD_UP)) {     //will be TRUE as long as button is pressed
        move(manual_speed, manual_speed);
        //Serial.println("Forward");
      } else {
        if (ps2x.Button(PSB_PAD_DOWN)) {
          move(-manual_speed, -manual_speed);
          //Serial.println("Backward");
        }
        else {
          if (ps2x.Button(PSB_PAD_LEFT)) {
            move(-manual_speed, manual_speed);
            //Serial.println("Left");
          } else {
            if (ps2x.Button(PSB_PAD_RIGHT)) {
              move(manual_speed, -manual_speed);
              //Serial.println("Right");
            } else {
              move(0, 0);
            }
          }
        }
      }
    }
  }
  accelerate();
  motors();
  Serial.println(String(s1) + " " + String(s2) + " " + String(s3) + " " + String(s4) + " " + String(s5) + " " + String(s6));
}
