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
#include <vector>

namespace yttria {
struct Token { std::string text; int line, column; };
struct Error : std::runtime_error {
    Error(const std::string& message, const Token& token)
        : std::runtime_error(message + " (line " + std::to_string(token.line) +
                             ", column " + std::to_string(token.column) + ")") {}
};

static std::vector<Token> lex(const std::string& source) {
    std::vector<Token> out; int line = 1, column = 1;
    for (size_t i = 0; i < source.size();) {
        char c = source[i];
        if (std::isspace(static_cast<unsigned char>(c))) {
            if (c == '\n') { ++line; column = 1; } else ++column;
            ++i; continue;
        }
        Token at{"", line, column};
        if (c == '/' && i + 1 < source.size() && source[i + 1] == '/') {
            while (i < source.size() && source[i] != '\n') { ++i; ++column; }
            continue;
        }
        if (c == '/' && i + 1 < source.size() && source[i + 1] == '*') {
            i += 2; column += 2; bool closed = false;
            while (i < source.size()) {
                if (source[i] == '*' && i + 1 < source.size() && source[i + 1] == '/') {
                    i += 2; column += 2; closed = true; break;
                }
                if (source[i++] == '\n') { ++line; column = 1; } else ++column;
            }
            if (!closed) throw Error("Unterminated comment", at);
            continue;
        }
        if (std::isalpha(static_cast<unsigned char>(c)) || c == '_') {
            std::string value;
            while (i < source.size() && (std::isalnum(static_cast<unsigned char>(source[i])) || source[i] == '_'))
                value += source[i++], ++column;
            out.push_back({value, at.line, at.column});
            continue;
        }
        if (std::isdigit(static_cast<unsigned char>(c))) {
            std::string value;
            while (i < source.size() && (std::isdigit(static_cast<unsigned char>(source[i])) || source[i] == '.'))
                value += source[i++], ++column;
            out.push_back({value, at.line, at.column}); continue;
        }
        if (c == '"' || c == '\'') {
            char quote = c; std::string value(1, c); ++i; ++column; bool closed = false;
            while (i < source.size()) {
                char x = source[i++]; value += x; ++column;
                if (x == '\\' && i < source.size()) { value += source[i++]; ++column; }
                else if (x == quote) { closed = true; break; }
            }
            if (!closed) throw Error("Unterminated string", at);
            out.push_back({value, at.line, at.column}); continue;
        }
        std::string two = source.substr(i, 2);
        if (two == "==" || two == "!=" || two == "<=" || two == ">=" || two == "&&" || two == "||") {
            out.push_back({two, line, column}); i += 2; column += 2; continue;
        }
        if (std::string("{}()[],;.:+-*/%<>=!").find(c) != std::string::npos)
            out.push_back({std::string(1, c), line, column}), ++i, ++column;
        else throw Error("Unexpected character", at);
    }
    out.push_back({"<eof>", line, column}); return out;
}

class Parser {
    std::vector<Token> t; size_t p = 0; std::ostringstream body;
    Token& peek() { return t[p]; }
    bool is(const std::string& s) { return peek().text == s; }
    Token take() { return t[p++]; }
    void need(const std::string& s) { if (!is(s)) throw Error("Expected '" + s + "'", peek()); take(); }
    std::string identifier() { Token x = take(); if (x.text.empty() || !std::isalpha(static_cast<unsigned char>(x.text[0]))) throw Error("Expected identifier", x); return x.text; }
    std::string type() {
        std::string x = identifier();
        if (x == "vector") { need("["); std::string inner = type(); need("]"); return "std::vector<" + inner + ">"; }
        static const std::unordered_map<std::string, std::string> map{{"sint8","int8_t"},{"sint16","int16_t"},{"sint32","int32_t"},{"sint64","int64_t"},{"uint8","uint8_t"},{"uint16","uint16_t"},{"uint32","uint32_t"},{"uint64","uint64_t"},{"int","int"},{"uint","unsigned"},{"char","char"},{"string","std::string"},{"str","std::string"},{"bool","bool"},{"boolean","bool"},{"void","void"}};
        auto it = map.find(x); if (it == map.end()) throw Error("Unknown type '" + x + "'", peek()); return it->second;
    }
    std::string expression(const std::vector<std::string>& stops) {
        std::string r; int depth = 0;
        while (!is("<eof>")) {
            if (depth == 0) { bool stop = false; for (const auto& s : stops) stop |= is(s); if (stop) break; }
            Token x = take();
            if ((x.text == "math" || x.text == "logic") && is(".")) {
                take();
                std::string operation = identifier();
                if (is("(")) {
                    take();
                    std::string first = expression({",", ")"});
                    if (is(",")) {
                        take();
                        std::string second = expression({")"});
                        need(")");
                        if (x.text == "math" && operation == "mod")
                            r += "yttria_mod(" + first + "," + second + ")";
                        else if (x.text == "logic" && operation == "or")
                            r += "(" + first + " || " + second + ")";
                        else if (x.text == "logic" && operation == "and")
                            r += "(" + first + " && " + second + ")";
                        else
                            throw Error("Unknown library operation", x);
                        continue;
                    }
                    need(")");
                }
                throw Error("Expected library call", x);
            }
            if (x.text == "(" || x.text == "[") ++depth;
            if (x.text == ")" || x.text == "]") --depth;
            if (x.text == "true" || x.text == "false" || x.text == "&&" || x.text == "||") {}
            if (x.text == "get" && is("(")) {
                take(); std::string value = expression({",", ")"});
                if (is(",")) { take(); std::string target = expression({")"}); need(")"); r += "yttria_convert<" + typeFor(target) + ">(" + value + ")"; }
                else { need(")"); r += value; }
                continue;
            }
            if (!r.empty() && x.text != ")" && x.text != "]" && x.text != "," && x.text != ";") r += " ";
            r += x.text;
        }
        return r;
    }
    std::string typeFor(const std::string& target) { if (target.find("uint") != std::string::npos) return "unsigned"; if (target.find("sint") != std::string::npos) return "int"; if (target == "string" || target == "str") return "std::string"; return target; }
    void statement() {
        if (is(";")) { take(); return; }
        if (is("let")) { take(); std::string mut = identifier(); std::string ty = type(); std::string name = identifier(); need("="); std::string value = expression({";"}); need(";"); body << (mut == "mut" ? "" : "const ") << ty << " " << name << " = " << value << ";\n"; return; }
        if (is("set")) { take(); std::string name = identifier(); need("="); body << name << " = " << expression({";"}) << ";\n"; need(";"); return; }
        if (is("return")) { take(); body << "return " << expression({";"}) << ";\n"; need(";"); return; }
        if (is("if")) { take(); need("("); std::string test = expression({")"}); need(")"); body << "if (" << test << ") "; block(); if (is("else")) { take(); body << " else "; if (is("if")) statement(); else block(); } return; }
        if (is("while")) { take(); need("("); body << "while (" << expression({")"}) << ") "; need(")"); block(); return; }
        if (is("for")) { take(); need("("); need("let"); std::string mut = identifier(); std::string ty = type(); std::string name = identifier(); need(")"); need("in"); need("("); std::string values = expression({")"}); need(")"); body << "for (" << (mut == "mut" ? "auto" : "const auto") << " " << name << " : "; if (values.rfind("range",0)==0) { auto open=values.find('('); body << "yttria_range" << values.substr(open); } else body << values; body << ") "; block(); return; }
        if (is("switch")) { take(); need("("); body << "switch (" << expression({")"}) << ") {"; need(")"); need("{"); while (!is("}")) { if (is("case")) { take(); need("("); body << "case " << expression({")"}) << ": "; need(")"); block(); } else if (is("default")) { take(); body << "default: "; block(); } else throw Error("Expected case or default", peek()); } need("}"); body << "}\n"; return; }
        if (is("try")) { take(); body << "try "; block(); need("catch"); need("("); std::string e=identifier(); need(")"); body << "catch (const std::exception& " << e << ") "; block(); if (is("finally")) { take(); body << "/* finally */ "; block(); } return; }
        if (is("io")) { std::string call = identifier(); need("."); call += "." + identifier(); need("."); call += "." + identifier(); need("("); std::string args=expression({")"}); need(")"); need(";"); if (call=="io.console.output") body << "yttria_append(output, " << args << ");\n"; else if (call=="io.console.error") body << "std::cerr << (" << args << ") << std::endl;\n"; else if (call=="io.console.flush") { if (args.size() < 3 || args.front() != '\'' || args.back() != '\'') throw Error("io.console.flush expects one char argument", peek()); body << "std::cout << output; output.clear(); std::cout << (" << args << ");\n"; } else if (call=="io.console.input") body << "std::getline(std::cin, " << args << ");\n"; return; }
        body << expression({";"}) << ";\n"; need(";");
    }
    void block() { need("{"); body << "{\n"; while (!is("}")) statement(); need("}"); body << "}\n"; }
public:
    explicit Parser(std::vector<Token> tokens):t(std::move(tokens)) {}
    std::string parse() {
        std::ostringstream functions;
        while (!is("<eof>")) {
            if (is("import")) {
                int importLine = peek().line;
                take();
                while (!is("<eof>") && peek().line == importLine) take();
                continue;
            }
            need("fun");
            std::string ret=type(), name=identifier(); need("(");
            std::vector<std::string> params;
            while (!is(")")) {
                need("let"); std::string mut=identifier(); (void)mut;
                std::string ty=type(), pn=identifier(); params.push_back(ty+" "+pn);
                if (!is(")")) need(",");
            }
            need(")"); body.str(""); body.clear(); block(); if (is(";")) take();
            functions << ret << " " << (name == "main" ? "yttria_main" : name) << "(";
            for(size_t i=0;i<params.size();++i) functions << (i?", ":"") << params[i];
            std::string functionBody = body.str();
            if (name == "main" && functionBody.find("return ") == std::string::npos) {
                const size_t closingBrace = functionBody.rfind('}');
                if (closingBrace == std::string::npos)
                    throw Error("Malformed main function body", peek());
                functionBody.insert(closingBrace, "return 0;\n");
            }
            functions << ") " << functionBody << "\n";
        }
        return functions.str();
    }
};
}

int main(int argc, char** argv) {
    if (argc < 2) { std::cerr << "usage: yttria-compiler source.ytr [-o|--output executable]\n"; return 2; }
    std::string destination = "a.out";
    for (int i = 2; i < argc; ++i) {
        if ((std::string(argv[i]) == "-o" || std::string(argv[i]) == "--output") && i + 1 < argc)
            destination = argv[++i];
        else {
            std::cerr << "unknown or incomplete option: " << argv[i] << "\n";
            return 2;
        }
    }
    std::ifstream in(argv[1]); if (!in) { std::cerr << "cannot open " << argv[1] << "\n"; return 1; }
    std::ostringstream source; source << in.rdbuf();
    try {
        std::string functions = yttria::Parser(yttria::lex(source.str())).parse();
        std::string generated = "#include <cstdint>\n#include <exception>\n#include <iostream>\n#include <string>\n#include <vector>\ntemplate<class T> T yttria_mod(T a,T b){return a % b;}\nstd::string output;\ninline void yttria_append(std::string& out,const std::string& value){out += value;}\ninline void yttria_append(std::string& out,const char* value){out += value;}\ninline void yttria_append(std::string& out,bool value){out += value ? \"true\" : \"false\";}\ntemplate<class T> void yttria_append(std::string& out,const T& value){out += std::to_string(value);}\ntemplate<class T> T yttria_convert(const T& v){return v;}\ntemplate<class T> std::vector<T> yttria_range(T a,T b){std::vector<T> r;for(T i=a;i<b;++i)r.push_back(i);return r;}\n" + functions + "\nint main(){ return yttria_main(); }\n";
                std::mt19937_64 random(std::chrono::steady_clock::now().time_since_epoch().count());
                std::filesystem::path temporary;
                do {
                    temporary = "yttria_tmp_" + std::to_string(random()) + ".cpp";
                } while (std::filesystem::exists(temporary));
                {
                    std::ofstream out(temporary);
                    if (!out) throw std::runtime_error("cannot create temporary C++ file");
                    out << generated;
                }
                const std::string command = "clang++ -std=c++17 -O0 \"" + temporary.string() +
                    "\" -o \"" + destination + "\"";
                const int status = std::system(command.c_str());
                std::filesystem::remove(temporary);
                if (status != 0) {
                    std::cerr << "C++ compilation failed\n";
                    return 1;
                }
    } catch (const std::exception& e) { std::cerr << "Compilation failed: " << e.what() << "\n"; return 1; }
}
