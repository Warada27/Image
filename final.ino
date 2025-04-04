#include <STM32TimerInterrupt.h>
#include <STM32_ISR_Timer.h>

#define TIMER_INTERVAL_20ms 20L
#define HW_TIMER_INTERVAL_MS 50

STM32Timer ITimer(TIM1);
STM32_ISR_Timer ISR_Timer;

// Pins
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
// #define TIM3_CH1 PB6
// #define TIM3_CH2 PB7
// #define TIM4_CH1 PA6
// #define TIM4_CH2 PA7

// Motor control
volatile float Vel_R = 0;
volatile float Vel_L = 0;

float Kp = 70;
float Ki = 0.8;

float sum_R = 0;
float sum_L = 0;

float prevEnc_R = 0;
float prevEnc_L = 0;

HardwareTimer *timer3 = new HardwareTimer(TIM3);
HardwareTimer *timer4 = new HardwareTimer(TIM4);

void TimerHandler() {
  ISR_Timer.run();
}

void setupMotorPins() {
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(LED, OUTPUT);
}

void setupEncoderWithRegister() {
  // TIM3 (PA6, PA7)
  GPIOA->AFR[0] = (GPIOA->AFR[0] & ~(0xF << (4 * 6))) | (2 << (4 * 6));    // PA6 AF2
  GPIOA->AFR[0] = (GPIOA->AFR[0] & ~(0xF << (4 * 7))) | (2 << (4 * 7));    // PA7 AF2
  GPIOA->MODER = (GPIOA->MODER & ~(0b11 << (2 * 6))) | (0b10 << (2 * 6));  // Alt func
  GPIOA->MODER = (GPIOA->MODER & ~(0b11 << (2 * 7))) | (0b10 << (2 * 7));

  // TIM4 (PB6, PB7)
  GPIOB->AFR[0] = (GPIOB->AFR[0] & ~(0xF << (4 * 6))) | (2 << (4 * 6));  // PB6 AF2
  GPIOB->AFR[0] = (GPIOB->AFR[0] & ~(0xF << (4 * 7))) | (2 << (4 * 7));  // PB7 AF2
  GPIOB->MODER = (GPIOB->MODER & ~(0b11 << (2 * 6))) | (0b10 << (2 * 6));
  GPIOB->MODER = (GPIOB->MODER & ~(0b11 << (2 * 7))) | (0b10 << (2 * 7));

  // ตั้ง TIM3 ให้เป็น encoder mode
  TIM3->CCMR1 = (1 << 0) | (1 << 8);       // CC1S=01, CC2S=01
  TIM3->SMCR = (TIM3->SMCR & ~0x7) | 0x3;  // SMS=011 = encoder mode
  TIM3->CCER = 0;                          // ไม่ invert
  TIM3->ARR = 0xFFFF;
  TIM3->CNT = 0;
  TIM3->CR1 |= 1;  // Enable

  // ตั้ง TIM4 เหมือนกัน
  TIM4->CCMR1 = (1 << 0) | (1 << 8);
  TIM4->SMCR = (TIM4->SMCR & ~0x7) | 0x3;
  TIM4->CCER = 0;
  TIM4->ARR = 0xFFFF;
  TIM4->CNT = 0;
  TIM4->CR1 |= 1;
}

void setup() {
  Serial.begin(115200);
  setupMotorPins();
  setupEncoderWithRegister();

  // Start timer interrupt every 20ms
  if (ITimer.attachInterruptInterval(HW_TIMER_INTERVAL_MS * 1000, TimerHandler)) {
    Serial.println("ITimer started");
  } else {
    Serial.println("Failed to start ITimer");
  }

  ISR_Timer.setInterval(TIMER_INTERVAL_20ms, driveMotor);
}

void loop() {
  if (Serial.available()) {
    String msg = Serial.readStringUntil('\n');
    int idx = msg.indexOf(',');
    if (idx != -1) {
      Vel_L = msg.substring(0, idx).toFloat();
      Vel_R = msg.substring(idx + 1).toFloat();

      if (Vel_R == 0) timer3->setCount(0);
      if (Vel_L == 0) timer4->setCount(0);

      if (Vel_R == 0 && Vel_L == 0) {
        analogWrite(ENA, 0);
        analogWrite(ENB, 0);
        digitalWrite(IN1, LOW);
        digitalWrite(IN2, LOW);
        digitalWrite(IN3, LOW);
        digitalWrite(IN4, LOW);
        return;
      }
    }
    delay(30);
  }
}

float pwm_L = 0;
float pwm_R = 0;

void driveMotor() {
  digitalWrite(LED, !digitalRead(LED));

  const float GearRatio = 20.0;
  const float PulsesPerRev = 44.0;
  const float WheelDiaMM = 65.0;
  const float LoopFreq = 100.0;

  float pulsesPerMM = (GearRatio * PulsesPerRev) / (WheelDiaMM * 3.1416);

  float targetEncChange_R = Vel_R * pulsesPerMM / LoopFreq;
  float targetEncChange_L = Vel_L * pulsesPerMM / LoopFreq;

  // float currEnc_R = timer4->getCount();
  // float currEnc_L = timer3->getCount();
  float currEnc_R = 0;
  float currEnc_L = 0;

  float delta_R = currEnc_R - prevEnc_R;
  float delta_L = currEnc_L - prevEnc_L;

  // // ✅ Force stop motor L
  // if (Vel_L == 0) {
  //   analogWrite(ENB, 0);
  //   digitalWrite(IN3, LOW);
  //   digitalWrite(IN4, LOW);
  //   sum_L = 0;
  //   // timer4->setCount(0);
  //   prevEnc_L = 0;
  //   pwm_L = 0;
  // }

  // // ✅ Force stop motor R
  // if (Vel_R == 0) {
  //   analogWrite(ENA, 0);
  //   digitalWrite(IN1, LOW);
  //   digitalWrite(IN2, LOW);
  //   sum_R = 0;
  //   // timer3->setCount(0);
  //   prevEnc_R = 0;
  //   pwm_R = 0;
  // }

  // ===== R PID =====
  if (Vel_R != 0) {
    float error_R = targetEncChange_R - delta_R;
    sum_R += error_R;
    sum_R = constrain(sum_R, -500, 500);
    pwm_R = Kp * error_R + Ki * sum_R;

    if (pwm_R >= 0) {
      digitalWrite(IN1, LOW);
      digitalWrite(IN2, HIGH);
    } else {
      digitalWrite(IN1, HIGH);
      digitalWrite(IN2, LOW);
      pwm_R = -pwm_R;
    }

    pwm_R = constrain(pwm_R, 0, 1000);
    analogWrite(ENA, map(pwm_R, 0, 1000, 0, 120));
    Serial.print("ENA -> ");
    Serial.println(map(pwm_R, 0, 1000, 0, 255));
  }

  // ===== L PID =====
  if (Vel_L != 0) {
    float error_L = targetEncChange_L - delta_L;
    sum_L += error_L;
    sum_L = constrain(sum_L, -500, 500);
    pwm_L = Kp * error_L + Ki * sum_L;

    if (pwm_L >= 0) {
      digitalWrite(IN3, HIGH);
      digitalWrite(IN4, LOW);
    } else {
      digitalWrite(IN3, LOW);
      digitalWrite(IN4, HIGH);
      pwm_L = -pwm_L;
    }

    pwm_L = constrain(pwm_L, 0, 1000);
    analogWrite(ENB, map(pwm_L, 0, 1000, 0, 120));
    Serial.print("ENB -> ");
    Serial.println(map(pwm_L, 0, 1000, 0, 255));
  }

  // Update encoder tracking
  prevEnc_R = currEnc_R;
  prevEnc_L = currEnc_L;

  // Debug
  Serial.print("Vel_L: ");
  Serial.print(Vel_L, 2);
  Serial.print(" | Target: ");
  Serial.print(targetEncChange_L, 2);
  Serial.print(" | pwm_L: ");
  Serial.print(pwm_L);
  Serial.print(" | TIM4 raw count: ");
  Serial.print(currEnc_L, 2);

  Serial.print(" || Vel_R: ");
  Serial.print(Vel_R, 2);
  Serial.print(" | Target: ");
  Serial.print(targetEncChange_R, 2);
  Serial.print(" | pwm_R: ");
  Serial.print(pwm_R);
  Serial.print(" | TIM3 raw count: ");
  Serial.println(currEnc_R, 2);
}
