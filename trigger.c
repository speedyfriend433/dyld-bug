#include <stdint.h>

#define SEG(n) \
    __attribute__((section("__DATA,__data" #n))) uintptr_t p##n = (uintptr_t)&p##n; \
    __attribute__((section("__DATA,__data" #n))) char pad##n[4096 * 2] = {1};

SEG(1)
SEG(2)
SEG(3)
SEG(4)
SEG(5)
SEG(6)

int trigger() {
    return 0;
}
