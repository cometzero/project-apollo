"""Read-only AArch64 EFI/UKI architecture gate for completed AutoSD raw disks.

This checks loadable PE structure and architecture, not Secure Boot signatures
or runtime behavior. Slot selection follows autosd/ukiboot/bootctl.h.
"""
import argparse
import hashlib
import json
import mmap
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.run.autosd_disk import inspect_disk


def inspect_pe(data, *, uki=False):
    """Check bounded PE headers/sections, allowing signed read-only inputs."""
    if len(data) < 64 or bytes(data[:2]) != b'MZ':
        raise ValueError('Missing or truncated DOS/PE header')
    pe = struct.unpack_from('<I', data, 60)[0]
    if pe < 64 or pe + 24 > len(data) or bytes(data[pe:pe+4]) != b'PE\0\0':
        raise ValueError('Invalid or truncated PE header')
    machine, count = struct.unpack_from('<HH', data, pe+4)
    if machine != 0xAA64:
        raise ValueError(f'Expected AArch64 PE machine 0xaa64, found 0x{machine:04x}')
    optsize = struct.unpack_from('<H', data, pe+20)[0]
    opt, table = pe+24, pe+24+optsize
    if not count or optsize < 112 or table+count*40 > len(data):
        raise ValueError('Truncated PE optional header/section table')
    if struct.unpack_from('<H',data,opt)[0] != 0x20B:
        raise ValueError('Expected PE32+ optional header')
    if struct.unpack_from('<H',data,opt+68)[0] != 10:
        raise ValueError('Expected EFI application subsystem')
    image_size, headers_size = struct.unpack_from('<II',data,opt+56)
    directories = struct.unpack_from('<I',data,opt+108)[0]
    if directories > (optsize-112)//8 or not table+count*40 <= headers_size <= len(data):
        raise ValueError('Invalid PE header/directory bounds')
    end = headers_size
    # Certificate table uses a file offset, unlike other data directories.
    if directories > 4:
        cert_offset, cert_size = struct.unpack_from('<II',data,opt+144)
        if bool(cert_offset) != bool(cert_size) or cert_offset+cert_size > len(data):
            raise ValueError('Truncated PE certificate table')
        end = max(end,cert_offset+cert_size)
    sections = {}
    for i in range(count):
        entry = table+i*40
        try:
            name = bytes(data[entry:entry+8]).rstrip(b'\0').decode('ascii')
        except UnicodeDecodeError as error:
            raise ValueError('Invalid PE section name') from error
        virtual_size,rva,size,offset = struct.unpack_from('<IIII',data,entry+8)
        if not name or name in sections or rva+max(size,virtual_size)>image_size:
            raise ValueError('Invalid PE section/image bounds')
        if size and (offset<headers_size or offset+size>len(data)):
            raise ValueError(f'Truncated PE section: {name}')
        sections[name] = {'offset':offset,'size':size,'virtual_size':virtual_size}
        end = max(end,offset+size if size else 0)
    if uki:
        for name in ('.linux','.initrd','.cmdline'):
            section = sections.get(name,{})
            if not section.get('virtual_size') or section['virtual_size']>section['size']:
                raise ValueError(f'Missing or uninitialized UKI section: {name}')
        kernel = sections['.linux']
        if kernel['virtual_size']<64 or bytes(data[kernel['offset']+56:kernel['offset']+60]) != b'ARM\x64':
            raise ValueError('UKI .linux is not an AArch64 kernel Image')
    return {'machine':'aarch64','machine_id':'0xaa64','size':end,
            'sha256':hashlib.sha256(data[:end]).hexdigest(),'sections':sorted(sections)}


def selected_slot(control):
    if control['state']=='uninitialized':
        return 'ukiboot_a'  # Upstream initializes priorities A=15, B=14.
    if control['state']!='valid':
        raise ValueError('Invalid UKIBoot control data')
    eligible = [(slot['priority'],-i) for i,slot in enumerate(control['slots'])
                if slot['successful_boot'] or slot['tries_remaining']]
    if not eligible:
        raise ValueError('No bootable UKIBoot slot')
    return ('ukiboot_a','ukiboot_b')[-max(eligible)[1]]


def inspect_image_architecture(image):
    """Return JSON-compatible evidence; raise ValueError on an unsafe boot chain."""
    image = Path(image).absolute()
    info = inspect_disk(image)
    active = selected_slot(info['bootctl'])
    result = {'status':'PASS','image':str(image),'bootctl_state':info['bootctl']['state'],
              'selected_slot':active,'boot_path':'/EFI/BOOT/BOOTAA64.EFI','efi':{},'slots':{},
              'scope':'PE architecture/structure only; Secure Boot trust and runtime not verified'}
    with image.open('rb') as stream, mmap.mmap(stream.fileno(),0,access=mmap.ACCESS_READ) as disk:
        for label in ('ukiboot_a','ukiboot_b'):
            part = info['partitions'][label]
            begin,end = part['offset'],part['offset']+part['size']
            empty = all(disk[pos:min(pos+1048576,end)]==b'\0'*min(1048576,end-pos)
                        for pos in range(begin,end,1048576))
            if empty:
                if label==active:
                    raise ValueError(f'Selected UKIBoot slot is empty: {label}')
                result['slots'][label] = {'state':'empty'}
            else:
                view = memoryview(disk)[begin:end]
                try:
                    result['slots'][label] = {'state':'populated',**inspect_pe(view,uki=True)}
                except ValueError as error:
                    raise ValueError(f'{label}: {error}') from error
                finally:
                    view.release()
        # Extract from a temporary ESP copy: mtools cannot write to the source disk.
        esp = info['partitions']['efi']
        with tempfile.TemporaryDirectory(prefix='autosd-efi-inspect-') as temporary:
            esp_path = Path(temporary)/'esp.img'
            with esp_path.open('wb') as output:
                for pos in range(esp['offset'],esp['offset']+esp['size'],1048576):
                    output.write(disk[pos:min(pos+1048576,esp['offset']+esp['size'])])
            listing = subprocess.run(['mdir','-i',str(esp_path),'-/','-b','::/EFI/BOOT'],capture_output=True,text=True)
            if listing.returncode:
                raise ValueError('Cannot read EFI/BOOT from ESP: '+listing.stderr.strip())
            paths = [name for name in listing.stdout.splitlines() if name.lower().endswith('.efi')]
            if not any(name.upper()=='::/EFI/BOOT/BOOTAA64.EFI' for name in paths):
                raise ValueError('Missing AArch64 fallback chainloader /EFI/BOOT/BOOTAA64.EFI')
            for i,name in enumerate(paths):
                extracted = Path(temporary)/f'{i}.efi'
                copied = subprocess.run(['mcopy','-i',str(esp_path),name,str(extracted)],capture_output=True,text=True)
                if copied.returncode:
                    raise ValueError(f'Cannot read EFI file {name}: {copied.stderr.strip()}')
                try:
                    result['efi'][name[2:]] = inspect_pe(extracted.read_bytes())
                except ValueError as error:
                    raise ValueError(f'{name}: {error}') from error
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image',type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(inspect_image_architecture(args.image),indent=2))
    except (ValueError,OSError) as error:
        print(json.dumps({'status':'FAIL','error':str(error)},indent=2))
        return 1
    return 0


if __name__=='__main__':
    raise SystemExit(main())
