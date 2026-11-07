#include <iostream>
#include <iomanip>
#include <ctime>
#include <fstream>
#include <string>
int main(int argc,char* argv[]){
    if (argc<3){
        std::cerr<<"Usage: "<<argv[0]<<" <id> <change>\n"<<std::flush;
        return 1;
    }
    std::time_t time=std::time(nullptr);
    std::tm tm=*std::localtime(&time);
    std::string id=argv[1];
    std::string change;
    for(int i=2;i<argc;i++){
        change+=argv[i];
        if(i<argc-1){change+=' ';}
    }
    std::fstream file;
    bool writeHeader=false;
    file.open("changelog.md",std::ios::in);
    if(!file.is_open()){writeHeader=true;}
    else{
        std::string line;
        if(!std::getline(file,line)||line!="# Changelog"){writeHeader=true;}
        file.close();
    }
    if(writeHeader){
        file.open("changelog.md",std::ios::out);
        if(file.is_open()){
            file<<"# Changelog\n";
            file.close();
        }
    }
    file.open("changelog.md",std::ios::out|std::ios::app);
    if(file.is_open()){
        std::cout<<id<<"-"<<std::put_time(&tm,"%Y.%m.%d-%H.%M.%S%z")<<": "<<change<<'\n'<<std::flush;
        file<<" - "<<id<<"-"<<std::put_time(&tm,"%Y.%m.%d-%H.%M.%S%z")<<": "<<change<<'\n';
        file.close();
    }else{
        std::cerr<<"Error: Could not open changelog.md\n";
        return 1;
    }
}
