/*
 * case10.c
 * ģʽ3�����������η��ʵ�ԭ����Υ��
 *
 * �������� �������ж� ������д
 *
 *  Created on: 2013��11��6��
 *      Author: chenrui
 */
#include "case10.h"

long shared1;
void main(){
	unsigned char tmp;
	disable_isr (1);
		if(shared1 = 0);
			enable_isr (1);
	tmp = shared1;
	enable_isr (1);
}
void isr1(){
	idlerun();
	shared1 = 1; 
	idlerun();
}
void isr2(){
	idlerun();
	nestedfunc();
	idlerun();
}
void nestedfunc(){
	disable_isr (1);
}
