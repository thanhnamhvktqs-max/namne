/*
 * Keypad.h
 *
 *  Created on: Sep 20, 2026
 *      Author: Legion
 */

#ifndef SRC_KEYPAD_H_
#define SRC_KEYPAD_H_
#include "main.h"

/* Ma phim tra ve. Cac phim so dung luon ky tu '0'..'9'. */
#define KEY_NONE    0
#define KEY_F1      'A'
#define KEY_F2      'B'
#define KEY_HASH    '#'
#define KEY_STAR    '*'
#define KEY_UP      'U'
#define KEY_DOWN    'D'
#define KEY_LEFT    'L'
#define KEY_RIGHT   'R'
#define KEY_ESC     'E'
#define KEY_ENTER   'N'

void Keypad_Init(void);

/* Goi deu dan trong vong lap chinh (chu ky ~20 ms).
   Tra ve ma phim MOT LAN duy nhat khi co phim moi duoc nhan,
   cac lan goi sau tra ve KEY_NONE cho toi khi nha phim ra.        */
char Keypad_GetKey(void);


#endif /* SRC_KEYPAD_H_ */
