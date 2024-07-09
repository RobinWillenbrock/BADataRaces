long shared1;
void main(){
	unsigned char tmp;
	disable_isr (1);
		if(shared1 = 0){
			enable_isr (1);
        }
        else
        {
            int variable2 = 1;
        }
	tmp = shared1;
	enable_isr (1);
}
void isr1(){
	shared1 = 1; 
}
void isr2(){
	enable_isr (1);
}