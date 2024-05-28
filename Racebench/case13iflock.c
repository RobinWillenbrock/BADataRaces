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

	lock(); //disable high priority isr;
	/* case13_isr_low might be triggerd here */
	if(g1_case13 == 0)
        unlock();
		
    g1_case13 = 0xff;
	

}

void case13_isr_low(){

	lock();
	idlerun();
	unlock();

}

void case13_isr_high(){
	g1_case13 = 0x01;  /* bug */
}
