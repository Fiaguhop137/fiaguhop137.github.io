#include <iostream>
#include <filesystem>
#include <string_view>
#include <utility>
#include <fstream>
#include <string>
#include <iterator>
#include <chrono>
using std::cout;
bool verbose=false;
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
            cout<<"  --version                    Show the version of the compiler\n";
            cout<<"  -v, --verbose                Show verbose output\n";
            exit(0);
        }
        if(std::string_view(argv[i])=="-v"||std::string_view(argv[i])=="--version"){
            cout<<"Compiler version: 0.1.2\n";
            exit(0);
        }
        if(std::string_view(argv[i])=="-v"||std::string_view(argv[i])=="--verbose"){
            cout<<"Verbose output enabled\n";
            verbose=true;
            continue;
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
std::string extract_namespace(const std::string& input) {
    std::string target="namespace=\"";
    size_t start=input.find(target);
    if(start!=std::string::npos){
        start+=target.length();
        size_t end=input.find("\"",start);
        if(end!=std::string::npos){
            return input.substr(start,end-start);
        }
    }
    return "";
}
std::string strip_xmpl_tags(const std::string& input) {
    size_t start=input.find("<xmpl>");
    size_t end=input.find("</xmpl>");
    if(start!=std::string::npos&&end!=std::string::npos&&start<end){
        return input.substr(start+6,end-start-6);
    }
    return "";
}
int main(int argc,char* argv[]){
    auto[input,output]=parseArgs(argc,argv);
    std::ifstream input_file(input);
    if(!input_file.is_open()){
        std::cerr<<"Could not open input file: "<<input<<"\n";
        exit(1);
    }
    std::string input_file_content((std::istreambuf_iterator<char>(input_file)),std::istreambuf_iterator<char>());
    std::filesystem::path tmpfile="xmpl_tmp_"+std::to_string(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::high_resolution_clock::now().time_since_epoch()).count())+".cpp";
    while(std::filesystem::exists(tmpfile)){
        tmpfile="xmpl_tmp_"+std::to_string(std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::high_resolution_clock::now().time_since_epoch()).count())+".cpp";
    }
    input_file_content=strip_xmpl_tags(input_file_content);
    while(input_file_content.find("<import")!=std::string::npos){
        size_t import_start=input_file_content.find("<import");
        size_t import_end=input_file_content.find("/>",import_start);
        std::string import_content=input_file_content.substr(import_start+8,import_end-import_start-8);
        std::string import_namespace=extract_namespace(import_content);
        if(verbose){cout<<"Importing namespace: "<<import_namespace<<"\n";}
        std::filesystem::path import_file_path=import_namespace+".xmpl";
        if(!std::filesystem::exists(import_file_path)){
            std::cerr<<"Import file does not exist: "<<import_file_path<<"\n";
            exit(1);
        }
        std::ifstream import_file(import_file_path);
        if(!import_file.is_open()){
            std::cerr<<"Could not open import file: "<<import_file_path<<"\n";
            exit(1);
        }
        std::string import_file_content((std::istreambuf_iterator<char>(import_file)),std::istreambuf_iterator<char>());
        size_t import_starter=import_file_content.find("<xmpl>");
        size_t import_ender=import_file_content.find("</xmpl>");
        if(import_starter==std::string::npos||import_ender==std::string::npos||import_starter>import_ender){
            std::cerr<<"Import file is not a valid xmpl file: "<<import_file_path<<"\n";
            exit(1);
        }
        import_file_content.erase(import_ender,std::string::npos);
        import_file_content.erase(0,import_starter+6);
        input_file_content.replace(import_start,import_end-import_start+2,import_file_content);
        if(import_end==std::string::npos){
            std::cerr<<"Input file has invalid import statement\n";
            exit(1);
        }
    }
    cout<<input_file_content<<"\n";
}