#include <iostream>
#include <filesystem>
#include <string_view>
#include <utility>
#include <fstream>
#include <string>
#include <iterator>
#include <chrono>
#include "tinyxml2.h"
using std::cout;
std::pair<std::filesystem::path,std::filesystem::path> parseArgs(int argc,char* argv[]){
    if(argc<2){
        std::cerr<<"Usage: "<<argv[0]<<" <input_file>\n";
        exit(1);
    }
    std::filesystem::path input;
    std::filesystem::path output="a.out";
    for(int i=1;i<argc;i++){
        if(std::string_view(argv[i])=="-h"||std::string_view(argv[i])=="--help"){
            cout<<"Usage: "<<argv[0]<<" <input_file>\n";
            cout<<"Flags:\n";
            cout<<"  -o, --output <output_file>   Specify the output file name (default: a.out)\n";
            cout<<"  -h, --help                   Show this help message\n";
            cout<<"  -v, --version                Show the version of the compiler\n";
            exit(0);
        }
        if(std::string_view(argv[i])=="-v"||std::string_view(argv[i])=="--version"){
            cout<<"Compiler version: 0.0.11\n";
            exit(0);
        }
        if(std::string_view(argv[i])=="-o"||std::string_view(argv[i])=="--output"){
            if(i+1<argc){
                if(!(output==std::filesystem::path("a.out"))){
                    std::cerr<<"Output file already specified\n";
                    exit(1);
                }
                output=argv[i+1];
                i++;
            }else{
                std::cerr<<"Missing output file after -o\nUsage: -o <output_file>\n";
                exit(1);
            }
        }else{
            if(!input.empty()){
                std::cerr<<"Multiple input files specified: "<<input<<" and "<<argv[i]<<"\n";
                exit(1);
            }
            input=argv[i];
        }
    }
    if(!std::filesystem::exists(input)){
        std::cerr<<"Input file does not exist: "<<input<<"\n";
        exit(1);
    }
    return {input,output};
}
int main(int argc,char* argv[]){
    auto[input,output]=parseArgs(argc,argv);
    std::ifstream input_file(input);
    if(!input_file.is_open()){
        std::cerr<<"Could not open input file: "<<input<<"\n";
        exit(1);
    }
    std::string input_file_content((std::istreambuf_iterator<char>(input_file)),std::istreambuf_iterator<char>());
    cout<<input_file_content<<"\n";
    std::filesystem::path tmpfile="xmpl_tmp_"+std::to_string(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::high_resolution_clock::now().time_since_epoch()).count())+".cpp";
}