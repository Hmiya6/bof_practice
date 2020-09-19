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