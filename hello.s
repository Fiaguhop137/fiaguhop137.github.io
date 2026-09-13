.global _start
.text
_start:
mov $1,%edi;mov %edi,%eax;lea msg(%rip),%rsi;mov $14,%edx;syscall
mov $60,%al;xor %edi,%edi;syscall
.section .rodata
msg:.ascii "Hello, world!\n"