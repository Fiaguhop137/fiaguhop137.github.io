#include <cctype>
#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

namespace yttria {
struct Token { std::string text; int line, column; };
struct Error : std::runtime_error {
    Error(const std::string& s, const Token& t)
        : std::runtime_error(s + " (line " + std::to_string(t.line) +
                             ", column " + std::to_string(t.column) + ")") {}
};

static std::vector<Token> lex(const std::string& source) {
    std::vector<Token> out; int line = 1, column = 1;
    for (size_t i = 0; i < source.size();) {
        char c = source[i];
        if (std::isspace((unsigned char)c)) { if (c == '\n') ++line, column = 1; else ++column; ++i; continue; }
        Token at{"", line, column};
        if (c == '/' && i + 1 < source.size() && source[i + 1] == '/') {
            while (i < source.size() && source[i] != '\n') ++i, ++column;
            continue;
        }
        if (c == '/' && i + 1 < source.size() && source[i + 1] == '*') {
            i += 2; column += 2; bool closed = false;
            while (i < source.size()) {
                if (source[i] == '*' && i + 1 < source.size() && source[i + 1] == '/') { i += 2; column += 2; closed = true; break; }
                if (source[i++] == '\n') ++line, column = 1; else ++column;
            }
            if (!closed) throw Error("Unterminated comment", at);
            continue;
        }
        if (std::isalpha((unsigned char)c) || c == '_') {
            std::string v; while (i < source.size() && (std::isalnum((unsigned char)source[i]) || source[i] == '_')) v += source[i++], ++column;
            out.push_back({v, at.line, at.column}); continue;
        }
        if (std::isdigit((unsigned char)c)) {
            std::string v; while (i < source.size() && (std::isdigit((unsigned char)source[i]) || source[i] == '.')) v += source[i++], ++column;
            out.push_back({v, at.line, at.column}); continue;
        }
        if (c == '"' || c == '\'') {
            char q = c; std::string v(1, c); ++i; ++column; bool closed = false;
            while (i < source.size()) { char x = source[i++]; v += x; ++column; if (x == '\\' && i < source.size()) v += source[i++], ++column; else if (x == q) { closed = true; break; } }
            if (!closed) throw Error("Unterminated string", at);
            out.push_back({v, at.line, at.column}); continue;
        }
        std::string two = source.substr(i, 2);
        if (two == "==" || two == "!=" || two == "<=" || two == ">=" || two == "&&" || two == "||")
            out.push_back({two, line, column}), i += 2, column += 2;
        else if (std::string("{}()[],;.:+-*/%<>=!").find(c) != std::string::npos)
            out.push_back({std::string(1, c), line, column}), ++i, ++column;
        else throw Error("Unexpected character", at);
    }
    out.push_back({"<eof>", line, column}); return out;
}

class Parser {
    std::vector<Token> t; size_t p = 0; std::ostringstream functions, body;
    std::filesystem::path sourceDir; std::unordered_set<std::string>& imported;
    std::string prefix;
    Token& peek() { return t[p]; }
    bool is(const std::string& s) { return peek().text == s; }
    Token take() { return t[p++]; }
    void need(const std::string& s) { if (!is(s)) throw Error("Expected '" + s + "'", peek()); take(); }
    std::string identifier() { Token x = take(); if (x.text.empty() || (!std::isalpha((unsigned char)x.text[0]) && x.text[0] != '_')) throw Error("Expected identifier", x); return x.text; }
    std::string type() {
        std::string x = identifier();
        if (x == "vector") { need("["); std::string y = type(); need("]"); return "std::vector<" + y + ">"; }
        if (x == "null") return "void";
        static const std::unordered_map<std::string,std::string> m{{"sint8","int8_t"},{"sint16","int16_t"},{"sint32","int32_t"},{"sint64","int64_t"},{"uint8","uint8_t"},{"uint16","uint16_t"},{"uint32","uint32_t"},{"uint64","uint64_t"},{"int","int"},{"uint","unsigned"},{"char","char"},{"string","std::string"},{"str","std::string"},{"bool","bool"},{"boolean","bool"},{"void","void"}};
        auto i = m.find(x); if (i == m.end()) throw Error("Unknown type '" + x + "'", peek()); return i->second;
    }
    std::string qualified(std::string first) {
        while (is(".")) { take(); first += "_" + identifier(); }
        if (first == "stdin") return "yttria_stdin";
        if (first == "stdout") return "yttria_stdout";
        if (first == "stderr") return "yttria_stderr";
        return first;
    }
    std::string expression(const std::vector<std::string>& stops) {
        std::string r; int depth = 0;
        while (!is("<eof>")) {
            if (!depth) { bool stop = false; for (const auto& s : stops) stop |= is(s); if (stop) break; }
            Token x = take();
            if (x.text == "get" && is("(")) {
                take(); std::string v = expression({",", ")"}); if (is(",")) { take(); std::string target = expression({")"}); need(")"); r += "yttria_convert<" + typeFor(target) + ">(" + v + ")"; } else { need(")"); r += v; } continue;
            }
            if (std::isalpha((unsigned char)x.text[0]) || x.text[0] == '_') {
                std::string name = qualified(x.text);
                if (!r.empty() && name != ")" && name != "]" && name != ",") r += " ";
                r += name; continue;
            }
            if (x.text == "(" || x.text == "[") ++depth;
            if (x.text == ")" || x.text == "]") --depth;
            if (!r.empty() && x.text != ")" && x.text != "]" && x.text != "," && x.text != ";") r += " ";
            r += x.text;
        }
        return r;
    }
    std::string typeFor(const std::string& x) { if (x.find("uint") != std::string::npos) return "unsigned"; if (x.find("sint") != std::string::npos) return "int"; if (x == "string" || x == "str") return "std::string"; return x; }
    void block() { need("{"); body << "{\n"; while (!is("}")) statement(); need("}"); body << "}\n"; }
    void statement() {
        if (is(";")) { take(); return; }
        if (is("let")) { take(); std::string mut=identifier(), ty=type(), n=identifier(); need("="); body << (mut=="mut"?"":"const ") << ty << " " << n << " = " << expression({";"}); need(";"); body << ";\n"; return; }
        if (is("set")) { take(); std::string n=identifier(); need("="); body << n << " = " << expression({";"}); need(";"); body << ";\n"; return; }
        if (is("return")) { take(); body << "return"; if (!is(";") && !is("}")) body << " " << expression({";", "}"}); if (is(";")) take(); body << ";\n"; return; }
        if (is("if")) { take(); need("("); body << "if (" << expression({")"}); need(")"); body << ") "; block(); if (is("else")) { take(); body << " else "; if (is("if")) statement(); else block(); } return; }
        if (is("while")) { take(); need("("); body << "while (" << expression({")"}); need(")"); body << ") "; block(); return; }
        if (is("for")) { take(); need("("); need("let"); std::string mut=identifier(); type(); std::string n=identifier(); need(")"); need("in"); need("("); std::string v=expression({")"}); need(")"); body << "for (" << (mut=="mut"?"auto":"const auto") << " " << n << " : "; if (v.rfind("range",0)==0) body << "yttria_range" << v.substr(5); else body << v; body << ") "; block(); return; }
        if (is("switch")) { take(); need("("); std::string v=expression({")"}); need(")"); need("{"); body << "switch (" << v << ") {\n"; while (!is("}")) { if (is("case")) { take(); need("("); body << "case " << expression({")"}); need(")"); body << ": "; block(); } else if (is("default")) { take(); body << "default: "; block(); } else throw Error("Expected case or default",peek()); } need("}"); body << "}\n"; return; }
        if (is("try")) { take(); body << "try "; block(); need("catch"); need("("); std::string e=identifier(); need(")"); body << "catch (const std::exception& " << e << ") "; block(); if (is("finally")) { take(); block(); } return; }
        body << expression({";"}) << ";\n"; need(";");
    }
    void parseFile(const std::filesystem::path& file, const std::string& forcedPrefix = "") {
        auto canonical = std::filesystem::weakly_canonical(file).string();
        if (!imported.insert(canonical).second) return;
        std::ifstream in(file); if (!in) throw std::runtime_error("cannot open module " + file.string());
        std::ostringstream s; s << in.rdbuf();
        Parser sub(lex(s.str()), file.parent_path(), imported, forcedPrefix);
        functions << sub.parse();
    }
    void parseImport() {
        take(); std::vector<std::string> names;
        while (!is(";")) { names.push_back(identifier()); if (!is(",")) break; take(); }
        need(";");
        for (const auto& n : names) {
            std::filesystem::path module = sourceDir / (n + ".ytr");
            // Examples keep shared modules one directory above their entry point.
            if (!std::filesystem::exists(module) && std::filesystem::exists(sourceDir.parent_path() / module.filename()))
                module = sourceDir.parent_path() / module.filename();
            parseFile(module);
        }
    }
    void parseFunction(const std::string& fnPrefix) {
        need("fun"); std::string ret=type(), name=identifier(); need("("); std::vector<std::string> params;
        while (!is(")")) {
            need("let");
            identifier();
            std::string parameterType = type();
            std::string parameterName = identifier();
            params.push_back(parameterType + " " + parameterName);
            if (!is(")")) need(",");
        }
        need(")"); body.str(""); body.clear(); block(); if (is(";")) take();
        std::string cppName = (fnPrefix.empty() && name == "main") ? "yttria_main" : (fnPrefix.empty() ? name : fnPrefix + "_" + name);
        functions << ret << " " << cppName << "("; for (size_t i=0;i<params.size();++i) functions << (i?", ":"") << params[i]; functions << ") " << body.str() << "\n";
    }
public:
    Parser(std::vector<Token> tokens, std::filesystem::path dir, std::unordered_set<std::string>& seen, std::string ns)
        : t(std::move(tokens)), sourceDir(std::move(dir)), imported(seen), prefix(std::move(ns)) {}
    std::string parse() {
        while (!is("<eof>") && !is("}")) {
            if (is("import")) { parseImport(); continue; }
            if (std::isalpha((unsigned char)peek().text[0]) && p + 1 < t.size() && t[p+1].text == "{") {
                std::string ns=identifier(); need("{"); Parser nested({}, sourceDir, imported, prefix.empty()?ns:prefix+"_"+ns);
                nested.t = t; nested.p = p; std::string part=nested.parse(); p=nested.p; need("}"); if (is(";")) take(); functions << part; continue;
            }
            if (is("fun")) { parseFunction(prefix); continue; }
            throw Error("Expected import, namespace, or fun", peek());
        }
        return functions.str();
    }
};
}

int main(int argc, char** argv) {
    if (argc < 2) { std::cerr << "usage: yttria-compiler source.ytr [-o|--output executable]\n"; return 2; }
    std::string destination="a.out"; for (int i=2;i<argc;++i) { if ((std::string(argv[i])=="-o" || std::string(argv[i])=="--output") && i+1<argc) destination=argv[++i]; else { std::cerr<<"unknown or incomplete option: "<<argv[i]<<"\n"; return 2; } }
    try {
        std::filesystem::path source=std::filesystem::absolute(argv[1]); std::unordered_set<std::string> seen;
        std::ifstream in(source); if (!in) throw std::runtime_error("cannot open " + source.string()); std::ostringstream text; text<<in.rdbuf();
        std::string functions=yttria::Parser(yttria::lex(text.str()), source.parent_path(), seen, "").parse();
        std::string generated="#include <cstdint>\n#include <exception>\n#include <iostream>\n#include <fstream>\n#include <string>\n#include <vector>\nconstexpr int yttria_stdin=0, yttria_stdout=1, yttria_stderr=2;\ninline size_t len(const std::string& s){return s.size();} inline size_t len(const char* s){return std::char_traits<char>::length(s);}\ninline void write(int fd,const std::string& s,size_t n){std::ostream* o=fd==1?&std::cout:fd==2?&std::cerr:nullptr;if(o)o->write(s.data(),(std::streamsize)n);}\ninline void write(int fd,const char* s,size_t n){write(fd,std::string(s,s+n),n);}\ninline std::string read(int fd,size_t n){std::string s(n,'\\0');if(fd==0){std::cin.read(s.data(),n);s.resize((size_t)std::cin.gcount());}return s;}\ntemplate<class T>T yttria_convert(const T&v){return v;} template<class T>std::vector<T> yttria_range(T a,T b){std::vector<T>r;for(T i=a;i<b;++i)r.push_back(i);return r;}\ntemplate<class T>T yttria_mod(T a,T b){return a%b;}\ntemplate<class T>bool math_less_than(T a,T b){return a<b;} template<class T>bool math_greater_than(T a,T b){return a>=b;} template<class T>T math_subtract(T a,T b){return a-b;} template<class T>T math_multiply(T a,T b){return a*b;}\nvoid io_console_output(std::string); inline void io_console_output(int v){io_console_output(std::to_string(v));} inline void io_console_flush(char c){std::cout<<c;std::cout.flush();}\n"+functions+"\nint main(){return yttria_main();}\n";
        std::mt19937_64 random(std::chrono::steady_clock::now().time_since_epoch().count()); std::filesystem::path temporary;
        do temporary="yttria_tmp_"+std::to_string(random())+".cpp"; while(std::filesystem::exists(temporary));
        { std::ofstream out(temporary); if(!out) throw std::runtime_error("cannot create temporary C++ file"); out<<generated; }
        int status=std::system(("clang++ -std=c++17 -O0 \""+temporary.string()+"\" -o \""+destination+"\"").c_str()); std::filesystem::remove(temporary);
        if(status) { std::cerr<<"C++ compilation failed\n"; return 1; }
    } catch(const std::exception& e) { std::cerr<<"Compilation failed: "<<e.what()<<"\n"; return 1; }
}
