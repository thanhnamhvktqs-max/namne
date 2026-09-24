/*
 * Keypad.c
 *
 *  Created on: Sep 20, 2026
 *      Author: Legion
 */

#include "Keypad.h"

#define KP_ROWS        5
#define KP_COLS        4
#define DEBOUNCE_CNT   2      /* so lan quet lien tiep phai giong nhau */

/* ---------------------------------------------------------------------
 *  So do noi day - dau noi BAN_PHIM1 (SM10B-GHS-TB, 10 chan)
 *
 *      chan 1  -> PD5      chan 6  -> PB7
 *      chan 2  -> PD6      chan 7  -> PB8
 *      chan 3  -> PD7      chan 8  -> PB9
 *      chan 4  -> PB5      chan 9  -> PE0
 *      chan 5  -> PB6      chan 10 -> PE1   (du ra, khong dung)
 *
 *  Ban phim 20 phim can 9 duong tin hieu:
 *      chan 1..4 = 4 COT   (ngo vao, keo len)
 *      chan 5..9 = 5 HANG  (ngo ra ho cuc mang)
 *
 *  Cac chan nam tren BA cong khac nhau (GPIOB, GPIOD, GPIOE) nen moi chan
 *  phai luu kem ten cong, khong dung chung mot KP_PORT nhu truoc duoc.
 * ------------------------------------------------------------------- */
typedef struct {
    GPIO_TypeDef *port;
    uint16_t      pin;
} KpPin_t;

/* Chan HANG (ngo ra) - chan 5,6,7,8,9 cua ban phim */
static const KpPin_t ROW_PIN[KP_ROWS] = {
    { GPIOB, GPIO_PIN_6 },    /* chan 5  - PB6 */
    { GPIOB, GPIO_PIN_7 },    /* chan 6  - PB7 */
    { GPIOB, GPIO_PIN_8 },    /* chan 7  - PB8 */
    { GPIOB, GPIO_PIN_9 },    /* chan 8  - PB9 */
    { GPIOE, GPIO_PIN_0 }     /* chan 9  - PE0 */
};

/* Chan COT (ngo vao, keo len) - chan 1,2,3,4 cua ban phim */
static const KpPin_t COL_PIN[KP_COLS] = {
    { GPIOD, GPIO_PIN_5 },    /* chan 1  - PD5 */
    { GPIOD, GPIO_PIN_6 },    /* chan 2  - PD6 */
    { GPIOD, GPIO_PIN_7 },    /* chan 3  - PD7 */
    { GPIOB, GPIO_PIN_5 }     /* chan 4  - PB5 */
};

/* Chan 10 cua dau noi (PE1) khong tham gia quet phim. Van dat la ngo vao
   keo len de chan khong bi tha noi.                                      */
#define KP_SPARE_PORT  GPIOE
#define KP_SPARE_PIN   GPIO_PIN_1

/* Bang ma phim, xep dung nhu mat ban phim */
static const char KEYMAP[KP_ROWS][KP_COLS] = {
    { KEY_F1,   KEY_F2, KEY_HASH,  KEY_STAR  },
    { '1',      '2',    '3',       KEY_UP    },
    { '4',      '5',    '6',       KEY_DOWN  },
    { '7',      '8',    '9',       KEY_ESC   },
    { KEY_LEFT, '0',    KEY_RIGHT, KEY_ENTER }
};

static char    s_last   = KEY_NONE;   /* ket qua quet lan truoc          */
static char    s_stable = KEY_NONE;   /* trang thai da duoc chong doi    */
static uint8_t s_count  = 0;

void Keypad_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    uint8_t i;

    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOD_CLK_ENABLE();
    __HAL_RCC_GPIOE_CLK_ENABLE();

    /* Cac chan HANG: ngo ra HO CUC MANG (open-drain) + dien tro keo len.
       Dung push-pull thi khi nguoi dung bam hai phim cung mot cot o hai
       hang khac nhau, mot chan dang keo len 3,3 V se noi thang vao mot
       chan dang keo xuong 0 V -> dong ngan mach qua hai chan GPIO.
       Voi open-drain, muc "cao" chi la tha noi cho dien tro keo len,
       nen truong hop tren chi con dong dien rat nho, hoan toan an toan.  */
    for (i = 0; i < KP_ROWS; i++) {
        HAL_GPIO_WritePin(ROW_PIN[i].port, ROW_PIN[i].pin, GPIO_PIN_SET);
        GPIO_InitStruct.Pin   = ROW_PIN[i].pin;
        GPIO_InitStruct.Mode  = GPIO_MODE_OUTPUT_OD;
        GPIO_InitStruct.Pull  = GPIO_PULLUP;
        GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
        HAL_GPIO_Init(ROW_PIN[i].port, &GPIO_InitStruct);
    }

    /* Cac chan COT: ngo vao, dien tro keo len ben trong.
       Khong nhan phim -> doc duoc muc 1.                                  */
    for (i = 0; i < KP_COLS; i++) {
        GPIO_InitStruct.Pin  = COL_PIN[i].pin;
        GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
        GPIO_InitStruct.Pull = GPIO_PULLUP;
        HAL_GPIO_Init(COL_PIN[i].port, &GPIO_InitStruct);
    }

    /* Chan du cua dau noi */
    GPIO_InitStruct.Pin  = KP_SPARE_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(KP_SPARE_PORT, &GPIO_InitStruct);
}

/* Cho tin hieu on dinh sau khi doi muc chan hang.
   Voi ngo ra open-drain, muc cao do dien tro keo len ben trong (~40 kOhm)
   dung len nen suon len cham hon han push-pull -> phai cho lau hon,
   khoang 20 us. Quet ca 5 hang cung chi mat ~0,1 ms, khong dang ke so voi
   chu ky quet 20 ms.                                                     */
static void Keypad_SettleDelay(void)
{
    volatile uint32_t i;
    for (i = 0; i < 1000u; i++) { __NOP(); }
}

/* Quet mot luot, tra ve phim dang duoc nhan (phim dau tien tim thay) */
static char Keypad_Scan(void)
{
    uint8_t r, c;
    char    key = KEY_NONE;

    for (r = 0; r < KP_ROWS; r++) {
        uint8_t k;

        /* Chi keo mot hang xuong 0, cac hang con lai tha len muc 1 */
        for (k = 0; k < KP_ROWS; k++)
            HAL_GPIO_WritePin(ROW_PIN[k].port, ROW_PIN[k].pin, GPIO_PIN_SET);
        HAL_GPIO_WritePin(ROW_PIN[r].port, ROW_PIN[r].pin, GPIO_PIN_RESET);
        Keypad_SettleDelay();

        for (c = 0; c < KP_COLS; c++) {
            if (HAL_GPIO_ReadPin(COL_PIN[c].port, COL_PIN[c].pin) == GPIO_PIN_RESET) {
                key = KEYMAP[r][c];
                break;
            }
        }
        if (key != KEY_NONE) break;
    }

    /* Tra cac hang ve muc cao */
    for (r = 0; r < KP_ROWS; r++)
        HAL_GPIO_WritePin(ROW_PIN[r].port, ROW_PIN[r].pin, GPIO_PIN_SET);

    return key;
}

char Keypad_GetKey(void)
{
    char now = Keypad_Scan();

    if (now != s_last) {              /* dang doi -> dem lai tu dau */
        s_last  = now;
        s_count = 0;
        return KEY_NONE;
    }

    if (s_count < DEBOUNCE_CNT) {
        s_count++;
        if (s_count == DEBOUNCE_CNT && now != s_stable) {
            s_stable = now;
            if (now != KEY_NONE) return now;   /* bao cao MOT lan duy nhat */
        }
    }
    return KEY_NONE;
}
