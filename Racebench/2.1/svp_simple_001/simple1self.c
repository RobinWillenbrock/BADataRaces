/*
 * racebench2.0
 * Filename:svp_simple_001_001
 * Template File:svp_simple_001
 * Created by Beijing Sunwise Information Technology Ltd. on 19/10/30.
 * Copyright © 2019年 Beijing Sunwise Information Technology Ltd. All rights reserved.
 * [说明]:
 * 主程序入口:svp_simple_001_001_main
 * 中断入口:svp_simple_001_001_isr_1,svp_simple_001_001_isr_2
 * 中断间的优先级以中断号作为标准，中断号越高，中断优先级越高。
 *
 *
 *
 *
 */

#include "../common.h"

long shared1;
void main(){
	unsigned char tmp;
	disable_isr (1);
	if(shared1 = 0){
		enable_isr (1);
    }else{
        int variable2 = 1;
    }
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
    int variable1 = 0;
	idlerun() ;
}