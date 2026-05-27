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


## lldb
```bash
* thread #1, queue = 'com.apple.main-thread', stop reason = EXC_BAD_ACCESS (code=1, address=0xdebdc11e000)
    frame #0: 0x000000018c37c6c0 dyld`dyld4::fixupPage64(void*, mwl_info_hdr const*, dyld_chained_starts_in_segment const*, unsigned int, bool) + 84
dyld`dyld4::fixupPage64:
->  0x18c37c6c0 <+84>: ldr    x12, [x9]
    0x18c37c6c4 <+88>: tbnz   x12, #0x3f, 0x18c37c6dc ; <+112>
    0x18c37c6c8 <+92>: and    x13, x12, #0xfffffffff
    0x18c37c6cc <+96>: add    x13, x13, x11
Target 0: (loader) stopped.
(lldb) bt
* thread #1, queue = 'com.apple.main-thread', stop reason = EXC_BAD_ACCESS (code=1, address=0xdebdc11e000)
  * frame #0: 0x000000018c37c6c0 dyld`dyld4::fixupPage64(void*, mwl_info_hdr const*, dyld_chained_starts_in_segment const*, unsigned int, bool) + 84
    frame #1: 0x000000018c37c484 dyld`dyld4::dyld_map_with_linking_np(mwl_region const*, unsigned int, mwl_info_hdr const*, unsigned int) + 548
    frame #2: 0x000000018c376580 dyld`dyld4::setUpPageInLinkingRegions(dyld4::RuntimeState&, dyld4::Loader const*, unsigned long, unsigned short, unsigned short, bool, dyld3::Array<dyld4::PageInLinkingRange> const&, dyld3::Array<void const*> const&) + 856
    frame #3: 0x000000018c375f30 dyld`invocation function for block in dyld4::Loader::setUpPageInLinking(Diagnostics&, dyld4::RuntimeState&, unsigned long, unsigned long long, dyld3::Array<void const*> const&) const + 380
    frame #4: 0x000000018c375c74 dyld`dyld4::Loader::setUpPageInLinking(Diagnostics&, dyld4::RuntimeState&, unsigned long, unsigned long long, dyld3::Array<void const*> const&) const + 508
    frame #5: 0x000000018c3766f0 dyld`dyld4::Loader::applyFixupsGeneric(Diagnostics&, dyld4::RuntimeState&, unsigned long long, dyld3::Array<void const*> const&, dyld3::Array<void const*> const&, bool, dyld3::Array<dyld4::Loader::MissingFlatLazySymbol> const&) const + 192
    frame #6: 0x000000018c36fbd0 dyld`dyld4::JustInTimeLoader::applyFixups(Diagnostics&, dyld4::RuntimeState&, dyld4::DyldCacheDataConstLazyScopedWriter&, bool, lsl::Vector<std::__1::pair<dyld4::Loader const*, char const*>>*) const + 676
    frame #7: 0x000000018c348ff0 dyld`dyld4::APIs::dlopen_from(char const*, int, void*)::$_0::operator()() const::'lambda'()::operator()() const + 1408
    frame #8: 0x000000018c348a04 dyld`void dyld4::RuntimeLocks::withLoadersWriteLockAndProtectedStack<dyld4::APIs::dlopen_from(char const*, int, void*)::$_0::operator()() const::'lambda'()>(dyld4::APIs::dlopen_from(char const*, int, void*)::$_0::operator()() const::'lambda'())::'lambda'()::operator()() const + 184
    frame #9: 0x000000018c347ca8 dyld`dyld4::APIs::dlopen_from(char const*, int, void*)::$_0::operator()() const + 792
    frame #10: 0x000000018c33bfd8 dyld`dyld4::APIs::dlopen_from(char const*, int, void*) + 1104
    frame #11: 0x000000018c33bae4 dyld`dyld4::APIs::dlopen(char const*, int) + 120
    frame #12: 0x0000000100000564 loader`main + 108
    frame #13: 0x000000018c34fda4 dyld`start + 6992
```
