#define MAX_LENGTH 100
#define TRIGGER 99

long shared1;
long shared2;

int flag1;
int flag2;

void main() {
  disable_isr(3);

  int reader1, reader2;
  int reader3, reader4;

  for (int i = 0; i < MAX_LENGTH; i++)
    if (i == TRIGGER) reader1 = shared1;

  reader2 = shared1;

  reader3 = shared2;

  reader4 = shared2;
}

void isr1() {
  enable_isr(2);
}

void isr2() {
  flag1 = 1;

  flag2 = 0;

  enable_isr(3);
}

void isr3() {
  if (flag1 == 1) shared1 = 0x01;
  if (flag2 == 1) shared2 = 0x01;
}