/*
 * Run_timer.h
 *
 *  Created on: Sep 20, 2026
 *      Author: Legion
 */

#ifndef INC_RUN_TIMER_H_
#define INC_RUN_TIMER_H_


#include "main.h"

#define TIMER_MAX_MIN   999u      /* gioi han tren khi nhap tu ban phim */

void     Timer_SetMinutes(uint32_t minutes);   /* 0 = phat lien tuc      */
uint32_t Timer_GetMinutes(void);

void     Timer_Start(void);       /* nap lai va bat dau dem nguoc        */
void     Timer_Stop(void);

uint8_t  Timer_IsRunning(void);   /* 1 = dang dem nguoc                  */
uint32_t Timer_RemainSec(void);   /* so giay con lai                     */

/* Goi tu ngat TIM2, dung mot lan moi giay */
void     Timer_Tick1s(void);

/* Tra ve 1 DUNG MOT LAN, ngay tai vong lap phat hien dong ho vua het gio.
   Doc xong co tu dong bi xoa.                                           */
uint8_t  Timer_PollExpired(void);
#endif /* INC_RUN_TIMER_H_ */
