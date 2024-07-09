long shared1;
void main(){
	unsigned char tmp;
	disable_isr (1);
    shared1=0;
    enable_isr (1);
	tmp = shared1;
	enable_isr (1);
}
void isr1(){
	shared1 = 1; 
}
void nestedfunc (){
    enable_isr (1);
}
void isr2(){
	call (nestedfunc);
}