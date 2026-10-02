#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <linux/uinput.h>
void send_click(int fd){
    struct input_event ie;
    memset(&ie,0,sizeof(ie));
    gettimeofday(&ie.time,NULL);
    ie.type=EV_KEY; 
    ie.code=BTN_LEFT; 
    ie.value=1;
    write(fd,&ie,sizeof(ie));
    memset(&ie,0,sizeof(ie));
    gettimeofday(&ie.time,NULL);
    ie.type=EV_SYN; 
    ie.code=SYN_REPORT; 
    ie.value=0;
    write(fd,&ie,sizeof(ie));
    usleep(33000);
    memset(&ie,0,sizeof(ie));
    gettimeofday(&ie.time,NULL);
    ie.type=EV_KEY; 
    ie.code=BTN_LEFT; 
    ie.value=0;
    write(fd,&ie,sizeof(ie));
    memset(&ie,0,sizeof(ie));
    gettimeofday(&ie.time,NULL);
    ie.type=EV_SYN; 
    ie.code=SYN_REPORT; 
    ie.value=0;
    write(fd,&ie,sizeof(ie));
}
int main() {
    int fd = open("/dev/uinput",O_WRONLY|O_NONBLOCK);
    ioctl(fd,UI_SET_EVBIT,EV_KEY);
    ioctl(fd,UI_SET_KEYBIT,BTN_LEFT);
    ioctl(fd,UI_SET_EVBIT,EV_REL);
    ioctl(fd,UI_SET_RELBIT,REL_X);
    ioctl(fd,UI_SET_RELBIT,REL_Y);
    struct uinput_setup usetup;
    memset(&usetup,0,sizeof(usetup));
    usetup.id.bustype=BUS_USB;
    usetup.id.vendor=0x1234;
    usetup.id.product=0x5678;
    strcpy(usetup.name,"real mouse(trust)");
    ioctl(fd,UI_DEV_SETUP,&usetup);
    ioctl(fd,UI_SET_PROPBIT,INPUT_PROP_POINTER);
    ioctl(fd,UI_DEV_CREATE);
    while(1){
        send_click(fd);
        usleep(67000);
    }
    ioctl(fd,UI_DEV_DESTROY);
    close(fd);
    return 0;
}
