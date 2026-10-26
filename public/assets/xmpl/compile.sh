#!/bin/bash
/usr/bin/clang++ -std=c++20 -Wall -Wextra -Werror -Wpedantic -Wno-unused-parameter -Wno-unused-variable -Wno-unused-function -Wno-unused-value -Wno-unused-label -Wno-unused-but-set-variable -Wno-unused-but-set-parameter -o /home/firebot/git/random_bs/site/assets/xmpl/compiler /home/firebot/git/random_bs/site/assets/xmpl/compiler.cpp
Y=$(sed -n 's/.*Compiler version: [0-9]\+\.[0-9]\+\.\([0-9]\+\)\\n.*/\1/p' compiler.cpp) && sed -i "s/\(Compiler version: [0-9]\+\.[0-9]\+\.\)$Y/\\1$((Y+1))/" compiler.cpp
clear
echo Compiled!