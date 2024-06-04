/*
 * case13.c
 * ģʽ4��lock-lock-unlock-unlock
 * �������� + ������ж� +
 *  Created on: 2013��11��6��
 *      Author: chenrui
 */
#include "case13.h"



volatile unsigned long g1_case13;

void case13_main(){
	init();
	disable_isr(1); //disable high priority isr;
	/* case13_isr_low might be triggerd here */
	if(g1_case13 == 0)
        enable_isr(1);
		
    g1_case13 = 0xff;
	

}

void case13_isr_2(){

	enable_isr(1);
}

void case13_isr_1(){
	g1_case13 = 0x01;  /* bug */
}
