#include "ch32fun.h"
#include <stdio.h>

#define PIN_LED PC1

int main()
{
  SystemInit();

  funGpioInitC();
  funPinMode(PIN_LED, GPIO_Speed_10MHz | GPIO_CNF_OUT_PP);

  while(true) {
    funDigitalWrite(PIN_LED, FUN_HIGH);
    Delay_Ms(400);
    funDigitalWrite(PIN_LED, FUN_LOW);
    Delay_Ms(400);
  }
}