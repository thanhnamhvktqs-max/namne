/*
 * Pulse_gen.h
 *
 *  Created on: Sep 20, 2026
 *      Author: Legion
 */

#ifndef INC_PULSE_GEN_H_
#define INC_PULSE_GEN_H_


#include "main.h"

typedef struct {
    uint8_t  valid;       /* 1 = dang phat xung                     */
    uint32_t period_ns;   /* chu ky T, don vi ns                    */
    uint32_t width_ns;    /* do rong xung Tw (muc cao), don vi ns   */
    uint32_t freq_x10;    /* tan so, don vi 0,1 Hz                  */
    uint16_t duty_x10;    /* he so lap day, don vi 0,1 %            */
} PulseData_t;

/* Khoi tao / chon che do co san */
void        PulseGen_Start(void);            /* goi sau MX_TIM1_Init()   */
void        PulseGen_Next(void);             /* che do ke tiep           */
void        PulseGen_Prev(void);             /* che do truoc do          */
void        PulseGen_Select(uint8_t idx);

/* Dieu khien tu ban phim */
void        PulseGen_SetPeriodUs(uint32_t us);  /* chu ky, giu nguyen he so lap day */
void        PulseGen_SetFreq(uint32_t hz);      /* tan so, giu nguyen he so lap day */
void        PulseGen_SetWidthUs(uint32_t us);   /* giu nguyen chu ky        */
void        PulseGen_StepDuty(int16_t delta_x10);
void        PulseGen_SetOutput(uint8_t on);

/* ===================== Che do CHUM XUNG (burst) ======================== */
/*  Xung con chay lien tuc o 1 kHz, nhung chi duoc phat ra thanh tung chum:
 *
 *      |<Tk>|
 *      __    __    __                        __    __    __
 *     |  |__|  |__|  |______________________|  |__|  |__|  |__________
 *      |<-TLx->|
 *      |<---- T chum ---->|
 *      |<------------- T Lc (chu ky chum) ------------->|
 *
 *      Tk    do rong xung con : 150..300 us, buoc 10 us
 *      TLx   chu ky xung con  : 1 ms co dinh
 *      TLc   chu ky chum      : 100..1000 ms, buoc 100 ms
 *      Tchum do rong chum     : 20..50 % cua TLc
 */
#define BURST_WIDTH_MIN_US     150u
#define BURST_WIDTH_MAX_US     300u
#define BURST_WIDTH_STEP_US     10u
#define BURST_PERIOD_MIN_MS    100u
#define BURST_PERIOD_MAX_MS   1000u
#define BURST_PERIOD_STEP_MS   100u
#define BURST_DUTY_MIN_PCT      20u
#define BURST_DUTY_MAX_PCT      50u
#define BURST_DUTY_STEP_PCT      5u

/* Chu ky xung con: co dinh 1 ms, khong co phim nao chinh. Doi gia tri nay
   neu muon mot chu ky xung con khac.                                     */
#define BURST_SUBPERIOD_US    1000u

void     PulseGen_BurstEnable(uint8_t on);   /* bat / tat che do chum     */
uint8_t  PulseGen_IsBurst(void);

/* MOI GIA TRI NHAP DEU THEO DON VI us, cho thong nhat tren ban phim.
   Ba ham Set tra ve ma loi. Khi co loi, ham KHONG thay doi gi ca - gia
   tri truoc do van giu nguyen va ngo ra xung khong bi anh huong.        */
#define PG_OK             0u   /* hop le, da ap dung                    */
#define PG_ERR_ZERO       1u   /* gia tri bang 0 (hoac < 1 ms voi Tch/TLc) */
#define PG_ERR_GE_PERIOD  2u   /* do rong >= chu ky tuong ung           */

uint8_t  PulseGen_BurstSetWidthUs(uint32_t us);   /* Tk  : phai < TLx     */
uint8_t  PulseGen_BurstSetPeriodUs(uint32_t us);  /* TLc : phai > Tch     */
uint8_t  PulseGen_BurstSetOnUs(uint32_t us);      /* Tch : phai < TLc     */

void     PulseGen_BurstStepWidth(int16_t delta_us);   /* Tk  buoc us      */
void     PulseGen_BurstStepOn(int16_t delta_pct);     /* Tch buoc % cua TLc */

uint16_t PulseGen_BurstGetWidthUs(void);      /* Tk,  us  */
uint16_t PulseGen_BurstGetSubPeriodUs(void);  /* TLx, us  */
uint16_t PulseGen_BurstGetOnMs(void);         /* Tch, ms  */
uint16_t PulseGen_BurstGetPeriodMs(void);     /* TLc, ms  */
uint8_t  PulseGen_BurstGetDutyPct(void);      /* Tch/TLc, % - suy ra */

/* Goi tu ngat TIM2, dung mot lan moi mili giay. Chinh ham nay cat chum. */
void     PulseGen_BurstTick(void);

/* Doc trang thai */
uint8_t     PulseGen_GetIndex(void);
uint8_t     PulseGen_GetCount(void);
uint8_t     PulseGen_IsOn(void);
uint8_t     PulseGen_IsCustom(void);   /* 1 = da chinh tay, khong con theo che do */
const char *PulseGen_GetName(void);
void        PulseGen_GetData(PulseData_t *out);

#endif /* INC_PULSE_GEN_H_ */
