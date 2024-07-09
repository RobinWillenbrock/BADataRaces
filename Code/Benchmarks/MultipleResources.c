long shared1;
long shared2;
void main(){
	unsigned char tmp;
		if(shared1 = 0){
			enable_isr (1);
        }
        else
        {
            shared2 = 1;
        }
    enable_isr (1);
    disable_isr (1);
	tmp = shared1;
	enable_isr (1);
}
void isr1(){
	shared1 = 1; 
    return;
}
void isr2(){
	int variable1 = 0;
    return;
}
