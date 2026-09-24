/*
 * Pulse_gen.c
 *
 *  Created on: Sep 20, 2026
 *      Author: Legion
 */

#include "Pulse_gen.h"

extern TIM_HandleTypeDef htim1;          /* khai bao trong main.c */

#define TIM1_CLK_HZ     168000000u       /* TIM1 = 2 x APB2 = 168 MHz */
#define TICKS_PER_US    (TIM1_CLK_HZ / 1000000u)   /* = 168 */
#define PULSE_CHANNEL   TIM_CHANNEL_3    /* TIM1_CH3 -> PA10          */

#define FREQ_MIN_HZ     1u
#define FREQ_MAX_HZ     1000000u
#define PERIOD_MIN_US   1u
/* Chu ky duoc luu duoi dang nano giay trong mot bien 32 bit (PulseData_t),
   nen gia tri lon nhat bieu dien duoc la 2^32 - 1 ns = 4,294 s. Dat tran
   o 4 s de khong bao gio tran so khi hien thi.                            */
#define PERIOD_MAX_US   4000000u        /* 4 s */

/* Bang cac che do phat xung mau.
   PSC / ARR / CCR tinh lai theo clock 168 MHz (ban F103 dung 72 MHz).   */
typedef struct {
    uint16_t    psc;
    uint16_t    arr;
    uint16_t    ccr;
    const char *name;
} PulsePreset_t;

static const PulsePreset_t PRESETS[] = {
    /* PSC=7 -> 21 MHz dem : 400 Hz, Tw = 1,25 ms.
       Day la che do MAC DINH luc bat may (s_index khoi tao bang 0).
       168 MHz / 8 / 52500 = 400,0 Hz chan, khong co sai so.       */
    {     7, 52499, 26250, "400Hz  50%"  },
    /* PSC=167 -> 1 MHz dem : 1 kHz, Tw = 250 us    */
    {   167,   999,   250, "1 kHz  25%"  },
    /* PSC=167 -> 1 MHz dem : 1 kHz, Tw = 500 us    */
    {   167,   999,   500, "1 kHz  50%"  },
    /* PSC=7   -> 21 MHz dem: 10 kHz, Tw = 10 us    */
    {     7,  2099,   210, "10 kHz 10%"  },
    /* PSC=0   -> 168 MHz dem: 100 kHz, Tw = 7,5 us */
    {     0,  1679,  1260, "100kHz 75%"  },
    /* PSC=167 -> 1 MHz dem : 50 Hz, Tw = 1,5 ms (tin hieu servo) */
    {   167, 19999,  1500, "50Hz servo"  },
    /* PSC=16799 -> 10 kHz dem: 2 Hz, Tw = 250 ms   */
    { 16799,  4999,  2500, "2 Hz   50%"  }
    /* Ten che do toi da 10 ky tu: dong trang thai ve o ty le 2 (12 diem
       anh moi ky tu) chi chua duoc 19 ky tu, trong do 9 ky tu dau da
       danh cho "XUNG ON  " / "XUNG OFF ".                               */
};
#define PRESET_COUNT   (sizeof(PRESETS) / sizeof(PRESETS[0]))

static uint8_t s_index   = 0;
static uint8_t s_running = 0;   /* 1 = dang phat xung ra chan          */
static uint8_t s_custom  = 0;   /* 1 = da chinh tay bang ban phim      */

/* ===================== Lop boc thu vien HAL cho TIM1 ==================== */
/* Toan bo file nay chi lam viec voi TIM1 qua macro / ham cua HAL, khong
   dung thang thanh ghi PSC, ARR, CCR3, EGR nua.                          */

/* Doc gia tri dang nam trong thanh ghi.
   HAL co san macro doc ARR va CCR, nhung KHONG co macro doc PSC. Vi vay
   ta doc ban sao luu trong htim1.Init.Prescaler - ban sao nay luon dung
   vi Gen_SetTiming() la noi duy nhat ghi PSC.                            */
static uint32_t Gen_GetPsc1(void)
{
    return htim1.Init.Prescaler + 1u;
}

static uint32_t Gen_GetArr1(void)
{
    return __HAL_TIM_GET_AUTORELOAD(&htim1) + 1u;
}

static uint32_t Gen_GetCcr(void)
{
    return __HAL_TIM_GET_COMPARE(&htim1, PULSE_CHANNEL);
}

/* Ghi bo chia truoc va chu ky.
   Luu y: ghi xong CHUA co hieu luc ngay, phai goi Gen_Reload() sau do.   */
static void Gen_SetTiming(uint32_t psc, uint32_t arr)
{
    htim1.Init.Prescaler = psc;             /* macro duoi khong tu cap nhat */
    __HAL_TIM_SET_PRESCALER(&htim1, psc);
    __HAL_TIM_SET_AUTORELOAD(&htim1, arr);  /* macro nay tu cap nhat Init.Period */
}

/* Sinh su kien Update de nap PSC / ARR / CCR vua ghi vao thanh ghi bong.
   Can lam vi ba thanh ghi co hanh vi khac nhau:
     - ARR : ARPE dang tat nen ghi la an ngay
     - PSC : phan cung LUON dem qua thanh ghi bong, chi nap khi co Update
     - CCR : OC3PE dang bat (do HAL_TIM_PWM_ConfigChannel) nen cung co bong
   Sinh Update mot lan lam ca ba doi dong thoi, va dua bo dem ve 0.       */
static void Gen_Reload(void)
{
    HAL_TIM_GenerateEvent(&htim1, TIM_EVENTSOURCE_UPDATE);
}

/* He so lap day hien tai, don vi 0,1 % */
static uint32_t Gen_GetDutyX10(void)
{
    uint32_t arr1 = Gen_GetArr1();
    if (arr1 == 0) return 500u;
    return (Gen_GetCcr() * 1000u) / arr1;
}

/* Ghi CCR co gioi han 1..ARR (khong cho 0% va 100%) */
static void Gen_SetCcr(uint32_t ccr)
{
    uint32_t arr1 = Gen_GetArr1();
    if (ccr < 1u) ccr = 1u;
    if (ccr > arr1 - 1u) ccr = arr1 - 1u;
    __HAL_TIM_SET_COMPARE(&htim1, PULSE_CHANNEL, ccr);
}

/* Chia TONG SO NHIP thanh (PSC+1) va (ARR+1).
   Chon (PSC+1) nho nhat sao cho (ARR+1) van nam trong 16 bit -> giu duoc
   do phan giai cao nhat co the.                                          */
static void Gen_SplitTicks(uint32_t total, uint32_t *psc1, uint32_t *arr1)
{
    if (total < 2u) total = 2u;

    *psc1 = (total + 65535u) / 65536u;         /* lam tron len            */
    if (*psc1 < 1u)     *psc1 = 1u;
    if (*psc1 > 65536u) *psc1 = 65536u;

    *arr1 = total / *psc1;
    if (*arr1 < 2u)     *arr1 = 2u;
    if (*arr1 > 65536u) *arr1 = 65536u;
}

static void PulseGen_Apply(void)
{
    const PulsePreset_t *p = &PRESETS[s_index];

    Gen_SetTiming(p->psc, p->arr);
    __HAL_TIM_SET_COMPARE(&htim1, PULSE_CHANNEL, p->ccr);
    Gen_Reload();

    s_custom = 0;
}

/* --------------------------- Che do co san ---------------------------- */
void PulseGen_Start(void)
{
    PulseGen_Apply();
    HAL_TIM_PWM_Start(&htim1, PULSE_CHANNEL);   /* ham nay tu bat MOE cho TIM1 */
    s_running = 1;
}

void PulseGen_Select(uint8_t idx)
{
    if (idx >= PRESET_COUNT) idx = 0;
    s_index = idx;
    PulseGen_Apply();
}

void PulseGen_Next(void)
{
    PulseGen_Select((uint8_t)((s_index + 1u) % PRESET_COUNT));
}

void PulseGen_Prev(void)
{
    PulseGen_Select((uint8_t)((s_index + PRESET_COUNT - 1u) % PRESET_COUNT));
}

/* ------------------------ Dieu khien tu ban phim ----------------------- */
/* Dat chu ky theo TONG SO NHIP DEM, giu nguyen he so lap day. */
static void Gen_ApplyTotalTicks(uint32_t total)
{
    uint32_t psc1, arr1, duty;

    duty = Gen_GetDutyX10();                   /* nho lai duty truoc khi doi */
    Gen_SplitTicks(total, &psc1, &arr1);

    Gen_SetTiming(psc1 - 1u, arr1 - 1u);
    Gen_SetCcr((arr1 * duty) / 1000u);         /* dat lai CCR theo duty cu   */
    Gen_Reload();

    s_custom = 1;
}

/* Dat TAN SO theo Hz */
void PulseGen_SetFreq(uint32_t hz)
{
    if (hz < FREQ_MIN_HZ) hz = FREQ_MIN_HZ;
    if (hz > FREQ_MAX_HZ) hz = FREQ_MAX_HZ;

    Gen_ApplyTotalTicks(TIM1_CLK_HZ / hz);
}

/* Dat CHU KY LAP theo us (1 us .. 9 999 999 us ~ 10 s), co gang giu nguyen
   DO RONG XUNG tuyet doi - vi Tw va T la hai tham so nguoi dung dat rieng.
   Neu chu ky moi ngan hon do rong xung dang co thi do rong bi ep xuong
   con ARR (tuc gan 100% he so lap day).                                  */
void PulseGen_SetPeriodUs(uint32_t us)
{
    uint32_t total, psc1, arr1;
    uint64_t width_ns, ccr;

    if (us < PERIOD_MIN_US) us = PERIOD_MIN_US;
    if (us > PERIOD_MAX_US) us = PERIOD_MAX_US;

    /* Do rong xung hien tai, tinh ra ns de giu nguyen sau khi doi chu ky */
    width_ns = ((uint64_t)Gen_GetCcr() * Gen_GetPsc1() * 125u) / 21u;

    total = (uint32_t)(((uint64_t)us * TICKS_PER_US));   /* tong so nhip   */
    Gen_SplitTicks(total, &psc1, &arr1);

    Gen_SetTiming(psc1 - 1u, arr1 - 1u);

    /* CCR = Tw[ns] x 168 / (1000 x (PSC+1)) */
    ccr = (width_ns * TICKS_PER_US) / (1000u * (uint64_t)psc1);
    if (ccr > 0xFFFFu) ccr = 0xFFFFu;
    Gen_SetCcr((uint32_t)ccr);

    Gen_Reload();
    s_custom = 1;
}

/* Dat do rong xung theo us, giu nguyen chu ky.
   CCR = us x 168 / (PSC+1). Khong can sinh UG vi CCR co thanh ghi bong,
   gia tri moi tu dong co hieu luc o dau chu ky ke tiep (khong bi glitch). */
void PulseGen_SetWidthUs(uint32_t us)
{
    uint64_t ccr = ((uint64_t)us * TICKS_PER_US) / Gen_GetPsc1();

    if (ccr > 0xFFFFu) ccr = 0xFFFFu;
    Gen_SetCcr((uint32_t)ccr);
    s_custom = 1;
}

/* Tang / giam he so lap day, buoc tinh theo don vi 0,1 % */
void PulseGen_StepDuty(int16_t delta_x10)
{
    int32_t duty = (int32_t)Gen_GetDutyX10() + delta_x10;

    if (duty < 1)   duty = 1;
    if (duty > 999) duty = 999;

    Gen_SetCcr((Gen_GetArr1() * (uint32_t)duty) / 1000u);
    s_custom = 1;
}

/* ======================= CHE DO CHUM XUNG (burst) ====================== */
/*  Cach tao chum:
 *
 *  TIM1 van chay lien tuc o 1 kHz (chu ky xung con 1 ms). De cat chum, ta
 *  ghi CCR = 0 trong khoang nghi - o che do PWM 1, CCR = 0 nghia la ngo ra
 *  giu muc thap suot ca chu ky.
 *
 *  Diem hay: CCR co thanh ghi bong (OC3PE bat), nen gia tri moi chi co
 *  hieu luc o DAU chu ky 1 ms ke tiep. Bien chum vi vay luon roi dung vao
 *  ranh gioi giua hai xung con - khong bao gio cat ngang mot xung con.
 *
 *  Do phan giai 1 ms cua bien chum lay tu ngat TIM2 (Timebase.c).
 */
/*  Tch duoc luu THANG bang mili giay chu khong luu theo phan tram. Ly do:
 *  ban phim gio nhap moi thu bang us, neu quy qua phan tram roi quy nguoc
 *  lai thi gia tri hien len se lech so voi con so vua go.
 *  Phan tram tro thanh dai luong suy ra, chi dung de hien thi va de buoc
 *  phim mui ten.                                                         */
static uint8_t  s_burstMode  = 0;
static uint16_t s_burstWidth = BURST_WIDTH_MIN_US;   /* Tk,  us          */
static uint16_t s_burstPer   = BURST_PERIOD_MAX_MS;  /* TLc, ms          */
/* Tch mac dinh = 20 % cua TLc, tuc 200 ms */
static uint16_t s_burstOnMs  =
        (uint16_t)((BURST_PERIOD_MAX_MS * BURST_DUTY_MIN_PCT) / 100u);

static uint32_t s_burstCcr   = 0;    /* CCR ung voi Tk - tinh san cho ngat */

static volatile uint16_t s_burstMs     = 0;   /* bo dem trong chu ky chum */
static volatile uint8_t  s_burstGateOn = 0;

/* Tinh san CCR de ngat 1 ms khong phai nhan chia. Goi SAU khi PSC dung.
   Day la CHAN DUY NHAT con lai o duong nhap tay, va no la chan PHAN CUNG
   chu khong phai chan theo dai 150..300 us: CCR khong the vuot qua ARR,
   nghia la Tk khong the dai hon TLx.                                     */
static void Gen_BurstRecalc(void)
{
    uint32_t ccr  = ((uint32_t)s_burstWidth * TICKS_PER_US) / Gen_GetPsc1();
    uint32_t arr1 = Gen_GetArr1();

    if (ccr > arr1 - 1u) ccr = arr1 - 1u;   /* khong cho lap day 100 % */
    s_burstCcr = ccr;
}

/* Mo / dong cong xung con */
static void Gen_BurstGate(uint8_t on)
{
    __HAL_TIM_SET_COMPARE(&htim1, PULSE_CHANNEL, on ? s_burstCcr : 0u);
    s_burstGateOn = on;
}

/* Nap cau hinh xung con: chu ky 1 ms, do rong theo s_burstWidth */
static void Gen_BurstApply(void)
{
    uint32_t psc1, arr1;

    /* 1 ms = 168 000 nhip -> PSC+1 = 3 (dem 56 MHz), ARR+1 = 56 000 */
    Gen_SplitTicks(BURST_SUBPERIOD_US * TICKS_PER_US, &psc1, &arr1);
    Gen_SetTiming(psc1 - 1u, arr1 - 1u);

    Gen_BurstRecalc();

    __HAL_TIM_SET_COMPARE(&htim1, PULSE_CHANNEL, s_burstCcr);
    Gen_Reload();

    s_burstMs     = 0;
    s_burstGateOn = 1;
}

void PulseGen_BurstTick(void)
{
    if (!s_burstMode || !s_running) return;

    /* Tch = 0 -> khong mo cong lan nao, ngo ra im hoan toan.
       Tch >= TLc -> bo dem quay vong truoc khi cham moc dong, cong khong
       bao gio dong: phat lien tuc.                                      */
    if (s_burstMs == 0u)                 Gen_BurstGate(s_burstOnMs != 0u);
    else if (s_burstMs == s_burstOnMs)   Gen_BurstGate(0);   /* dong chum */

    if (++s_burstMs >= s_burstPer) s_burstMs = 0;
}

void PulseGen_BurstEnable(uint8_t on)
{
    if (on) {
        s_burstMode = 1;
        s_custom    = 0;
        Gen_BurstApply();
    } else {
        s_burstMode   = 0;
        s_burstGateOn = 0;
        PulseGen_Apply();            /* quay ve che do mau dang chon */
    }
}

uint8_t PulseGen_IsBurst(void) { return s_burstMode; }

/* =======================================================================
 *  HAI DUONG DAT GIA TRI, CO Y NGHIA KHAC NHAU:
 *
 *    PulseGen_BurstSet...()   <- NHAP TAY tu ban phim so.
 *        Khong gioi han theo dai 150..300 us hay 20..50 %. Go bao nhieu
 *        ra bay nhieu - MIEN LA HOP LE VE VAT LY:
 *            - do rong > 0
 *            - do rong < chu ky tuong ung (Tk < TLx, Tch < TLc)
 *        Sai mot trong hai dieu tren thi ham tra ve ma loi va KHONG dung
 *        vao bat ky bien nao -> gia tri truoc do duoc giu nguyen.
 *
 *    PulseGen_BurstStep...()  <- PHIM MUI TEN.
 *        Luon ep ve dung dai da quy dinh, de bam nhanh khong lo vuot.
 *        Neu gia tri hien tai dang nam ngoai dai (do vua nhap tay), lan
 *        bam dau tien se keo no tro lai bien gan nhat.
 * ===================================================================== */

/* Tk - do rong xung con. Phai 0 < Tk < TLx. */
uint8_t PulseGen_BurstSetWidthUs(uint32_t us)
{
    if (us == 0u)                 return PG_ERR_ZERO;
    if (us >= BURST_SUBPERIOD_US) return PG_ERR_GE_PERIOD;

    s_burstWidth = (uint16_t)us;
    Gen_BurstRecalc();                       /* van ep CCR <= ARR cho chac */
    if (s_burstGateOn) {                     /* dang trong chum -> ap dung ngay */
        __HAL_TIM_SET_COMPARE(&htim1, PULSE_CHANNEL, s_burstCcr);
    }
    return PG_OK;
}

/* Tk - phim trai / phai. Giu trong dai 150..300 us. */
void PulseGen_BurstStepWidth(int16_t delta_us)
{
    int32_t v = (int32_t)s_burstWidth + delta_us;

    if (v < (int32_t)BURST_WIDTH_MIN_US) v = (int32_t)BURST_WIDTH_MIN_US;
    if (v > (int32_t)BURST_WIDTH_MAX_US) v = (int32_t)BURST_WIDTH_MAX_US;

    (void)PulseGen_BurstSetWidthUs((uint32_t)v);   /* 150..300 < TLx: luon OK */
}

/* TLc - chu ky chum. Phai TLc > Tch.
   Nhap bang us, luu bang ms vi bo cat chum chay theo nhip 1 ms cua TIM2.
   Lam tron thay vi cat cut cho sat so vua go; duoi 500 us lam tron ve 0
   nen tinh la loi "toi thieu 1 ms".                                     */
uint8_t PulseGen_BurstSetPeriodUs(uint32_t us)
{
    uint32_t ms = (us + 500u) / 1000u;

    if (ms == 0u)              return PG_ERR_ZERO;
    if (ms > 0xFFFFu)          ms = 0xFFFFu;
    if (ms <= s_burstOnMs)     return PG_ERR_GE_PERIOD;  /* Tch se >= TLc */

    s_burstPer = (uint16_t)ms;
    s_burstMs  = 0;          /* bat dau lai chu ky chum cho gon */
    return PG_OK;
}

/* Tch - do rong chum. Phai 0 < Tch < TLc. */
uint8_t PulseGen_BurstSetOnUs(uint32_t us)
{
    uint32_t ms = (us + 500u) / 1000u;

    if (ms == 0u)              return PG_ERR_ZERO;
    if (ms >= s_burstPer)      return PG_ERR_GE_PERIOD;

    s_burstOnMs = (uint16_t)ms;
    s_burstMs   = 0;
    return PG_OK;
}

/* Tch - phim len / xuong, buoc theo % cua TLc. Giu trong dai 20..50 %. */
void PulseGen_BurstStepOn(int16_t delta_pct)
{
    int32_t lo   = ((int32_t)s_burstPer * (int32_t)BURST_DUTY_MIN_PCT) / 100;
    int32_t hi   = ((int32_t)s_burstPer * (int32_t)BURST_DUTY_MAX_PCT) / 100;
    int32_t step = ((int32_t)s_burstPer * delta_pct) / 100;
    int32_t v    = (int32_t)s_burstOnMs + step;

    if (v < lo) v = lo;
    if (v > hi) v = hi;

    s_burstOnMs = (uint16_t)v;
    s_burstMs   = 0;
}

uint16_t PulseGen_BurstGetWidthUs(void)     { return s_burstWidth; }
uint16_t PulseGen_BurstGetSubPeriodUs(void) { return BURST_SUBPERIOD_US; }
uint16_t PulseGen_BurstGetOnMs(void)        { return s_burstOnMs; }
uint16_t PulseGen_BurstGetPeriodMs(void)    { return s_burstPer; }

uint8_t PulseGen_BurstGetDutyPct(void)
{
    uint32_t p;

    if (s_burstPer == 0u) return 0u;

    /* Nhap tay co the cho Tch > TLc, luc do phan tram vuot qua 100 - day
       la trang thai hop le, nghia la phat lien tuc. Chan o 255 de khong
       tran khi ep ve 8 bit.                                             */
    p = ((uint32_t)s_burstOnMs * 100u) / s_burstPer;
    if (p > 255u) p = 255u;
    return (uint8_t)p;
}

/* ======================================================================= */

void PulseGen_SetOutput(uint8_t on)
{
    if (on && !s_running) {
        if (s_burstMode) {           /* bat dau lai tu dau mot chum */
            s_burstMs = 0;
            Gen_BurstGate(1);
        }
        HAL_TIM_PWM_Start(&htim1, PULSE_CHANNEL);
        s_running = 1;
    } else if (!on && s_running) {
        HAL_TIM_PWM_Stop(&htim1, PULSE_CHANNEL);
        s_running = 0;
    }
}

/* ---------------------------- Doc trang thai --------------------------- */
uint8_t PulseGen_GetIndex(void)  { return s_index; }
uint8_t PulseGen_GetCount(void)  { return (uint8_t)PRESET_COUNT; }
uint8_t PulseGen_IsOn(void)      { return s_running; }
uint8_t PulseGen_IsCustom(void)  { return s_custom; }

const char *PulseGen_GetName(void)
{
    if (s_burstMode) return "Chum xung";
    return s_custom ? "Tuy chinh" : PRESETS[s_index].name;
}

/* Doi so dem sang ns:
   t = cnt * (PSC+1) / 168 MHz = cnt * (PSC+1) * 1000/168 = cnt * (PSC+1) * 125/21
   (dung so nguyen 64 bit, khong dung so thuc)                            */
static uint32_t CntToNs(uint32_t cnt, uint32_t psc1)
{
    uint64_t ns = ((uint64_t)cnt * psc1 * 125u) / 21u;

    if (ns > 0xFFFFFFFFULL) ns = 0xFFFFFFFFULL;   /* chan tran so 32 bit */
    return (uint32_t)ns;
}

void PulseGen_GetData(PulseData_t *out)
{
    uint32_t psc1 = Gen_GetPsc1();
    uint32_t arr1 = Gen_GetArr1();
    uint32_t ccr  = Gen_GetCcr();

    /* O che do chum, trong khoang nghi CCR = 0. Neu doc thang thanh ghi
       thi man hinh se nhap nhay ve "---" theo dung nhip chum. Vi vay luon
       bao cao theo do rong xung con da dat.                              */
    if (s_burstMode) ccr = s_burstCcr;

    /* "valid" chi noi len cau hinh co hop le hay khong, KHONG phu thuoc
       vao viec ngo ra dang bat hay tat. Truoc day co dieu kien !s_running
       o day, hau qua la vua bam dung xung la ca bon dong so lieu nhay
       thanh "---", nguoi dung khong con thay minh dang chinh cai gi.
       Trang thai bat/tat da co dong "XUNG ON / XUNG OFF" lo roi.        */
    if (arr1 <= 1u || ccr == 0u) {
        out->valid = 0;
        out->period_ns = out->width_ns = out->freq_x10 = 0;
        out->duty_x10  = 0;
        return;
    }

    out->valid     = 1;
    out->period_ns = CntToNs(arr1, psc1);
    out->width_ns  = CntToNs(ccr,  psc1);

    /* f = 1/T ; luu don vi 0,1 Hz  -> 1e10 / T[ns] */
    out->freq_x10 = (uint32_t)(10000000000ULL / out->period_ns);
    /* D = CCR/(ARR+1) ; luu don vi 0,1 % */
    out->duty_x10 = (uint16_t)((ccr * 1000u) / arr1);
}
