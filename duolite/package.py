#!/usr/bin/env python3
"""Create one native-app ZIP for Slopetanium, with no symlink requirements."""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
build = repo/'duolite/build'
stage = build/'package'
if stage.exists():
    shutil.rmtree(stage)
stage.mkdir(parents=True)
app = stage/'greenlight'
shutil.copytree(build/'electron/linux-arm64-unpacked', app/'electron', symlinks=False)
shutil.copytree(build/'runtime', app/'runtime', symlinks=False)
shutil.copyfile(repo/'duolite/launcher.py', app/'launcher.py')
shutil.copyfile(repo/'duolite/Greenlight.sh', stage/'Greenlight Duo.sh')
shutil.copyfile(repo/'packages/desktop/renderer/public/images/logo.png', stage/'Greenlight Duo.png')
shutil.copyfile(repo/'LICENSE', app/'LICENSE-Greenlight')
version = json.loads((repo/'packages/desktop/package.json').read_text())['version']
manifest = {'name':'Greenlight Duo', 'version':version, 'architecture':'aarch64',
    'launcher':'Greenlight Duo.sh', 'repository':'rzrbld/greenlight',
    'upstream':'unknownskl/greenlight v2.4.2', 'profile':'XDG_CONFIG_HOME/greenlight-duo'}
(app/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
files = sorted(p for p in stage.rglob('*') if p.is_file())
assert len([p for p in files if p.suffix=='.sh'])==1, 'Ambiguous app launcher'
assert not any(p.is_symlink() for p in stage.rglob('*')), 'exFAT cannot retain symlinks'
checksums = ''.join(hashlib.file_digest(p.open('rb'),'sha256').hexdigest()+'  '+str(p.relative_to(stage))+'\n' for p in files)
(stage/'SHA256SUMS').write_text(checksums)
release = build/('Greenlight-Duo-'+version+'-linux-arm64.zip')
with zipfile.ZipFile(release, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for p in sorted(stage.rglob('*')):
        if p.is_file():
            z.write(p, str(p.relative_to(stage)))
print(release)
