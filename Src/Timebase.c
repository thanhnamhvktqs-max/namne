/*
 * Timebase.c
 *
 *  Created on: Sep 20, 2026
 *      Author: Legion
 */


#include "Timebase.h"
#include "Run_timer.h"
#include "Pulse_gen.h"

/* htim2 duoc DINH NGHIA trong main.c (do CubeMX sinh ra). O day chi dung
   lai - Timebase.h da co "extern TIM_HandleTypeDef htim2;".
   Neu khai bao them "TIM_HandleTypeDef htim2;" o day thi trinh lien ket
   bao loi "multiple definition of htim2" (gcc >= 10 mac dinh -fno-common). */

static volatile uint32_t s_ms      = 0;   /* bo dem mili giay          */
static volatile uint16_t s_div20   = 0;   /* chia tan de lay nhip 20 ms */
static volatile uint16_t s_div1000 = 0;   /* chia tan de lay nhip 1 s   */
static volatile uint8_t  s_f20ms   = 0;
static volatile uint8_t  s_f1s     = 0;

void Timebase_Init(void)
{
    TIM_ClockConfigTypeDef  sClockSourceConfig = {0};
    TIM_MasterConfigTypeDef sMasterConfig      = {0};

    htim2.Instance               = TIM2;
    htim2.Init.Prescaler         = 83;      /* 84 MHz / 84 = 1 MHz -> 1 us */
    htim2.Init.CounterMode       = TIM_COUNTERMODE_UP;
    htim2.Init.Period            = 999;     /* 1000 us = 1 ms              */
    htim2.Init.ClockDivision     = TIM_CLOCKDIVISION_DIV1;
    htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
    if (HAL_TIM_Base_Init(&htim2) != HAL_OK) {
        Error_Handler();
    }

    sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
    if (HAL_TIM_ConfigClockSource(&htim2, &sClockSourceConfig) != HAL_OK) {
        Error_Handler();
    }

    sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
    sMasterConfig.MasterSlaveMode     = TIM_MASTERSLAVEMODE_DISABLE;
    if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK) {
        Error_Handler();
    }

    HAL_TIM_Base_Start_IT(&htim2);          /* chay va bat ngat Update */
}

/* --------------------------- Ngat cua TIM2 ----------------------------- */
/* HAL_TIM_IRQHandler() goi vao day moi khi TIM2 tran (1 ms mot lan).
   TIM1 khong bat ngat Update nen callback nay chi phuc vu TIM2.          */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if (htim->Instance != TIM2) return;

    s_ms++;

    /* Cat chum xung. Phai lam ngay o day chu khong the doi vong lap chinh:
       bien chum can do phan giai 1 ms, trong khi vong lap chay 20 ms mot
       nhip - chum ngan nhat chi rong 20 ms nen se sai hoan toan.         */
    PulseGen_BurstTick();

    if (++s_div20 >= 20u) {                 /* nhip 20 ms */
        s_div20 = 0;
        s_f20ms = 1;
    }

    if (++s_div1000 >= 1000u) {             /* nhip 1 giay */
        s_div1000 = 0;
        s_f1s     = 1;
        Timer_Tick1s();                     /* TIM2 chinh la bo dem gio */
    }
}

/* ------------------------- Doc nhip / doc co --------------------------- */
uint32_t Timebase_GetMs(void)
{
    return s_ms;        /* doc 32 bit tren Cortex-M la mot lenh, an toan */
}

/* Cam ngat co nho lai trang thai cu: neu ham duoc goi khi ngat DANG bi cam
   thi luc thoat ra van phai giu nguyen trang thai cam, khong duoc mo bua. */
uint8_t Timebase_Poll20ms(void)
{
    uint32_t primask = __get_PRIMASK();
    uint8_t  f;

    __disable_irq();
    f       = s_f20ms;
    s_f20ms = 0;
    __set_PRIMASK(primask);

    return f;
}

uint8_t Timebase_Poll1s(void)
{
    uint32_t primask = __get_PRIMASK();
    uint8_t  f;

    __disable_irq();
    f     = s_f1s;
    s_f1s = 0;
    __set_PRIMASK(primask);

    return f;
}
