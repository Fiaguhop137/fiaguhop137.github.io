#include <stdio.h>
#include <string.h>
int main(int argc, char *argv[]) {
    int pot[6]={243,81,27,9,3,1};
    if(argc!=3){printf("Usage: %s <encode|decode> <\"text\">\n",argv[0]);return 1;}
    char *ende=argv[1];
    char *code=argv[2];
    if(strcmp(ende,"encode")==0){printf("tbd");}
    else if(strcmp(ende,"decode")==0){
        int charcnt=strlen(code)/6;
        int b10arr[charcnt+1];
        char ascii_cnvt[charcnt];
        for(int i=0;i<charcnt;i++){
            b10arr[i]=0;
            for (int j=0;j<6;j++){
                char bt=code[i*6+j];
                if((bt=='+')){b10arr[i]+=pot[j];}
                else if((bt=='-')){b10arr[i]-=pot[j];}
            }
            ascii_cnvt[i]=(char)b10arr[i]+364;
        }
        ascii_cnvt[charcnt]='\0';
        printf("%s\n",ascii_cnvt);
    }
    else{printf("Invalid input, please enter encode or decode");}
    return 0;
}