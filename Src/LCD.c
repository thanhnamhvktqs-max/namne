/*
 * LCD.c
 *
 *  Created on: Sep 20, 2026
 *      Author: Legion
 */

#include "LCD.h"
#include "Font5x7.h"

extern SPI_HandleTypeDef hspi1;          /* khai bao trong main.c */
#define LCD_SPI          (&hspi1)
#define LCD_SPI_TIMEOUT  1000u

/* So pixel gui trong mot lan HAL_SPI_Transmit khi to mau.
   STM32F407 co 128 KB SRAM nen dung khoi lon hon han ban F103C6 (64 pixel):
   256 pixel = 512 byte -> giam so lan goi HAL, to man hinh nhanh hon. */
#define FILL_CHUNK       256
static uint8_t s_fillBuf[FILL_CHUNK * 2];
static uint8_t s_rowBuf[FONT_CELL_W * 4 * 2];   /* 1 dong cua ky tu, scale <= 4 */

/* ------------------------- Dieu khien chan GPIO ------------------------ */
#define CS_LOW()    HAL_GPIO_WritePin(LCD_CS_PORT,  LCD_CS_PIN,  GPIO_PIN_RESET)
#define CS_HIGH()   HAL_GPIO_WritePin(LCD_CS_PORT,  LCD_CS_PIN,  GPIO_PIN_SET)
#define DC_LOW()    HAL_GPIO_WritePin(LCD_DC_PORT,  LCD_DC_PIN,  GPIO_PIN_RESET)  /* command */
#define DC_HIGH()   HAL_GPIO_WritePin(LCD_DC_PORT,  LCD_DC_PIN,  GPIO_PIN_SET)    /* data    */
#define RST_LOW()   HAL_GPIO_WritePin(LCD_RST_PORT, LCD_RST_PIN, GPIO_PIN_RESET)
#define RST_HIGH()  HAL_GPIO_WritePin(LCD_RST_PORT, LCD_RST_PIN, GPIO_PIN_SET)

/* ------------------------------ Lop SPI -------------------------------- */
static void LCD_WriteCmd(uint8_t cmd)
{
    DC_LOW();
    CS_LOW();
    HAL_SPI_Transmit(LCD_SPI, &cmd, 1, LCD_SPI_TIMEOUT);
    CS_HIGH();
}

static void LCD_WriteData8(uint8_t dat)
{
    DC_HIGH();
    CS_LOW();
    HAL_SPI_Transmit(LCD_SPI, &dat, 1, LCD_SPI_TIMEOUT);
    CS_HIGH();
}

static void LCD_WriteDataBuf(uint8_t *buf, uint16_t len)
{
    DC_HIGH();
    CS_LOW();
    HAL_SPI_Transmit(LCD_SPI, buf, len, LCD_SPI_TIMEOUT);
    CS_HIGH();
}

/* ------------------------- Khoi tao man hinh --------------------------- */
static void LCD_Reset(void)
{
    RST_HIGH(); HAL_Delay(20);
    RST_LOW();  HAL_Delay(20);
    RST_HIGH(); HAL_Delay(120);
}

/* Chuoi khoi tao thanh ghi - lay theo LCD_1in3.c cua bo code mau
   va doi chieu voi bang lenh trong datasheet ST7789VW.               */
static void LCD_InitReg(void)
{
    LCD_WriteCmd(ST7789_COLMOD);      /* 3Ah = 05h -> RGB565, 65K mau */
    LCD_WriteData8(0x05);

    LCD_WriteCmd(0xB2);               /* Porch Setting                */
    LCD_WriteData8(0x0C); LCD_WriteData8(0x0C); LCD_WriteData8(0x00);
    LCD_WriteData8(0x33); LCD_WriteData8(0x33);

    LCD_WriteCmd(0xB7);               /* Gate Control                 */
    LCD_WriteData8(0x35);

    LCD_WriteCmd(0xBB);               /* VCOM Setting                 */
    LCD_WriteData8(0x19);

    LCD_WriteCmd(0xC0);               /* LCM Control                  */
    LCD_WriteData8(0x2C);

    LCD_WriteCmd(0xC2);               /* VDV & VRH Command Enable     */
    LCD_WriteData8(0x01);
    LCD_WriteCmd(0xC3);               /* VRH Set                      */
    LCD_WriteData8(0x12);
    LCD_WriteCmd(0xC4);               /* VDV Set                      */
    LCD_WriteData8(0x20);

    LCD_WriteCmd(0xC6);               /* FR Control 2 (~60 Hz)        */
    LCD_WriteData8(0x0F);

    LCD_WriteCmd(0xD0);               /* Power Control 1              */
    LCD_WriteData8(0xA4); LCD_WriteData8(0xA1);

    LCD_WriteCmd(0xE0);               /* Positive Voltage Gamma       */
    LCD_WriteData8(0xD0); LCD_WriteData8(0x04); LCD_WriteData8(0x0D);
    LCD_WriteData8(0x11); LCD_WriteData8(0x13); LCD_WriteData8(0x2B);
    LCD_WriteData8(0x3F); LCD_WriteData8(0x54); LCD_WriteData8(0x4C);
    LCD_WriteData8(0x18); LCD_WriteData8(0x0D); LCD_WriteData8(0x0B);
    LCD_WriteData8(0x1F); LCD_WriteData8(0x23);

    LCD_WriteCmd(0xE1);               /* Negative Voltage Gamma       */
    LCD_WriteData8(0xD0); LCD_WriteData8(0x04); LCD_WriteData8(0x0C);
    LCD_WriteData8(0x11); LCD_WriteData8(0x13); LCD_WriteData8(0x2C);
    LCD_WriteData8(0x3F); LCD_WriteData8(0x44); LCD_WriteData8(0x51);
    LCD_WriteData8(0x2F); LCD_WriteData8(0x1F); LCD_WriteData8(0x1F);
    LCD_WriteData8(0x20); LCD_WriteData8(0x23);

    LCD_WriteCmd(ST7789_INVON);       /* 21h - dao mau (can cho tam IPS) */
    LCD_WriteCmd(ST7789_SLPOUT);      /* 11h - thoat che do ngu          */
    HAL_Delay(120);
    LCD_WriteCmd(ST7789_DISPON);      /* 29h - bat hien thi              */
}

/* Cau hinh bon chan dieu khien RST / DC / CS / BL.
   Lam ngay trong driver de khong phu thuoc vao MX_GPIO_Init(): neu de
   thieu mot chan nao thi chan do tha noi va man hinh khong bao gio sang.

   Rieng chan BL nam tren PA9, dung chan voi TIM1_CH2. O day dat lai thanh
   ngo ra thuong (bat / tat den nen). Xem chu thich o ST7789_Backlight().  */
static void LCD_GpioInit(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOE_CLK_ENABLE();

    /* Muc nghi: CS = 1 (khong chon chip), RST = 1 (thoi reset),
       DC = 1 (du lieu), BL = 0 (den nen tat cho toi khi khoi tao xong) */
    HAL_GPIO_WritePin(LCD_CS_PORT,  LCD_CS_PIN,  GPIO_PIN_SET);
    HAL_GPIO_WritePin(LCD_DC_PORT,  LCD_DC_PIN,  GPIO_PIN_SET);
    HAL_GPIO_WritePin(LCD_RST_PORT, LCD_RST_PIN, GPIO_PIN_SET);
    HAL_GPIO_WritePin(LCD_BL_PORT,  LCD_BL_PIN,  GPIO_PIN_RESET);

    GPIO_InitStruct.Mode  = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull  = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;

    GPIO_InitStruct.Pin = LCD_CS_PIN;   HAL_GPIO_Init(LCD_CS_PORT,  &GPIO_InitStruct);
    GPIO_InitStruct.Pin = LCD_DC_PIN;   HAL_GPIO_Init(LCD_DC_PORT,  &GPIO_InitStruct);
    GPIO_InitStruct.Pin = LCD_RST_PIN;  HAL_GPIO_Init(LCD_RST_PORT, &GPIO_InitStruct);

    GPIO_InitStruct.Pin   = LCD_BL_PIN;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(LCD_BL_PORT, &GPIO_InitStruct);
}

void ST7789_Init(void)
{
    LCD_GpioInit();

    CS_HIGH();
    DC_HIGH();
    LCD_Reset();

    LCD_WriteCmd(ST7789_MADCTL);      /* 36h - huong quet, thu tu mau RGB */
    LCD_WriteData8(0x00);

    LCD_InitReg();
    ST7789_Backlight(1);
    ST7789_Clear(BLACK);
}

/* Den nen chi bat / tat, khong chinh do sang bang PWM.
   Ly do: chan BL (PA9) la TIM1_CH2, ma TIM1 dang lam nhiem vu phat xung.
   PulseGen doi ARR va PSC cua TIM1 moi khi nguoi dung dat lai chu ky, nen
   neu lay CH2 de dieu do sang thi tan so bam den nen se chay theo tan so
   xung dang phat. O che do "2 Hz" den nen se nhap nhay 2 lan moi giay.
   Muon chinh do sang thi phai chuyen BL sang mot bo dinh thoi khac.      */
void ST7789_Backlight(uint8_t on)
{
    HAL_GPIO_WritePin(LCD_BL_PORT, LCD_BL_PIN, on ? GPIO_PIN_SET : GPIO_PIN_RESET);
}

/* ---------------------------- Ve co ban -------------------------------- */
void ST7789_SetWindow(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1)
{
    uint8_t buf[4];

    x0 += LCD_X_OFFSET; x1 += LCD_X_OFFSET;
    y0 += LCD_Y_OFFSET; y1 += LCD_Y_OFFSET;

    LCD_WriteCmd(ST7789_CASET);                  /* 2Ah */
    buf[0] = (uint8_t)(x0 >> 8); buf[1] = (uint8_t)(x0 & 0xFF);
    buf[2] = (uint8_t)(x1 >> 8); buf[3] = (uint8_t)(x1 & 0xFF);
    LCD_WriteDataBuf(buf, 4);

    LCD_WriteCmd(ST7789_RASET);                  /* 2Bh */
    buf[0] = (uint8_t)(y0 >> 8); buf[1] = (uint8_t)(y0 & 0xFF);
    buf[2] = (uint8_t)(y1 >> 8); buf[3] = (uint8_t)(y1 & 0xFF);
    LCD_WriteDataBuf(buf, 4);

    LCD_WriteCmd(ST7789_RAMWR);                  /* 2Ch */
}

void ST7789_FillRect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color)
{
    uint32_t total, n;
    uint16_t i;

    if (x >= LCD_WIDTH || y >= LCD_HEIGHT || w == 0 || h == 0) return;
    if (x + w > LCD_WIDTH)  w = LCD_WIDTH  - x;
    if (y + h > LCD_HEIGHT) h = LCD_HEIGHT - y;

    for (i = 0; i < FILL_CHUNK; i++) {
        s_fillBuf[2 * i]     = (uint8_t)(color >> 8);
        s_fillBuf[2 * i + 1] = (uint8_t)(color & 0xFF);
    }

    ST7789_SetWindow(x, y, x + w - 1, y + h - 1);

    DC_HIGH();
    CS_LOW();
    total = (uint32_t)w * h;
    while (total) {
        n = (total > FILL_CHUNK) ? FILL_CHUNK : total;
        HAL_SPI_Transmit(LCD_SPI, s_fillBuf, (uint16_t)(n * 2), LCD_SPI_TIMEOUT);
        total -= n;
    }
    CS_HIGH();
}

void ST7789_Clear(uint16_t color)
{
    ST7789_FillRect(0, 0, LCD_WIDTH, LCD_HEIGHT, color);
}

void ST7789_DrawPixel(uint16_t x, uint16_t y, uint16_t color)
{
    uint8_t buf[2];

    if (x >= LCD_WIDTH || y >= LCD_HEIGHT) return;
    ST7789_SetWindow(x, y, x, y);
    buf[0] = (uint8_t)(color >> 8);
    buf[1] = (uint8_t)(color & 0xFF);
    LCD_WriteDataBuf(buf, 2);
}

void ST7789_HLine(uint16_t x, uint16_t y, uint16_t len, uint16_t color)
{
    ST7789_FillRect(x, y, len, 1, color);
}

void ST7789_VLine(uint16_t x, uint16_t y, uint16_t len, uint16_t color)
{
    ST7789_FillRect(x, y, 1, len, color);
}

void ST7789_DrawRect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color)
{
    if (w == 0 || h == 0) return;
    ST7789_HLine(x, y,         w, color);
    ST7789_HLine(x, y + h - 1, w, color);
    ST7789_VLine(x,         y, h, color);
    ST7789_VLine(x + w - 1, y, h, color);
}

/* ------------------------------ Van ban -------------------------------- */
/* Mo dung mot cua so GRAM cho ca o ky tu roi day tung dong pixel.
   Nhanh hon nhieu so voi ve tung diem (moi diem phai gui lai 2Ah/2Bh/2Ch). */
void ST7789_DrawChar(uint16_t x, uint16_t y, char c,
                     uint16_t fg, uint16_t bg, uint8_t scale)
{
    uint8_t  col, row, sx, sy;
    uint8_t  bits[FONT_CELL_W];
    uint16_t w, h, idx;

    if (scale == 0) scale = 1;
    if (scale > 4)  scale = 4;
    if (c < FONT_FIRST_CHAR || c > FONT_LAST_CHAR) c = '?';

    for (col = 0; col < FONT_WIDTH; col++)
        bits[col] = Font5x7[(uint8_t)c - FONT_FIRST_CHAR][col];
    bits[FONT_WIDTH] = 0x00;                 /* cot trong ngan cach chu */

    w = (uint16_t)FONT_CELL_W * scale;
    h = (uint16_t)FONT_CELL_H * scale;
    if (x + w > LCD_WIDTH || y + h > LCD_HEIGHT) return;

    ST7789_SetWindow(x, y, x + w - 1, y + h - 1);
    DC_HIGH();
    CS_LOW();

    for (row = 0; row < FONT_CELL_H; row++) {
        idx = 0;
        for (col = 0; col < FONT_CELL_W; col++) {
            uint16_t px = ((row < FONT_HEIGHT) && (bits[col] & (1u << row))) ? fg : bg;
            for (sx = 0; sx < scale; sx++) {
                s_rowBuf[idx++] = (uint8_t)(px >> 8);
                s_rowBuf[idx++] = (uint8_t)(px & 0xFF);
            }
        }
        for (sy = 0; sy < scale; sy++)
            HAL_SPI_Transmit(LCD_SPI, s_rowBuf, idx, LCD_SPI_TIMEOUT);
    }

    CS_HIGH();
}

void ST7789_DrawString(uint16_t x, uint16_t y, const char *s,
                       uint16_t fg, uint16_t bg, uint8_t scale)
{
    if (scale == 0) scale = 1;
    while (*s) {
        ST7789_DrawChar(x, y, *s++, fg, bg, scale);
        x += (uint16_t)FONT_CELL_W * scale;
        if (x >= LCD_WIDTH) break;
    }
}
