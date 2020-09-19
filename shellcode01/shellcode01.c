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