# patch_dylib.py
# Jian Lee (@speedyfriend433)

import sys
import struct

def patch_dylib(filename, target_offset):
    with open(filename, 'rb') as f:
        data = bytearray(f.read())

    magic, cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags = struct.unpack('<IIIIIII', data[:28])    
    offset = 32 
    chained_fixups_cmd_offset = None
    
    for i in range(ncmds):
        cmd, cmdsize = struct.unpack('<II', data[offset:offset+8])
        if cmd == 0x80000034: # LC_DYLD_CHAINED_FIXUPS
            chained_fixups_cmd_offset = offset
            break
        offset += cmdsize
        
    if not chained_fixups_cmd_offset:
        print("LC_DYLD_CHAINED_FIXUPS not found")
        return

    _, _, dataoff, datasize = struct.unpack('<IIII', data[chained_fixups_cmd_offset:chained_fixups_cmd_offset+16])
    
    fixup_header_offset = dataoff
    fixups_version, starts_offset, imports_offset, symbols_offset, imports_count, imports_format, symbols_format = struct.unpack('<IIIIIII', data[fixup_header_offset:fixup_header_offset+28])
    starts_in_image_offset = fixup_header_offset + starts_offset
    seg_count = struct.unpack('<I', data[starts_in_image_offset:starts_in_image_offset+4])[0]
    print(f"Segment count in fixups: {seg_count}")
    
    found_segments = 0
    for i in range(seg_count):
        seg_info_offset = struct.unpack('<I', data[starts_in_image_offset+4+i*4:starts_in_image_offset+8+i*4])[0]
        if seg_info_offset == 0:
            continue
            
        found_segments += 1
        if found_segments < 6:
            continue

        starts_in_seg_offset = starts_in_image_offset + seg_info_offset
        print(f"Patching 6th segment info at 0x{starts_in_seg_offset:x}")
        orig_offset = struct.unpack('<Q', data[starts_in_seg_offset+8:starts_in_seg_offset+16])[0]  # segment_offset is at starts_in_seg_offset+8
        print(f"Original segment_offset: 0x{orig_offset:x}")
        data[starts_in_seg_offset+8:starts_in_seg_offset+16] = struct.pack('<Q', target_offset)# overwrite
        print(f"New segment_offset: 0x{target_offset:x}")
        orig_page_count = struct.unpack('<H', data[starts_in_seg_offset+20:starts_in_seg_offset+22])[0] # page_count is at starts_in_seg_offset+20
        print(f"Original page_count: {orig_page_count}")
        data[starts_in_seg_offset+20:starts_in_seg_offset+22] = struct.pack('<H', 1)
        print("New page_count: 1")
        break

    if found_segments < 6:
        print(f"found {found_segments} segments with fixups, need at least 6.") # apple patched? :/
        return
    with open(filename + '.patched', 'wb') as f:
        f.write(data)
    print(f"Saved to {filename}.patched")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 patch_dylib.py <dylib> <hex_offset>")
        sys.exit(1)
    patch_dylib(sys.argv[1], int(sys.argv[2], 16))
