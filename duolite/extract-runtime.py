#!/usr/bin/env python3
"""Collect ARM64 desktop dependencies; retain the handheld's native GPU ABI.
Run in Dockerfile.runtime. The collector never executes target binaries.
"""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--electron', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
out = a.output
out.mkdir(parents=True, exist_ok=True)
search = [a.electron, Path('/usr/lib/aarch64-linux-gnu'), Path('/lib/aarch64-linux-gnu'), Path('/usr/lib/aarch64-linux-gnu/weston')]
external = re.compile(r'^(ld-linux-|lib(c|m|pthread|dl|rt|resolv|util|anl)\.so|lib(stdc\+\+|gcc_s|atomic|drm[^/]*|gbm|EGL|GLES[^/]*|GLdispatch|gallium[^/]*|LLVM[^/]*|vulkan)\.so)')
seen = set()
external_names = set()
owners = {}
files = []

def owner(path):
    for name in [str(path), str(path).replace('/usr/lib/', '/lib/', 1)]:
        r = subprocess.run(['dpkg-query', '-S', name], text=True, capture_output=True)
        if r.returncode == 0:
            pkg = r.stdout.splitlines()[0].split(': ', 1)[0]
            owners[pkg] = subprocess.check_output(['dpkg-query', '-W', '-f=${Version}', pkg], text=True)
            return

def needed(path):
    header = subprocess.check_output(['readelf', '-h', str(path)], text=True)
    if 'AArch64' not in header:
        raise RuntimeError('Not ARM64: ' + str(path))
    dynamic = subprocess.check_output(['readelf', '-d', str(path)], text=True)
    return re.findall(r'\(NEEDED\).*\[(.*?)\]', dynamic)

def add(src, dest):
    src = src.resolve()
    key = (str(src), str(dest))
    if key in seen:
        return
    seen.add(key)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    dest.chmod(0o755)
    owner(src)
    files.append(str(dest.relative_to(out)))
    for name in needed(src):
        dependency(name)

def dependency(name):
    if external.match(name):
        external_names.add(name)
        return
    found = next((d/name for d in search if (d/name).exists()), None)
    if found is None:
        raise RuntimeError('Missing dependency ' + name)
    if found.parent != a.electron:
        add(found, out/'lib'/name)

for name in ['weston', 'seatd', 'dbus-daemon']:
    src=Path('/usr/sbin/seatd') if name=='seatd' else Path('/usr/bin')/name
    add(src, out/'bin'/name)
weston_modules=next(d for d in Path('/usr/lib/aarch64-linux-gnu').glob('libweston-*') if d.is_dir() and (d/'drm-backend.so').exists())
for path in [weston_modules/'drm-backend.so',weston_modules/'gl-renderer.so',Path('/usr/lib/aarch64-linux-gnu/weston/kiosk-shell.so')]:
    add(path, out/'modules'/path.name)
for path in a.electron.iterdir():
    if path.is_file():
        with path.open('rb') as f:
            elf = f.read(4) == b'\x7fELF'
        if elf:
            for name in needed(path):
                dependency(name)
for name in ['libnssckbi.so', 'libsoftokn3.so', 'libfreebl3.so', 'libfreeblpriv3.so']:
    src=Path('/usr/lib/aarch64-linux-gnu')/name
    add(src, out/'lib'/name)
    if src.with_suffix('.chk').exists(): shutil.copyfile(src.with_suffix('.chk'),(out/'lib'/name).with_suffix('.chk'))
for src, rel in [('/usr/share/X11/xkb', 'share/X11/xkb'), ('/usr/share/fonts/truetype/dejavu', 'share/fonts'), ('/usr/share/glib-2.0/schemas', 'share/glib-2.0/schemas')]:
    shutil.copytree(src, out/rel, dirs_exist_ok=True, symlinks=False)
    for path in Path(src).rglob('*'):
        if path.is_file():
            owner(path)
            break
for pkg in owners:
    src = Path('/usr/share/doc')/pkg.split(':')[0]/'copyright'
    if src.exists():
        dest = out/'licenses'/(pkg.replace(':', '_')+'.txt')
        dest.parent.mkdir(exist_ok=True)
        shutil.copyfile(src, dest)
manifest = {'architecture': 'aarch64', 'debian_packages': owners, 'os_provided_libraries': sorted(external_names), 'files': sorted(files)}
(out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
print('Runtime files:', len(files), 'packages:', len(owners), 'OS libraries:', ','.join(sorted(external_names)))
