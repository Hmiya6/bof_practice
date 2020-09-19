from pwn import *

shellcode = asm(
    """
    push 0x0006948;
    mov eax, 0x4;
    mov ebx, 0x1;
    mov ecx, esp;
    mov edx, 0x4;
    int 0x80
    """
    )

print(enhex(shellcode))
print(shellcraft.sh())
print(enhex(p32(0x17800168)))