#include "ch32fun.h"
#include <stdio.h>

#define PIN_LED PC1

int8_t off_max_reverse;   // offset from base_max_reverse
int8_t off_min_reverse;   // offset from base_min_reverse
int8_t off_min_forward;   // offset from base_min_forward
int8_t off_max_forward;   // offset from base_max_forward

void setup_servo()
{
  // Enable GPIOC and TIM1 clocks
  RCC->APB2PCENR |= RCC_APB2Periph_GPIOC | RCC_APB2Periph_TIM1;

  // PC4 is TIM1_CH4 (alternate function, push-pull)
  funPinMode(PC4, GPIO_Speed_10MHz | GPIO_CNF_OUT_PP_AF);
  funPinMode(PC2, GPIO_Speed_10MHz | GPIO_CNF_OUT_PP);

  // Timer 1: reset to a clean state
  RCC->APB2PRSTR |= RCC_APB2Periph_TIM1;
  RCC->APB2PRSTR &= ~RCC_APB2Periph_TIM1;

  // Configure timing (assuming 24MHz clock):
  // Prescaler divide by 24, 1 tick is 1us (1MHz). 1000 ticks per 1ms. Servo frame is 20ms.
  TIM1->PSC = 24 - 1;
  TIM1->ATRLR = 20000 - 1;

  // Timer 1: enable ARR preload, emit update event
  TIM1->CTLR1 = TIM_ARPE;
  TIM1->SWEVGR |= TIM_UG;

  // Channel 4: active high, enable output
  TIM1->CCER &= ~(TIM_CC4P);
  TIM1->CCER |= TIM_CC4E;

  // Channel 4: PWM Mode 1 (high below threshold), enable preload
  TIM1->CHCTLR2 &= ~(TIM_OC4M | TIM_OC4PE);
  TIM1->CHCTLR2 |= (TIM_OC4M_2 | TIM_OC4M_1 | TIM_OC4PE);

  // Timer 1: enable output, start the timer
  TIM1->BDTR |= TIM_MOE;
  TIM1->CTLR1 |= TIM_CEN;
}

// Set continuous-rotation SG90 servo speed.
// speed: -127 .. +127 (0 = stop, positive = forward, negative = reverse)
// neutral_us: calibrated neutral pulse width (typically 1500 us)
//
// NOTE:
//   * This version uses float math for clarity.
//   * CH32V003 has no FPU, so this is slower.
//   * We will replace this with integer math later.
//
void set_servo_speed(int8_t speed, uint16_t neutral_us)
{
  // Clamp speed to symmetric range.
  if (speed < -127) speed = -127;
  if (speed >  127) speed =  127;

  // Convert speed to a pulse width offset.
  //
  // Full forward/reverse range is 500 us:
  //     neutral_us = 1500 us
  //     max forward = 2000 us
  //     max reverse = 1000 us
  //
  // Each step is:
  //     500 us / 127 ≈ 3.937 us per speed unit
  //
  // Using float here for clarity. Will replace with integer math later.
  float scale = 500.0f / 127.0f;   // ≈ 3.937 us per step

  // Compute pulse width in microseconds.
  float pulse_f = (float)neutral_us + ((float)speed * scale);

  // Clamp to safe servo range.
  if (pulse_f < 1000.0f) pulse_f = 1000.0f;
  if (pulse_f > 2000.0f) pulse_f = 2000.0f;

  // Convert to integer microseconds.
  uint16_t pulse_us = (uint16_t)(pulse_f + 0.5f); // round to nearest

  // 1 tick = 1 us
  TIM1->CH4CVR = pulse_us;
}

void set_servo_speed_float(int8_t speed,
                           int8_t off_max_reverse,
                           int8_t off_min_reverse,
                           int8_t off_min_forward,
                           int8_t off_max_forward)
{
  // TODO: Cache
  uint16_t max_reverse = 1000 + off_max_reverse;
  uint16_t min_reverse = 1450 + off_min_reverse;
  uint16_t min_forward = 1550 + off_min_forward;
  uint16_t max_forward = 2000 + off_max_forward;

  // Clamp speed.
  if (speed < -127) speed = -127;
  if (speed >  127) speed =  127;

  // Deadzone.
  if (speed == 0) {
    TIM1->CH4CVR = (min_reverse + min_forward) / 2;
    return;
  }

  float pulse_f;

  if (speed < 0) {
    // Reverse: -127..-1 → max_reverse..min_reverse
    float t = (float)(-speed) / 127.0f;
    pulse_f = (float)min_reverse + t * (float)(max_reverse - min_reverse);
  } else {
    // Forward: +1..+127 → min_forward..max_forward
    float t = (float)speed / 127.0f;
    pulse_f = (float)min_forward + t * (float)(max_forward - min_forward);
  }

  // Clamp for safety.
  if (pulse_f < max_reverse) pulse_f = max_reverse;
  if (pulse_f > max_forward) pulse_f = max_forward;

  TIM1->CH4CVR = (uint16_t)(pulse_f + 0.5f);
}

void set_servo_speed_int(int8_t speed,
                         int8_t off_max_reverse,
                         int8_t off_min_reverse,
                         int8_t off_min_forward,
                         int8_t off_max_forward)
{
  // Compute calibrated pulse widths.
  uint16_t max_reverse = 1000 + off_max_reverse;
  uint16_t min_reverse = 1470 + off_min_reverse;
  uint16_t min_forward = 1530 + off_min_forward;
  uint16_t max_forward = 2000 + off_max_forward;

  // Clamp speed.
  if (speed < -127) speed = -127;
  if (speed >  127) speed =  127;

  // Deadzone.
  if (speed == 0) {
    TIM1->CH4CVR = (min_reverse + min_forward) / 2;
    return;
  }

  int32_t pulse_us;

  if (speed < 0) {
    // Reverse: -127..-1 → max_reverse..min_reverse
    int16_t s = -speed;  // 1..127
    int32_t range = (int32_t)(max_reverse - min_reverse);
    pulse_us = min_reverse + (range * s) / 127;
  } else {
    // Forward: +1..+127 → min_forward..max_forward
    int16_t s = speed;   // 1..127
    int32_t range = (int32_t)(max_forward - min_forward);
    pulse_us = min_forward + (range * s) / 127;
  }

  // Clamp for safety.
  if (pulse_us < max_reverse) pulse_us = max_reverse;
  if (pulse_us > max_forward) pulse_us = max_forward;

  TIM1->CH4CVR = (uint16_t)pulse_us;
}

int main()
{
  SystemInit();
  Delay_Ms(100);

  setup_servo();
  uint16_t neutral_us = 1500;

  funDigitalWrite(PC2, FUN_HIGH);
  set_servo_speed_int(1, 0, 0, 0, 0);
  Delay_Ms(1000);

  funDigitalWrite(PC2, FUN_LOW);
  set_servo_speed_int(32, 0, 0, 0, 0);
  Delay_Ms(1000);

  funDigitalWrite(PC2, FUN_HIGH);
  set_servo_speed_int(64, 0, 0, 0, 0);
  Delay_Ms(1000);

  funDigitalWrite(PC2, FUN_LOW);
  set_servo_speed_int(96, 0, 0, 0, 0);
  Delay_Ms(1000);

  funDigitalWrite(PC2, FUN_HIGH);
  set_servo_speed_int(127, 0, 0, 0, 0);
  Delay_Ms(1000);

  funDigitalWrite(PC2, FUN_LOW);
  set_servo_speed_int(-127, 0, 0, 0, 0);
  Delay_Ms(1000);

  funDigitalWrite(PC2, FUN_HIGH);
  set_servo_speed_int(127, 0, 0, 0, 0);
  Delay_Ms(1000);

  funDigitalWrite(PC2, FUN_LOW);
  set_servo_speed_int(0, 0, 0, 0, 0);
  Delay_Ms(1000);

  funDigitalWrite(PC2, FUN_HIGH);
  set_servo_speed_int(127, 0, 0, 0, 0);
  Delay_Ms(1000);

  funDigitalWrite(PC2, FUN_LOW);
  set_servo_speed_int(-127, 0, 0, 0, 0);
  Delay_Ms(5000);

  funDigitalWrite(PC2, FUN_HIGH);
  while (1) {}

  while(true) {
    /*
    set_servo_speed(0, neutral_us);
    Delay_Ms(500);
    set_servo_speed(64, neutral_us);
    Delay_Ms(500);
    set_servo_speed(127, neutral_us);
    Delay_Ms(500);
    set_servo_speed(64, neutral_us);
    Delay_Ms(500);
    set_servo_speed(0, neutral_us);
    Delay_Ms(500);
    set_servo_speed(-64, neutral_us);
    Delay_Ms(500);
    set_servo_speed(-127, neutral_us);
    Delay_Ms(500);
    set_servo_speed(-64, neutral_us);
    Delay_Ms(500);
    */
    /*
    set_servo_speed_float(0, 0, 0, 0, 0);
    Delay_Ms(500);
    set_servo_speed_float(64, 0, 0, 0, 0);
    Delay_Ms(500);
    set_servo_speed_float(127, 0, 0, 0, 0);
    Delay_Ms(500);
    set_servo_speed_float(64, 0, 0, 0, 0);
    Delay_Ms(500);
    set_servo_speed_float(0, 0, 0, 0, 0);
    Delay_Ms(500);
    set_servo_speed_float(-64, 0, 0, 0, 0);
    Delay_Ms(500);
    set_servo_speed_float(-127, 0, 0, 0, 0);
    Delay_Ms(500);
    set_servo_speed_float(-64, 0, 0, 0, 0);
    Delay_Ms(500);
    */
    set_servo_speed_int(0, 0, 0, 0, 0);
    Delay_Ms(500);
    set_servo_speed_int(64, 0, 0, 0, 0);
    Delay_Ms(500);
    set_servo_speed_int(127, 0, 0, 0, 0);
    Delay_Ms(500);
    set_servo_speed_int(64, 0, 0, 0, 0);
    Delay_Ms(500);
    set_servo_speed_int(0, 0, 0, 0, 0);
    Delay_Ms(500);
    set_servo_speed_int(-64, 0, 0, 0, 0);
    Delay_Ms(500);
    set_servo_speed_int(-127, 0, 0, 0, 0);
    Delay_Ms(500);
    set_servo_speed_int(-64, 0, 0, 0, 0);
    Delay_Ms(500);
  }
}