/*
 * Timebase.h
 *
 *  Created on: Sep 20, 2026
 *      Author: Legion
 */

#ifndef INC_TIMEBASE_H_
#define INC_TIMEBASE_H_


#include "main.h"

extern TIM_HandleTypeDef htim2;

void     Timebase_Init(void);       /* cau hinh TIM2 1 ms va bat ngat */

uint32_t Timebase_GetMs(void);      /* so mili giay tu luc khoi dong  */

/* Doc co ngat; doc xong co tu dong bi xoa (tra ve 1 dung mot lan) */
uint8_t  Timebase_Poll20ms(void);
uint8_t  Timebase_Poll1s(void);
#endif /* INC_TIMEBASE_H_ */
