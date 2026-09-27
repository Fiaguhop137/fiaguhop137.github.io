#include <iostream>
#include <filesystem>
#include <string_view>
#include <utility>
#include <fstream>
#include <string>
#include <iterator>
#include <chrono>
#include <variant>
using std::cout;
bool verbose=false;
struct variable{
    std::string name;
    std::string type;
    std::variant<int,bool,std::string> value;
    bool mut;
};
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
            cout<<"  -V, --version                Show the version of the compiler\n";
            cout<<"  -v, --verbose                Show verbose output\n";
            exit(0);
        }
        if(std::string_view(argv[i])=="-V"||std::string_view(argv[i])=="--version"){
            cout<<"Compiler version: 0.1.4\n";
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
std::string resolve_imports(std::string input,const std::filesystem::path& source_dir,const std::filesystem::path& assets_dir){
    while(input.find("<import")!=std::string::npos){
        size_t import_start=input.find("<import");
        size_t import_end=input.find("/>",import_start);
        if(import_end==std::string::npos){
            std::cerr<<"Input file has invalid import statement\n";
            exit(1);
        }
        std::string import_content=input.substr(import_start+8,import_end-import_start-8);
        std::string import_namespace=extract_namespace(import_content);
        if(verbose){cout<<"Importing namespace: "<<import_namespace<<"\n";}
        std::filesystem::path import_file_path=std::filesystem::current_path();
        for(const auto& dir:{source_dir,assets_dir}){
            import_file_path=dir/(import_namespace+".xmpl");
            if(std::filesystem::exists(import_file_path)){
                break;
            }
        }
        if(!std::filesystem::exists(import_file_path)){
            std::cerr<<"Could not find import file for namespace: "<<import_namespace<<"\n";
            exit(1);
        }
        std::ifstream import_file(import_file_path);
        if(!import_file.is_open()){
            std::cerr<<"Could not open import file: "<<import_file_path<<"\n";
            exit(1);
        }
        std::string import_file_content((std::istreambuf_iterator<char>(import_file)),std::istreambuf_iterator<char>());
        import_file_content=strip_xmpl_tags(import_file_content);
        input.replace(import_start,import_end-import_start+2,import_file_content);
    }
    return input;
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
    input_file_content=resolve_imports(input_file_content,input.parent_path(),std::filesystem::absolute(argv[0]).parent_path());
    std::ofstream tmpfile_stream(tmpfile);
    if(!tmpfile_stream.is_open()){
        std::cerr<<"Could not create temporary file: "<<tmpfile<<"\n";
        exit(1);
    }
    
    if(verbose){cout<<input_file_content<<"\n";}
}