#include "ch32fun.h"
#include <stdio.h>

#define PIN_LED PC1

int main()
{
  SystemInit();
  Delay_Ms(100);

  // Enable GPIO C and TIM1
  RCC->APB2PCENR |= RCC_APB2Periph_GPIOC | RCC_APB2Periph_TIM1;

  // Set PC4 to alternate function output for TIM1_CH4
  funPinMode(PC4, GPIO_Speed_10MHz | GPIO_CNF_OUT_PP_AF);

  // Reset TIM1
  RCC->APB2PRSTR |= RCC_APB2Periph_TIM1;
  RCC->APB2PRSTR &= ~RCC_APB2Periph_TIM1;

  // Set values, enable preload, emit change event
  // TODO: Review how to compute these values for different frequencies and duty cycles.
  TIM1->PSC = 0;
  TIM1->ATRLR = 2048 - 1;
  TIM1->CTLR1 = TIM_ARPE;
  TIM1->SWEVGR |= TIM_UG;

  // Enable TIM1_CH4
  TIM1->CCER |= TIM_CC4E | TIM_CC4P; // Active low
  TIM1->CHCTLR2 |= TIM_OC4M_2 | TIM_OC4M_1 | TIM_OC4PE;

  TIM1->CH4CVR = 0;
  TIM1->BDTR |= TIM_MOE;
  TIM1->CTLR1 |= TIM_CEN;

  // We're moving within [1, arr-1] to avoid the weird behavior of 0 and arr.
  uint32_t arr = (TIM1->ATRLR + 1) / 8;
  uint32_t count = 1;
  bool up = true;
  while(true) {
    TIM1->CH4CVR = count;
    if (up) {
      if (++count >= (arr-1)) up = false;
    } else {
      if (count-- <= 1) up = true;
    }
    Delay_Ms(5);
  }
}