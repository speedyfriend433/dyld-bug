# dyld crash bug

## how did i find
discovered this at 2025 while browsing dylib components

## how to reprpduce
1. download trigger.dylib & run
```bash
python3 patch_dylib.py trigger.dylib 0xDEADC0DE000
```

2. compile loader
```bash
clang loader.c -o loader
```

3. lldb
```bash
lldb ./loader -o r -o bt -o register read -o q
```

## why does it crash

i don't remember clearly but i remember an oob exists in dyld chained fixup.
mach-o has 5~6 segments with chained fixup and dyld adds more by `dyld_map_with_linking_np`.

and dyld doesn't check segment_offset, dyld also process user controlled offset, do fixup operation within mapped macho image -> BOOM oob!
