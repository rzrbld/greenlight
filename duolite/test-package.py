#!/usr/bin/env python3
"""Check the actual installable app archive, not a synthetic launcher fixture."""
import json
import stat
import struct
import sys
import zipfile
from pathlib import PurePosixPath

with zipfile.ZipFile(sys.argv[1]) as z:
    names=z.namelist()
    assert [n for n in names if n.endswith('.sh')]==['Greenlight Duo.sh']
    assert 'Greenlight Duo.png' in names
    assert 'greenlight/launcher.py' in names
    for entry in z.infolist():
        p=PurePosixPath(entry.filename)
        assert not p.is_absolute() and '..' not in p.parts
        assert not stat.S_ISLNK(entry.external_attr>>16),'No symlinks on exFAT'
        assert not any(x in p.parts for x in ['.git','.cache','__pycache__'])
        data=z.read(entry)
        if data[:4]==b'\x7fELF':assert struct.unpack_from('<H',data,18)[0]==183,'Non-ARM64 binary: '+entry.filename
    m=json.loads(z.read('greenlight/runtime/manifest.json'))
    assert m['architecture']=='aarch64'
    assert 'libseat.so.1' in [PurePosixPath(p).name for p in m['files']]
    for driver in ['libEGL.so.1','libGLESv2.so.2','libgbm.so.1','libdrm.so.2','libc.so.6']:
        assert 'greenlight/runtime/lib/'+driver not in names,'OS driver/core must stay native: '+driver
    assert z.read('greenlight/runtime/licenses/weston_arm64.txt')
print('PASS: native app launcher, ARM64 ELF payloads, libseat, licenses, exFAT files and native OS GPU/core isolation')
