/*
 * LCD.h
 *
 *  Created on: Sep 20, 2026
 *      Author: Legion
 */

#ifndef SRC_LCD_H_
#define SRC_LCD_H_


#include "main.h"

/* ------------------------------------------------------------------ */
/*  Cau hinh kich thuoc man hinh                                       */
/*  - Waveshare 1.3" / 1.54" : 240 x 240, offset 0/0                   */
/*  - Waveshare 1.14"        : 240 x 135, offset 40/53 (che do ngang)  */
/*  - Waveshare 2.0"         : 240 x 320                               */
/* ------------------------------------------------------------------ */
#define LCD_WIDTH        240
#define LCD_HEIGHT       240
#define LCD_X_OFFSET     0
#define LCD_Y_OFFSET     0

/* ------------------------------------------------------------------ */
/*  So do noi day - dau noi LCD_1 (SM06B-GHS-TB, 6 chan)               */
/*                                                                     */
/*      chan 1  SCL  -> PA5   SPI1_SCK   (do HAL_SPI_MspInit cau hinh) */
/*      chan 2  SDA  -> PA7   SPI1_MOSI  (do HAL_SPI_MspInit cau hinh) */
/*      chan 3  RST  -> PB0                                            */
/*      chan 4  DC   -> PB1                                            */
/*      chan 5  CS   -> PE7                                            */
/*      chan 6  BL   -> PA9   (chinh la chan TIM1_CH2)                 */
/*                                                                     */
/*  GND va VCC lay trung tu nguon board.                               */
/*  Bon chan RST / DC / CS / BL duoc LCD_GpioInit() trong LCD.c cau     */
/*  hinh, khong phu thuoc vao MX_GPIO_Init() do CubeMX sinh ra.         */
/* ------------------------------------------------------------------ */
#define LCD_CS_PORT      GPIOE
#define LCD_CS_PIN       GPIO_PIN_7
#define LCD_DC_PORT      GPIOB
#define LCD_DC_PIN       GPIO_PIN_1
#define LCD_RST_PORT     GPIOB
#define LCD_RST_PIN      GPIO_PIN_0
#define LCD_BL_PORT      GPIOA
#define LCD_BL_PIN       GPIO_PIN_9

/* Lenh cua ST7789VW - theo bang lenh trong datasheet ST7789VW */
#define ST7789_SWRESET   0x01   /* Software Reset                       */
#define ST7789_SLPOUT    0x11   /* Sleep Out                            */
#define ST7789_INVON     0x21   /* Display Inversion On                 */
#define ST7789_DISPON    0x29   /* Display On                           */
#define ST7789_CASET     0x2A   /* Column Address Set                   */
#define ST7789_RASET     0x2B   /* Row Address Set                      */
#define ST7789_RAMWR     0x2C   /* Memory Write                         */
#define ST7789_MADCTL    0x36   /* Memory Data Access Control           */
#define ST7789_COLMOD    0x3A   /* Interface Pixel Format               */

/* Mau RGB565 (COLMOD = 0x05 -> 16 bit/pixel, 65K mau) */
#define BLACK            0x0000
#define WHITE            0xFFFF
#define RED              0xF800
#define GREEN            0x07E0
#define BLUE             0x001F
#define YELLOW           0xFFE0
#define CYAN             0x07FF
#define MAGENTA          0xF81F
#define ORANGE           0xFD20
#define GRAY             0x8410
#define DARKGRAY         0x39E7
#define DARKBLUE         0x0010
#define NAVY             0x0250
#define DARKGREEN        0x0320

/* API */
void ST7789_Init(void);
void ST7789_SetWindow(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1);
void ST7789_FillRect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color);
void ST7789_Clear(uint16_t color);
void ST7789_DrawPixel(uint16_t x, uint16_t y, uint16_t color);
void ST7789_HLine(uint16_t x, uint16_t y, uint16_t len, uint16_t color);
void ST7789_VLine(uint16_t x, uint16_t y, uint16_t len, uint16_t color);
void ST7789_DrawRect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color);
void ST7789_DrawChar(uint16_t x, uint16_t y, char c,
                     uint16_t fg, uint16_t bg, uint8_t scale);
void ST7789_DrawString(uint16_t x, uint16_t y, const char *s,
                       uint16_t fg, uint16_t bg, uint8_t scale);
void ST7789_Backlight(uint8_t on);


#endif /* SRC_LCD_H_ */
