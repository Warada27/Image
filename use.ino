#include <STM32TimerInterrupt.h>
#include <STM32_ISR_Timer.h>
#define TIMER_INTERVAL_MS 100
#define HW_TIMER_INTERVAL_MS 50

STM32Timer ITimer(TIM1);
STM32_ISR_Timer ISR_Timer;

#define TIMER_INTERVAL_20ms 20L
#define TIMER_INTERVAL_0_5S 500L
#define TIMER_INTERVAL_1S 1000L
#define TIMER_INTERVAL_1_5S 1500L

void TimerHandler() {
  ISR_Timer.run();
}

// Pin Definitions
#define IN1 PA2
#define IN2 PA1
#define ENA PA5

#define IN3 PB2
#define IN4 PB1
#define ENB PB0

#define LED PC13
#define TIM3_CH1 PA6
#define TIM3_CH2 PA7
#define TIM4_CH1 PB6
#define TIM4_CH2 PB7

// Motor Control Variables
volatile float Vel_R = -200;
volatile float Vel_L = -200;

// Right Motor
float setpoint_R = 2;
float error_R = 0;
float Kp_R = 70;
float Ki_R = 0.8;
float Kd_R = 0;

float sum_R = 0;
float prevError_R = 0;

float speed_R = 0;
float prevSpeed_R = 0;
float PWMvalue_R = 0;

// ========= End Motor R ===========

float setpoint_L = 2;
float error_L = 0;
float Kp_L = 70;
float Ki_L = 0.8;
float Kd_L = 0;

float sum_L = 0;
float prevError_L = 0;

HardwareTimer *timer3;
HardwareTimer *timer4;

void driveMotor();
void timer3Int();
void timer4Int();

void setup() {
  Serial.begin(115200);
  pinMode(LED, OUTPUT);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);

  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);

  pinMode(TIM3_CH1, INPUT);
  pinMode(TIM3_CH2, INPUT);
  pinMode(TIM4_CH1, INPUT);
  pinMode(TIM4_CH2, INPUT);

  // Timer Configuration
  timer3 = new HardwareTimer(TIM3);
  timer4 = new HardwareTimer(TIM4);

  // Attach interrupt
  timer3->attachInterrupt(timer3Int);
  timer4->attachInterrupt(timer4Int);

  // Start timers
  timer3->resume();
  timer4->resume();

  // Start ITimer
  if (ITimer.attachInterruptInterval(HW_TIMER_INTERVAL_MS * 1000, TimerHandler)) {
    Serial.println("ITimer started");
  } else {
    Serial.println("Failed to start ITimer");
  }

  ISR_Timer.setInterval(TIMER_INTERVAL_20ms, driveMotor);
}

void loop() {
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');
    int separatorIndex = message.indexOf(',');

    if (separatorIndex != -1) {
      Vel_R = message.substring(0, separatorIndex).toInt();
      Vel_L = message.substring(separatorIndex + 1).toInt();
    }

    delay(50);
  }
}

void driveMotor() {
  float pulse_per_sec_R = Vel_R * 20; 
  float pulse_per_sec_L = Vel_L * 20;

  error_R = pulse_per_sec_R - sum_R;
  error_L = pulse_per_sec_L - sum_L;

  sum_R += error_R;
  sum_L += error_L;

  // Anti-windup mechanism for integral term
  sum_R = constrain(sum_R, -500, 500);
  sum_L = constrain(sum_L, -500, 500);

  float PWMvalue_R = Kp_R * error_R + Ki_R * sum_R;
  float PWMvalue_L = Kp_L * error_L + Ki_L * sum_L;

  // Motor direction control
  digitalWrite(IN1, PWMvalue_R > 0 ? HIGH : LOW);
  digitalWrite(IN2, PWMvalue_R > 0 ? LOW : HIGH);
  digitalWrite(IN3, PWMvalue_L > 0 ? HIGH : LOW);
  digitalWrite(IN4, PWMvalue_L > 0 ? LOW : HIGH);

  PWMvalue_R = abs(PWMvalue_R);
  PWMvalue_L = abs(PWMvalue_L);

  PWMvalue_R = constrain(PWMvalue_R, 0, 100);
  PWMvalue_L = constrain(PWMvalue_L, 0, 100);

  analogWrite(ENA, (int)PWMvalue_R);
  analogWrite(ENB, (int)PWMvalue_L);
}

void timer3Int() {
  digitalWrite(LED, !digitalRead(LED));
}

void timer4Int() {
  digitalWrite(LED, !digitalRead(LED));
}
