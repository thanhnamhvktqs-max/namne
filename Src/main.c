/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "LCD.h"
#include "pulse_gen.h"
#include "Keypad.h"
#include "Run_timer.h"
#include "Timebase.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define BG_COLOR      BLACK
#define TITLE_BG      NAVY

#define VAL_X         40      /* gia tri Tw co lon - cach nhan mot khoang */
#define VAL_Y         22
#define ROW_T_Y       50      /* chu ky lap T                           */
#define ROW_F_Y       68      /* tan so f                               */
#define ROW_D_Y       86      /* he so lap day D                        */
#define FIELD_X       64      /* toa do x cua 3 gia tri tren            */
#define FIELD_W       13      /* so ky tu co dinh cua moi truong        */
#define BIGFIELD_W    11

#define TIMER_X       4       /* dong hen gio / dem nguoc               */
#define TIMER_Y       104
#define TIMER_W       19
#define STATUS_X      4       /* dong trang thai / dong nhap so         */
#define STATUS_Y      122
#define STATUS_W      19

/* Vung do thi */
#define FRAME_X       2
#define FRAME_Y       140
#define FRAME_W       236
#define FRAME_H       99

#define PLOT_X        4
#define PLOT_Y        142
#define PLOT_W        232
#define PLOT_H        95

/* Vung do thi chia lam HAI khung chong len nhau, vi khong the ve chung
   mot truc: mot chum chua toi 500 xung con, ve dung ti le thi moi xung
   con chi rong 0,2 diem anh.
     - Khung tren : phong to muc xung con, dung ti le Tk / TLx
     - Khung duoi : muc chum,              dung ti le Tch / TLc          */
#define P1_LABEL_Y    142     /* chu "xung con"                         */
#define P1_BRACK_Y    152     /* vach do danh dau Tk                    */
#define P1_HIGH       157
#define P1_LOW        175

#define P2_LABEL_Y    183     /* chu "chum xung"                        */
#define P2_BRACK_Y    193     /* vach do danh dau Tch                   */
#define P2_HIGH       198
#define P2_LOW        216

#define LEGEND_Y      224
#define P2_CYCLES     2       /* so chu ky chum ve tren khung duoi      */
/* Khung tren khong co so chu ky co dinh: no ve dung bang so xung ma
   khung duoi ve trong mot chum, chi khac la phong to het be ngang.     */

/* ===================== Trang thai nhap tu ban phim ====================== */
/* Moi gia tri nhap deu theo don vi us, tru hen gio tinh bang phut. */
#define ENTRY_NONE    0
#define ENTRY_BON     1       /* Tch do rong chum,     us     phim F1   */
#define ENTRY_BPERIOD 2       /* TLc chu ky chum,      us     phim F2   */
#define ENTRY_BWIDTH  3       /* Tk  do rong xung con, us     phim #    */
#define ENTRY_TIMER   4       /* hen gio,              phut   phim *    */
#define ENTRY_MAXLEN  7
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
SPI_HandleTypeDef hspi1;

TIM_HandleTypeDef htim1;
TIM_HandleTypeDef htim2;

/* USER CODE BEGIN PV */
/* Chu y: KHONG khai bao lai SystemClock_Config()/MX_xxx_Init() o day.
   Cac nguyen mau da co san trong phan "Private function prototypes" ben duoi.
   Khai bao lai voi tu khoa "static" se xung dot voi dinh nghia khong static
   cua SystemClock_Config() -> loi bien dich.                              */

/* ===================== Cac ham dinh dang chuoi ========================== */
/* Tu viet thay cho sprintf de tiet kiem Flash (printf keo theo ~8 KB).    */

static uint8_t U32ToStr(uint32_t v, char *buf)
{
    char tmp[12];
    uint8_t n = 0, i;

    if (v == 0) { buf[0] = '0'; return 1; }
    while (v) { tmp[n++] = (char)('0' + (v % 10u)); v /= 10u; }
    for (i = 0; i < n; i++) buf[i] = tmp[n - 1 - i];
    return n;
}

/* In so dang dau phay tinh: scaled = gia tri * 10^dec */
static uint8_t FixedToStr(uint32_t scaled, uint8_t dec, char *buf)
{
    uint8_t  n = 0, i, d;
    uint32_t div = 1;
    uint32_t ip, fp;

    for (i = 0; i < dec; i++) div *= 10u;
    ip = scaled / div;
    fp = scaled % div;

    n = U32ToStr(ip, buf);
    if (dec) {
        buf[n++] = '.';
        for (d = dec; d > 0; d--) {
            uint32_t p = 1, k;
            for (k = 1; k < d; k++) p *= 10u;
            buf[n++] = (char)('0' + ((fp / p) % 10u));
        }
    }
    buf[n] = '\0';
    return n;
}

static void AppendStr(char *dst, uint8_t *pos, const char *src)
{
    while (*src) dst[(*pos)++] = *src++;
    dst[*pos] = '\0';
}

/* Bo sung dau cach cho du do dai co dinh -> ghi de sach chuoi cu */
static void PadTo(char *buf, uint8_t width)
{
    uint8_t n = 0;
    while (buf[n]) n++;
    while (n < width) buf[n++] = ' ';
    buf[n] = '\0';
}

/* Chon don vi thoi gian phu hop: ns / us / ms */
static void FormatTime(uint32_t ns, char *buf, uint8_t width)
{
    uint8_t n;

    if (ns < 1000u) {
        n = FixedToStr(ns, 0, buf);
        AppendStr(buf, &n, " ns");
    } else if (ns < 1000000u) {
        n = FixedToStr(ns / 10u, 2, buf);      /* us, 2 so le */
        AppendStr(buf, &n, " us");
    } else if (ns < 1000000000u) {
        n = FixedToStr(ns / 10000u, 2, buf);   /* ms, 2 so le */
        AppendStr(buf, &n, " ms");
    } else {
        n = FixedToStr(ns / 1000000u, 3, buf); /* s, 3 so le  */
        AppendStr(buf, &n, " s");
    }
    PadTo(buf, width);
}

/* Ghi chu: FormatFreq() va FormatDuty() da bi go bo. Chung chi phuc vu
   hai dong "f =" va "D =" cua che do xung lien tuc - che do nay da duoc
   gop vao man hinh chum xung duy nhat, nen khong con cho goi.           */

static uint8_t StrEqual(const char *a, const char *b)
{
    while (*a && *b) { if (*a++ != *b++) return 0; }
    return (*a == *b);
}

static void StrCopy(char *dst, const char *src)
{
    while ((*dst++ = *src++)) { }
}

static uint8_t s_entryMode = ENTRY_NONE;
static char    s_entryBuf[ENTRY_MAXLEN + 1];
static uint8_t s_entryLen  = 0;

/* 1 = lan phat gan nhat ket thuc vi HET GIO (de bao len man hinh) */
static uint8_t s_expired = 0;

/* Bo nho dem chuoi dang hien thi (de so sanh, tranh ve lai vo ich) */
static char s_txtTw[24] = "", s_txtT[24] = "", s_txtF[24] = "", s_txtD[24] = "";
static char s_txtTimer[28] = "", s_txtStatus[28] = "";
/* Trang thai cua lan ve do thi truoc. Do thi chi ve lai khi mot trong
   nam thu nay doi, nho vay man hinh khong nhap nhay.                    */
static uint8_t  s_lastOn  = 0xFF;      /* bat / tat ngo ra               */
static uint32_t s_lastTk  = 0xFFFFFFFF;/* do rong xung con, ns           */
static uint32_t s_lastTlx = 0xFFFFFFFF;/* chu ky xung con, ns            */
static uint32_t s_lastTch = 0xFFFFFFFF;/* do rong chum, ms               */
static uint32_t s_lastTlc = 0xFFFFFFFF;/* chu ky chum, ms                */

/* ========================= Bo dinh thoi phat xung ======================= */
/* Phan dem nguoc nam trong run_timer.c; o day chi ghep no voi ngo ra xung. */
static void Pulse_StartRun(void)
{
    s_expired = 0;
    PulseGen_SetOutput(1);
    Timer_Start();                /* so phut = 0 thi phat lien tuc */
}

static void Pulse_StopRun(void)
{
    PulseGen_SetOutput(0);
    Timer_Stop();
}

/* Nhan cac dong so lieu doi y nghia theo che do phat nen phai ve lai
   moi khi chuyen che do. Ky hieu dat dung theo hinh ve tay:
     - Xung lien tuc : Tw (do rong xung), T (chu ky), f (tan so),
                       D (he so lap day)
     - Chum xung     : Tk  (do rong xung con)
                       TLx (chu ky xung con)
                       Tch (do rong chum - vua theo ms vua theo %)
                       TLc (chu ky chum)
   Nhan gioi han 4 ky tu: 4 x 12 diem anh = 48, ve tu x = 4 nen ket thuc
   o x = 52, con cach FIELD_X = 64 mot khoang 12 diem anh.                */
static void UI_DrawLabels(void)
{
    ST7789_DrawString(4, VAL_Y + 6, "Tk",   CYAN,  BG_COLOR, 2);
    ST7789_DrawString(4, ROW_T_Y,   "TLx=", WHITE, BG_COLOR, 2);
    ST7789_DrawString(4, ROW_F_Y,   "Tch=", WHITE, BG_COLOR, 2);
    ST7789_DrawString(4, ROW_D_Y,   "TLc=", WHITE, BG_COLOR, 2);
}

/* --------- Ve cac chi tiet co dinh, chi goi 1 lan luc khoi dong -------- */
static void UI_DrawStatic(void)
{
    ST7789_Clear(BG_COLOR);

    ST7789_FillRect(0, 0, LCD_WIDTH, 20, TITLE_BG);
    ST7789_DrawString(6, 2, "MAY PHAT XUNG VUONG", WHITE, TITLE_BG, 2);

    UI_DrawLabels();

    ST7789_DrawRect(FRAME_X, FRAME_Y, FRAME_W, FRAME_H, GRAY);
}

/* -------------------- Cac ham ve trong vung do thi --------------------- */
static void Plot_HLine(int x0, int x1, int y, uint16_t color)
{
    if (x1 < x0) { int t = x0; x0 = x1; x1 = t; }
    if (x1 < 0 || x0 > (PLOT_W - 1)) return;
    if (x0 < 0) x0 = 0;
    if (x1 > (PLOT_W - 1)) x1 = PLOT_W - 1;
    ST7789_HLine((uint16_t)(PLOT_X + x0), (uint16_t)y, (uint16_t)(x1 - x0 + 1), color);
}

static void Plot_VLine(int x, int y0, int y1, uint16_t color)
{
    if (x < 0 || x > (PLOT_W - 1)) return;
    if (y1 < y0) { int t = y0; y0 = y1; y1 = t; }
    ST7789_VLine((uint16_t)(PLOT_X + x), (uint16_t)y0, (uint16_t)(y1 - y0 + 1), color);
}

/* Ve npulse xung vuong lien tiep, bat dau tai x0, moi chu ky rong px_per
   diem anh, ti le muc cao tren mot chu ky = hi_num / hi_den.            */
static void Plot_Train(int x0, int npulse, int px_per,
                       uint32_t hi_num, uint32_t hi_den,
                       int y_hi, int y_lo, uint16_t color)
{
    int px_hi = (hi_den == 0u) ? 1
              : (int)(((uint32_t)px_per * hi_num) / hi_den);
    int k;

    if (px_hi < 1)          px_hi = 1;           /* luon thay duoc xung   */
    if (px_hi > px_per - 1) px_hi = px_per - 1;  /* luon thay duoc khe ho */

    for (k = 0; k < npulse; k++) {
        int xs = x0 + k * px_per;
        int xh = xs + px_hi;
        int xe = xs + px_per - 1;

        Plot_VLine(xs, y_hi, y_lo, color);      /* suon len   */
        Plot_HLine(xs, xh - 1, y_hi, color);    /* muc cao    */
        Plot_VLine(xh, y_hi, y_lo, color);      /* suon xuong */
        Plot_HLine(xh, xe, y_lo, color);        /* muc thap   */
    }
}

/* Ve toan bo vung do thi.
 *
 *   KHUNG DUOI  muc chum: hai chu ky chum, khoi chum rong dung ti le
 *               Tch / TLc, va BEN TRONG khoi la cac xung con that.
 *   KHUNG TREN  chinh la khoi chum do phong to het be ngang man hinh.
 *
 *  Hai khung ve DUNG CUNG MOT SO XUNG, nen dem tren bao nhieu thi duoi
 *  bay nhieu - chi khac do phong dai. Khoi chum o duoi la cho chat hep
 *  nhat nen so xung ve duoc lay theo no: moi xung can it nhat 6 diem anh
 *  thi mat moi con phan biet duoc suon len va suon xuong.
 *
 *  Khi mot chum chua qua nhieu xung con (toi 500), khong the ve het -
 *  luc do ca hai khung cung ve so xung toi da con doc duoc, con con so
 *  THAT nam o dong chu thich phia duoi.
 */
static void UI_DrawWave(uint8_t on)
{
    uint32_t tk   = PulseGen_BurstGetWidthUs();
    uint32_t tlx  = PulseGen_BurstGetSubPeriodUs();
    uint32_t tch  = PulseGen_BurstGetOnMs();
    uint32_t tlc  = PulseGen_BurstGetPeriodMs();
    uint32_t nreal;                 /* so xung con that su trong mot chum */
    int px_burst, px_on, ndraw, px_per2, px_per1, block, k, i;

    ST7789_FillRect(PLOT_X, PLOT_Y, PLOT_W, PLOT_H, BG_COLOR);

    if (!on) {
        ST7789_DrawString(PLOT_X + 24, 178, "KHONG PHAT XUNG", RED, BG_COLOR, 2);
        for (i = 0; i < PLOT_W; i += 8) Plot_HLine(i, i + 3, P2_LOW, DARKGRAY);
        return;
    }

    nreal = (tlx == 0u) ? 0u : (tch * 1000u) / tlx;

    /* Be rong khoi chum o khung duoi, dung ti le Tch / TLc */
    px_burst = PLOT_W / P2_CYCLES;
    px_on    = (tlc == 0u) ? px_burst
             : (int)(((uint32_t)px_burst * tch) / tlc);
    if (px_on < 6)              px_on = 6;
    if (px_on > px_burst - 4)   px_on = px_burst - 4;   /* chua khe ho */

    /* So xung ve chung cho CA HAI khung */
    ndraw = px_on / 6;
    if (ndraw < 1) ndraw = 1;
    if ((uint32_t)ndraw > nreal) ndraw = (int)nreal;    /* dung ve thua */
    if (ndraw < 1) ndraw = 1;

    px_per2 = px_on / ndraw;            /* be rong 1 xung o khung duoi */
    if (px_per2 < 2) px_per2 = 2;
    block   = ndraw * px_per2;          /* be rong khoi chum thuc ve   */

    px_per1 = PLOT_W / ndraw;           /* be rong 1 xung o khung tren */

    /* ---------------- Khung tren: khoi chum phong to ------------------ */
    ST7789_DrawString(PLOT_X + 2, P1_LABEL_Y, "XUNG CON", CYAN, BG_COLOR, 1);
    Plot_Train(0, ndraw, px_per1, tk, tlx, P1_HIGH, P1_LOW, GREEN);
    {
        int px_hi = (int)(((uint32_t)px_per1 * tk) / tlx);
        if (px_hi < 1) px_hi = 1;
        Plot_HLine(0, px_hi - 1, P1_BRACK_Y, RED);
        ST7789_DrawString((uint16_t)(PLOT_X + px_hi + 4), P1_BRACK_Y - 3,
                          "Tk", RED, BG_COLOR, 1);
    }

    /* ---------------- Khung duoi: hai chu ky chum --------------------- */
    ST7789_DrawString(PLOT_X + 2, P2_LABEL_Y, "CHUM XUNG", ORANGE, BG_COLOR, 1);
    for (k = 0; k < P2_CYCLES; k++) {
        int base = k * px_burst;

        Plot_Train(base, ndraw, px_per2, tk, tlx, P2_HIGH, P2_LOW, GREEN);
        /* khoang nghi giua hai chum */
        Plot_HLine(base + block, base + px_burst - 1, P2_LOW, GREEN);
    }
    Plot_HLine(0, block - 1, P2_BRACK_Y, RED);
    ST7789_DrawString((uint16_t)(PLOT_X + block + 4), P2_BRACK_Y - 3,
                      "Tch", RED, BG_COLOR, 1);

    /* Chu thich: so xung con THAT trong moi chum = Tch / TLx */
    {
        char    leg[44];
        uint8_t n = 0;

        AppendStr(leg, &n, "PA10   ");
        n += U32ToStr(nreal, &leg[n]);
        leg[n] = 0;
        AppendStr(leg, &n, " xung con moi chum");
        if ((uint32_t)ndraw < nreal) AppendStr(leg, &n, " (ve rut gon)");

        ST7789_DrawString(PLOT_X + 2, LEGEND_Y, leg, GRAY, BG_COLOR, 1);
    }
}

/* ------------------ Dong hen gio / dem nguoc thoi gian ----------------- */
static void UI_UpdateTimerRow(void)
{
    char     buf[28];
    uint8_t  n = 0;
    uint16_t color;
    uint32_t rem, mm, ss;

    if (PulseGen_IsOn() && Timer_IsRunning()) {
        rem = Timer_RemainSec();
        mm  = rem / 60u;
        ss  = rem % 60u;
        AppendStr(buf, &n, "Con lai   ");
        if (mm < 10u) buf[n++] = '0';        /* luon hien 2 chu so phut */
        n += U32ToStr(mm, &buf[n]);
        buf[n++] = ':';
        buf[n++] = (char)('0' + (ss / 10u));
        buf[n++] = (char)('0' + (ss % 10u));
        buf[n]   = '\0';
        color = CYAN;
    } else if (PulseGen_IsOn()) {
        AppendStr(buf, &n, "Phat lien tuc");
        color = CYAN;
    } else if (s_expired) {
        AppendStr(buf, &n, "HET GIO - da dung");
        color = ORANGE;
    } else if (Timer_GetMinutes() > 0u) {
        AppendStr(buf, &n, "Hen gio   ");
        n += U32ToStr(Timer_GetMinutes(), &buf[n]);
        buf[n] = '\0';
        AppendStr(buf, &n, " phut");
        color = GRAY;
    } else {
        AppendStr(buf, &n, "Khong hen gio");
        color = GRAY;
    }
    PadTo(buf, TIMER_W);

    if (!StrEqual(buf, s_txtTimer)) {
        ST7789_DrawString(TIMER_X, TIMER_Y, buf, color, BG_COLOR, 2);
        StrCopy(s_txtTimer, buf);
    }
}

/* ------------------- Dong trang thai / dong nhap so -------------------- */
static void UI_UpdateStatus(void)
{
    char     buf[28];
    uint8_t  n = 0;
    uint16_t color;

    if (s_entryMode != ENTRY_NONE) {
        /* Tien to noi ro dang nhap dai luong nao, don vi di kem o cuoi */
        const char *pre  = "";
        const char *unit = "";

        switch (s_entryMode) {
        case ENTRY_BWIDTH:  pre = "Tk= ";  unit = "_ us"; break;
        case ENTRY_BON:     pre = "Tch="; unit = "_ us"; break;
        case ENTRY_BPERIOD: pre = "TLc="; unit = "_ us"; break;
        case ENTRY_TIMER:   pre = "Gio= "; unit = "_ ph"; break;
        default: break;
        }

        AppendStr(buf, &n, pre);
        AppendStr(buf, &n, s_entryBuf);
        AppendStr(buf, &n, unit);
        color = ORANGE;
    } else {
        AppendStr(buf, &n, PulseGen_IsOn() ? "XUNG ON  " : "XUNG OFF ");
        AppendStr(buf, &n, PulseGen_GetName());
        color = PulseGen_IsOn() ? GREEN : RED;
    }
    PadTo(buf, STATUS_W);

    if (!StrEqual(buf, s_txtStatus)) {
        ST7789_DrawString(STATUS_X, STATUS_Y, buf, color, BG_COLOR, 2);
        StrCopy(s_txtStatus, buf);
    }
}

/* --------------------- Cap nhat cac truong so lieu ---------------------
   Chi con MOT che do nen khong phai re nhanh nua. Bon dong so lieu bam
   dung ky hieu tren hinh ve: Tk, TLx, Tch, TLc.
     - Tk va TLx doc NGUOC tu thanh ghi TIM1 (d->width_ns, d->period_ns)
       nen la con so phan cung that su dang phat.
     - Tch va TLc la trang thai phan mem cua bo cat chum.                */
static void UI_Update(const PulseData_t *d)
{
    char     buf[24];
    uint8_t  n;
    uint8_t  on  = PulseGen_IsOn();
    uint32_t tch = PulseGen_BurstGetOnMs();
    uint32_t tlc = PulseGen_BurstGetPeriodMs();

    /* Tk - o chu lon */
    FormatTime(d->width_ns, buf, BIGFIELD_W);
    if (!StrEqual(buf, s_txtTw)) {
        ST7789_DrawString(VAL_X, VAL_Y, buf, YELLOW, BG_COLOR, 3);
        StrCopy(s_txtTw, buf);
    }

    /* TLx - chu ky xung con */
    FormatTime(d->period_ns, buf, FIELD_W);
    if (!StrEqual(buf, s_txtT)) {
        ST7789_DrawString(FIELD_X, ROW_T_Y, buf, WHITE, BG_COLOR, 2);
        StrCopy(s_txtT, buf);
    }

    /* Tch - do rong chum. Hien ca thoi gian that va phan tram, vi nguoi
       dung nhap bang us nhung phim mui ten lai buoc theo % cua TLc.    */
    n = U32ToStr(tch, buf);
    AppendStr(buf, &n, "ms ");
    n += U32ToStr(PulseGen_BurstGetDutyPct(), &buf[n]);
    buf[n] = '\0';
    AppendStr(buf, &n, "%");
    PadTo(buf, FIELD_W);
    if (!StrEqual(buf, s_txtF)) {
        ST7789_DrawString(FIELD_X, ROW_F_Y, buf, WHITE, BG_COLOR, 2);
        StrCopy(s_txtF, buf);
    }

    /* TLc - chu ky chum */
    n = U32ToStr(tlc, buf);
    AppendStr(buf, &n, " ms");
    PadTo(buf, FIELD_W);
    if (!StrEqual(buf, s_txtD)) {
        ST7789_DrawString(FIELD_X, ROW_D_Y, buf, WHITE, BG_COLOR, 2);
        StrCopy(s_txtD, buf);
    }

    UI_UpdateTimerRow();
    UI_UpdateStatus();

    /* Ve lai do thi khi BAT KY thong so nao doi -> hinh dang xung luon
       bam theo so lieu. Khong doi thi khong ve, tranh nhap nhay.        */
    if (on  != s_lastOn  || d->width_ns != s_lastTk || d->period_ns != s_lastTlx ||
        tch != s_lastTch || tlc != s_lastTlc) {
        UI_DrawWave(on);
        s_lastOn  = on;
        s_lastTk  = d->width_ns;
        s_lastTlx = d->period_ns;
        s_lastTch = tch;
        s_lastTlc = tlc;
    }
}

/* ======================= Man hinh bao loi nhap lieu ===================== */
/*  Khi nhap mot gia tri sai (vd Tk >= TLx), toan bo man hinh chuyen sang
 *  nen do trong ERR_SHOW_MS, sau do tu ve lai man hinh chinh. Gia tri sai
 *  KHONG duoc ap dung - PulseGen tu choi no - nen man hinh chinh hien lai
 *  dung gia tri truoc khi nhap loi.
 *
 *  Trong luc bao loi, phim bam bi bo qua de nguoi dung khong vo tinh thao
 *  tac khi chua nhin thay man hinh chinh. Ngo ra xung, bo cat chum va dong
 *  ho hen gio van chay binh thuong vi chung nam trong ngat.
 */
#define ERR_SHOW_MS   1500u

static uint8_t  s_errActive  = 0;
static uint32_t s_errStartMs = 0;

/* Ghep "<pre><gia tri> us" vao dst */
static void MakeUsLine(char *dst, const char *pre, uint32_t us)
{
    uint8_t n = 0;

    AppendStr(dst, &n, pre);
    n += U32ToStr(us, &dst[n]);
    dst[n] = '\0';
    AppendStr(dst, &n, " us");
}

/* Ve mot dong chu co 2, canh giua theo be ngang man hinh */
static void DrawCentered2(uint16_t y, const char *s, uint16_t fg, uint16_t bg)
{
    uint16_t len = 0, w;

    while (s[len]) len++;
    w = (uint16_t)(len * 12u);          /* o chu 6 diem anh x co chu 2 */
    ST7789_DrawString((uint16_t)((w < LCD_WIDTH) ? (LCD_WIDTH - w) / 2u : 0u),
                      y, s, fg, bg, 2);
}

/* Hien man hinh loi. l1 = ly do, l2 = gia tri vua nhap, l3 = gioi han. */
static void UI_ShowError(const char *l1, const char *l2, const char *l3)
{
    ST7789_Clear(RED);
    ST7789_DrawRect(3, 3, LCD_WIDTH - 6, LCD_HEIGHT - 6, WHITE);
    ST7789_DrawRect(5, 5, LCD_WIDTH - 10, LCD_HEIGHT - 10, WHITE);

    ST7789_DrawString(48, 22, "LOI NHAP", WHITE, RED, 3);   /* 8 x 18 = 144 */

    DrawCentered2(76,  l1, WHITE,  RED);
    DrawCentered2(112, l2, YELLOW, RED);
    DrawCentered2(136, l3, YELLOW, RED);
    DrawCentered2(186, "Giu gia tri cu", WHITE, RED);

    s_errActive  = 1;
    s_errStartMs = Timebase_GetMs();
}

/* Sau khi het bao loi: ve lai nen man hinh chinh va xoa moi bo nho dem,
   de lan UI_Update ke tiep ve lai TAT CA cac truong, ke ca do thi.      */
static void UI_RedrawAll(void)
{
    UI_DrawStatic();

    s_txtTw[0] = s_txtT[0] = s_txtF[0] = s_txtD[0] = '\0';
    s_txtTimer[0] = s_txtStatus[0] = '\0';

    s_lastOn  = 0xFF;
    s_lastTk  = 0xFFFFFFFFu;
    s_lastTlx = 0xFFFFFFFFu;
    s_lastTch = 0xFFFFFFFFu;
    s_lastTlc = 0xFFFFFFFFu;
}

/* ======================= Xu ly phim bam ================================= */
static uint32_t Entry_Value(void)
{
    uint32_t v = 0;
    uint8_t  i;
    for (i = 0; i < s_entryLen; i++) v = v * 10u + (uint32_t)(s_entryBuf[i] - '0');
    return v;
}

static void Entry_Reset(uint8_t mode)
{
    s_entryMode   = mode;
    s_entryLen    = 0;
    s_entryBuf[0] = '\0';
}

static void Entry_Apply(void)
{
    uint32_t v = Entry_Value();
    uint8_t  err;
    char     l2[24], l3[24];

    l2[0] = l3[0] = '\0';

    /* MOI gia tri nhap deu theo don vi us, tru hen gio tinh bang phut.
       Ham Set cua PulseGen tu kiem tra; neu sai no tra ma loi va giu
       nguyen gia tri cu, o day chi viec bao len man hinh.              */
    switch (s_entryMode) {
    case ENTRY_BWIDTH:      /* Tk - do rong xung con, phai 0 < Tk < TLx  */
        err = PulseGen_BurstSetWidthUs(v);
        if (err != PG_OK) {
            MakeUsLine(l2, "Tk  = ", v);
            if (err == PG_ERR_ZERO) {
                UI_ShowError("Tk phai > 0", l2, "");
            } else {
                MakeUsLine(l3, "TLx = ", PulseGen_BurstGetSubPeriodUs());
                UI_ShowError("Tk phai < TLx", l2, l3);
            }
        }
        break;

    case ENTRY_BON:         /* Tch - do rong chum, phai 0 < Tch < TLc    */
        err = PulseGen_BurstSetOnUs(v);
        if (err != PG_OK) {
            MakeUsLine(l2, "Tch = ", v);
            if (err == PG_ERR_ZERO) {
                UI_ShowError("Tch toi thieu 1 ms", l2, "");
            } else {
                MakeUsLine(l3, "TLc = ",
                           (uint32_t)PulseGen_BurstGetPeriodMs() * 1000u);
                UI_ShowError("Tch phai < TLc", l2, l3);
            }
        }
        break;

    case ENTRY_BPERIOD:     /* TLc - chu ky chum, phai TLc > Tch         */
        err = PulseGen_BurstSetPeriodUs(v);
        if (err != PG_OK) {
            MakeUsLine(l2, "TLc = ", v);
            if (err == PG_ERR_ZERO) {
                UI_ShowError("TLc toi thieu 1 ms", l2, "");
            } else {
                MakeUsLine(l3, "Tch = ",
                           (uint32_t)PulseGen_BurstGetOnMs() * 1000u);
                UI_ShowError("TLc phai > Tch", l2, l3);
            }
        }
        break;

    case ENTRY_TIMER:       /* hen gio, phut. Nhap 0 = tat hen gio.      */
        Timer_SetMinutes(v);
        s_expired = 0;
        /* Dang phat ma vua dat gio -> bat dau dem nguoc ngay tu bay gio */
        if (PulseGen_IsOn() && !Timer_IsRunning()) Timer_Start();
        break;

    default:
        break;
    }
}

static void HandleKey(char key)
{
    /* Phim so: chi co y nghia khi dang o che do nhap */
    if (key >= '0' && key <= '9') {
        if (s_entryMode != ENTRY_NONE && s_entryLen < ENTRY_MAXLEN) {
            s_entryBuf[s_entryLen++] = key;
            s_entryBuf[s_entryLen]   = '\0';
        }
        return;
    }

    switch (key) {
    case KEY_F1:        /* nhap Tch - do rong chum (us)   */
        Entry_Reset(ENTRY_BON);
        break;

    case KEY_F2:        /* nhap TLc - chu ky chum (us)    */
        Entry_Reset(ENTRY_BPERIOD);
        break;

    case KEY_HASH:      /* nhap Tk - do rong xung con (us) */
        Entry_Reset(ENTRY_BWIDTH);
        break;

    case KEY_STAR:      /* hen gio (phut). Nhap 0 = tat hen gio. */
        Entry_Reset(ENTRY_TIMER);
        break;

    case KEY_ESC:
        if (s_entryLen > 0) {              /* xoa lui mot chu so */
            s_entryLen--;
            s_entryBuf[s_entryLen] = '\0';
        } else {
            Entry_Reset(ENTRY_NONE);       /* thoat che do nhap  */
        }
        break;

    case KEY_ENTER:
        if (s_entryMode != ENTRY_NONE) {   /* ap dung gia tri vua nhap */
            if (s_entryLen > 0) Entry_Apply();
            Entry_Reset(ENTRY_NONE);
        } else {
            /* Ngoai che do nhap, ENTER dung de BAT / DUNG phat xung */
            if (PulseGen_IsOn()) Pulse_StopRun();
            else                 Pulse_StartRun();
        }
        break;

    case KEY_UP:        /* tang do rong chum 5 % cua TLc */
        PulseGen_BurstStepOn(+(int16_t)BURST_DUTY_STEP_PCT);
        break;

    case KEY_DOWN:      /* giam do rong chum 5 % cua TLc */
        PulseGen_BurstStepOn(-(int16_t)BURST_DUTY_STEP_PCT);
        break;

    case KEY_LEFT:      /* giam do rong xung con 10 us */
        PulseGen_BurstStepWidth(-(int16_t)BURST_WIDTH_STEP_US);
        break;

    case KEY_RIGHT:     /* tang do rong xung con 10 us */
        PulseGen_BurstStepWidth(+(int16_t)BURST_WIDTH_STEP_US);
        break;

    default:
        break;
    }
}
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_TIM1_Init(void);
static void MX_TIM2_Init(void);
static void MX_SPI1_Init(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */
  char        key;              /* ma phim doc duoc tu ban phim ma tran */
  PulseData_t data;             /* so lieu xung de hien thi len man hinh */
  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_TIM1_Init();
  MX_TIM2_Init();
  MX_SPI1_Init();
  /* USER CODE BEGIN 2 */
  Timebase_Init();              /* TIM2 - nhip goc 1 ms + ngat        */
  Keypad_Init();

  PulseGen_Start();
  PulseGen_BurstEnable(1);      /* chi con MOT che do: chum xung */

  ST7789_Init();
  UI_DrawStatic();
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* Toan bo cong viec chay theo co ngat 20 ms cua TIM2.
       Ngoai nhip do, CPU khong lam gi - cho ngat bang __WFI(). */
    if (!Timebase_Poll20ms()) {
      __WFI();
      continue;
    }

    /* Van quet ban phim de giu dung trang thai chong doi, nhung trong luc
       dang bao loi thi bo qua phim bam.                                  */
    key = Keypad_GetKey();
    if (key != KEY_NONE && !s_errActive) HandleKey(key);

    if (Timer_PollExpired()) {      /* het gio -> tu dong cat xung   */
      PulseGen_SetOutput(0);
      s_expired = 1;
    }

    /* Dang hien man hinh loi: giu nguyen cho du ERR_SHOW_MS, roi ve lai
       man hinh chinh voi gia tri cu.                                     */
    if (s_errActive) {
      if ((uint32_t)(Timebase_GetMs() - s_errStartMs) < ERR_SHOW_MS) {
        continue;
      }
      s_errActive = 0;
      UI_RedrawAll();
    }

    PulseGen_GetData(&data);
    UI_Update(&data);
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  /* Nguon clock: thach anh ngoai 25 MHz o PH0/PH1 (HSE).
     Truoc day chay bang bo dao dong RC noi (HSI) - sai so +-1 %, khong du
     chinh xac cho mot may phat xung. Thach anh chi sai khoang +-20 ppm.

       VCO vao  = HSE / PLLM = 25 MHz / 25 = 1 MHz   (cho phep 1..2 MHz)
       VCO ra   = 1 MHz x PLLN = 336 MHz             (cho phep 100..432)
       SYSCLK   = 336 MHz / PLLP = 336 / 2 = 168 MHz
       PLLQ = 7 -> 336 / 7 = 48 MHz chan (danh cho USB, hien chua dung)

     Voi thach anh 25 MHz khong the lay VCO vao bang 2 MHz nhu ST khuyen
     nghi (phai chia 12,5 - khong nguyen), nen dung 1 MHz. Day la cau hinh
     chuan cho cac board F407 gan thach anh 25 MHz.                      */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 25;
  RCC_OscInitStruct.PLL.PLLN = 336;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 7;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    /* Thach anh khong dao dong duoc -> dung han o day, man hinh se toi den.
       Neu gap hien tuong do, xem lai thach anh / tu 2 dau chan PH0-PH1,
       hoac quay ve HSI: OscillatorType = RCC_OSCILLATORTYPE_HSI,
       HSIState = RCC_HSI_ON, PLLSource = RCC_PLLSOURCE_HSI,
       PLLM = 8, PLLN = 168.                                             */
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief SPI1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_SPI1_Init(void)
{

  /* USER CODE BEGIN SPI1_Init 0 */

  /* USER CODE END SPI1_Init 0 */

  /* USER CODE BEGIN SPI1_Init 1 */

  /* USER CODE END SPI1_Init 1 */
  /* SPI1 parameter configuration*/
  hspi1.Instance = SPI1;
  hspi1.Init.Mode = SPI_MODE_MASTER;
  hspi1.Init.Direction = SPI_DIRECTION_2LINES;
  hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
  hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
  hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;
  hspi1.Init.NSS = SPI_NSS_SOFT;
  /* APB2 = 84 MHz. Chia 2 se cho SCK = 42 MHz - vuot qua muc ST7789 chay
     on dinh khi noi bang day rap (datasheet cho chu ky ghi toi thieu 66 ns).
     Chia 4 -> SCK = 21 MHz, van du nhanh de ve het man hinh.              */
  hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_4;
  hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;
  hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
  hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
  hspi1.Init.CRCPolynomial = 10;
  if (HAL_SPI_Init(&hspi1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN SPI1_Init 2 */

  /* USER CODE END SPI1_Init 2 */

}

/**
  * @brief TIM1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM1_Init(void)
{

  /* USER CODE BEGIN TIM1_Init 0 */

  /* USER CODE END TIM1_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};
  TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};

  /* USER CODE BEGIN TIM1_Init 1 */

  /* USER CODE END TIM1_Init 1 */
  /* TIM1 = 168 MHz.  Tan so goc 400 Hz:
       168 000 000 / 400 = 420 000 nhip  -> vuot qua 16 bit, phai chia truoc
       PSC = 7  -> dem 21 MHz
       ARR = 52499 -> 52 500 nhip = 2,5 ms = 400,0 Hz (dung tuyet doi)     */
  htim1.Instance = TIM1;
  htim1.Init.Prescaler = 7;
  htim1.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim1.Init.Period = 52499;
  htim1.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim1.Init.RepetitionCounter = 0;
  htim1.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim1, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim1, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 0;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCNPolarity = TIM_OCNPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  sConfigOC.OCIdleState = TIM_OCIDLESTATE_RESET;
  sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
  if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  /* Kenh 2 khong duoc cau hinh: PA9 dung lam chan BL cua man hinh LCD */
  if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_3) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_4) != HAL_OK)
  {
    Error_Handler();
  }
  sBreakDeadTimeConfig.OffStateRunMode = TIM_OSSR_DISABLE;
  sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
  sBreakDeadTimeConfig.LockLevel = TIM_LOCKLEVEL_OFF;
  sBreakDeadTimeConfig.DeadTime = 0;
  sBreakDeadTimeConfig.BreakState = TIM_BREAK_DISABLE;
  sBreakDeadTimeConfig.BreakPolarity = TIM_BREAKPOLARITY_HIGH;
  sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_DISABLE;
  if (HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakDeadTimeConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM1_Init 2 */

  /* USER CODE END TIM1_Init 2 */
  HAL_TIM_MspPostInit(&htim1);

}

/**
  * @brief TIM2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM2_Init(void)
{

  /* USER CODE BEGIN TIM2_Init 0 */

  /* USER CODE END TIM2_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM2_Init 1 */

  /* USER CODE END TIM2_Init 1 */
  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 0;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 335999;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim2) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim2, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM2_Init 2 */

  /* USER CODE END TIM2_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  /* USER CODE BEGIN MX_GPIO_Init_1 */

  /* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();
  __HAL_RCC_GPIOE_CLK_ENABLE();
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();

  /* ---------------------------------------------------------------------
     CAC CHAN DANH CHO BAN PHIM - KHONG cau hinh o day.

     Dau noi BAN_PHIM1 chiem 10 chan:
         PD5 PD6 PD7 PB5 PB6 PB7 PB8 PB9 PE0 PE1
     Toan bo do Keypad_Init() cau hinh (hang = ngo ra ho cuc mang,
     cot = ngo vao keo len). Neu o day dat chung lam ngo ra push-pull
     thi khi bam phim se co hai chan GPIO danh nguoc chieu nhau tren
     cung mot day dan -> ngan mach.

     Cac chan con lai:
         PB0 = LCD_RST, PB1 = LCD_DC, PE7 = LCD_CS, PA9 = LCD_BL
     Bon chan tren duoc dat muc nghi dung o day, sau do LCD_GpioInit()
     (goi tu ST7789_Init) cau hinh lai chinh xac.
         PC9 = chan du cua he thong.
     --------------------------------------------------------------------- */

  /*Configure GPIO pin Output Level */
  /* PA9 = LCD_BL - de den nen tat cho toi khi man hinh khoi tao xong */
  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_9, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  /* PB0 = LCD_RST, PB1 = LCD_DC */
  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0|GPIO_PIN_1, GPIO_PIN_SET);

  /*Configure GPIO pin Output Level */
  /* PE7 = LCD_CS - muc nghi phai la 1 (khong chon chip) */
  HAL_GPIO_WritePin(GPIOE, GPIO_PIN_7, GPIO_PIN_SET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOC, GPIO_PIN_9, GPIO_PIN_RESET);

  /*Configure GPIO pin : PA9 */
  GPIO_InitStruct.Pin = GPIO_PIN_9;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pins : PB0 PB1 */
  GPIO_InitStruct.Pin = GPIO_PIN_0|GPIO_PIN_1;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /*Configure GPIO pin : PE7 */
  GPIO_InitStruct.Pin = GPIO_PIN_7;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
  HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);

  /*Configure GPIO pin : PC9 */
  GPIO_InitStruct.Pin = GPIO_PIN_9;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /* USER CODE BEGIN MX_GPIO_Init_2 */

  /* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
