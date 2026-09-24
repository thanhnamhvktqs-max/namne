/*
 * Run_timer.c
 *
 *  Created on: Sep 20, 2026
 *      Author: Legion
 */


#include "Run_timer.h"

static uint32_t          s_minutes   = 0;   /* 0 = phat lien tuc          */
static volatile uint32_t s_remainSec = 0;   /* so giay con lai            */
static volatile uint8_t  s_running   = 0;
static volatile uint8_t  s_expired   = 0;

void Timer_SetMinutes(uint32_t minutes)
{
    if (minutes > TIMER_MAX_MIN) minutes = TIMER_MAX_MIN;
    s_minutes = minutes;

    /* Dang dem ma doi so phut thi nap lai tu dau */
    if (s_running) Timer_Start();
}

uint32_t Timer_GetMinutes(void)
{
    return s_minutes;
}

void Timer_Start(void)
{
    uint32_t primask;

    if (s_minutes == 0u) {          /* lien tuc -> khong dem nguoc */
        s_running = 0;
        return;
    }

    /* Giu nguyen trang thai cam ngat cu khi thoat ra (xem Timebase.c) */
    primask = __get_PRIMASK();
    __disable_irq();
    s_remainSec = s_minutes * 60u;
    s_expired   = 0;
    s_running   = 1;
    __set_PRIMASK(primask);
}

void Timer_Stop(void)
{
    s_running = 0;
}

uint8_t Timer_IsRunning(void)
{
    return s_running;
}

uint32_t Timer_RemainSec(void)
{
    return s_running ? s_remainSec : 0u;
}

/* Duoc ngat TIM2 goi dung mot lan moi giay */
void Timer_Tick1s(void)
{
    if (!s_running) return;

    if (s_remainSec > 0u) {
        s_remainSec--;
        if (s_remainSec == 0u) {
            s_running = 0;
            s_expired = 1;          /* vong lap chinh se cat ngo ra xung */
        }
    }
}

uint8_t Timer_PollExpired(void)
{
    uint32_t primask = __get_PRIMASK();
    uint8_t  e;

    __disable_irq();
    e         = s_expired;
    s_expired = 0;
    __set_PRIMASK(primask);

    return e;
}
