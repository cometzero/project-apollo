import hashlib
from pathlib import Path
import struct
from types import SimpleNamespace

import pytest
from scripts.autosd_demo import image_architecture as target


def pe(*, uki=False, machine=0xAA64):
    names = ['.linux','.initrd','.cmdline'] if uki else ['.text']
    data = bytearray(512*(1+len(names)))
    data[:2] = b'MZ'
    struct.pack_into('<I',data,60,64)
    data[64:68] = b'PE\0\0'
    struct.pack_into('<HH',data,68,machine,len(names))
    struct.pack_into('<H',data,84,240)
    struct.pack_into('<H',data,88,0x20B)
    struct.pack_into('<II',data,144,(len(names)+1)*4096,512)
    struct.pack_into('<H',data,156,10)
    for i,name in enumerate(names):
        entry = 328+i*40
        data[entry:entry+len(name)] = name.encode()
        struct.pack_into('<IIII',data,entry+8,512,(i+1)*4096,512,(i+1)*512)
    if uki:
        data[512+56:512+60] = b'ARM\x64'
    return bytes(data)


def test_pe_rejects_wrong_architecture_and_truncation():
    good = pe(uki=True)
    assert target.inspect_pe(good,uki=True)['machine']=='aarch64'
    with pytest.raises(ValueError,match='0x8664'):
        target.inspect_pe(pe(machine=0x8664))
    for cut in (0,63,75,200,511,len(good)-1):
        with pytest.raises(ValueError):
            target.inspect_pe(good[:cut],uki=True)
    malformed = bytearray(good)
    struct.pack_into('<I',malformed,60,0xFFFFFF00)
    with pytest.raises(ValueError,match='PE header'):
        target.inspect_pe(malformed)


def test_signed_pe_is_inspected_without_claiming_trust():
    data = bytearray(pe())
    struct.pack_into('<I',data,196,5)
    struct.pack_into('<II',data,232,len(data),8)
    data.extend(b'CERTDATA')
    assert target.inspect_pe(data)['machine']=='aarch64'
    with pytest.raises(ValueError,match='certificate'):
        target.inspect_pe(data[:-1])


def test_slot_policy_matches_bootctl_priority_and_ties():
    assert target.selected_slot({'state':'uninitialized'})=='ukiboot_a'
    control = {'state':'valid','slots':[{'priority':15,'tries_remaining':0,'successful_boot':0},
                                       {'priority':14,'tries_remaining':7,'successful_boot':0}]}
    assert target.selected_slot(control)=='ukiboot_b'
    control['slots'][0]['successful_boot']=1
    assert target.selected_slot(control)=='ukiboot_a'
    control['slots'][1]['priority']=15
    assert target.selected_slot(control)=='ukiboot_a'
    with pytest.raises(ValueError,match='Invalid'):
        target.selected_slot({'state':'invalid'})


@pytest.mark.parametrize('bad_slot,bad_loader,selected_b',[(False,False,False),(True,False,False),(False,True,False),(False,False,True)])
def test_disk_gate_is_read_only_and_all_populated_slots_checked(tmp_path,monkeypatch,bad_slot,bad_loader,selected_b):
    image=tmp_path/'disk.img'
    blob=bytearray(12288)
    blob[4096:4096+len(pe(uki=True))]=pe(uki=True)
    if bad_slot:
        blob[8192:8192+len(pe(uki=True))]=pe(uki=True,machine=0x8664)
    image.write_bytes(blob)
    before=hashlib.sha256(image.read_bytes()).digest()
    control={'state':'uninitialized'}
    if selected_b:
        control={'state':'valid','slots':[{'priority':0,'tries_remaining':0,'successful_boot':0},
                                         {'priority':15,'tries_remaining':7,'successful_boot':0}]}
    monkeypatch.setattr(target,'inspect_disk',lambda path:{'bootctl':control,'partitions':{
        'efi':{'offset':0,'size':4096},'ukiboot_a':{'offset':4096,'size':4096},'ukiboot_b':{'offset':8192,'size':4096}}})
    def run(args,**kwargs):
        if args[0]=='mdir':
            return SimpleNamespace(returncode=0,stdout='::/EFI/BOOT/BOOTAA64.EFI\n',stderr='')
        assert args[0]=='mcopy'
        Path(args[-1]).write_bytes(pe(machine=0x8664 if bad_loader else 0xAA64))
        return SimpleNamespace(returncode=0,stdout='',stderr='')
    monkeypatch.setattr(target.subprocess,'run',run)
    if bad_slot or bad_loader or selected_b:
        with pytest.raises(ValueError,match='0x8664|empty'):
            target.inspect_image_architecture(image)
    else:
        result=target.inspect_image_architecture(image)
        assert result['slots']['ukiboot_b']=={'state':'empty'}
        assert '/EFI/BOOT/BOOTAA64.EFI' in result['efi']
    assert hashlib.sha256(image.read_bytes()).digest()==before


def test_arm64_stub_does_not_hide_wrong_kernel_or_absent_uki_sections():
    with pytest.raises(ValueError,match='Missing or uninitialized UKI section'):
        target.inspect_pe(pe(),uki=True)
    data=bytearray(pe(uki=True))
    data[568:572]=b'x64!'
    with pytest.raises(ValueError,match='kernel Image'):
        target.inspect_pe(data,uki=True)
