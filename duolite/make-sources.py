#!/usr/bin/env python3
"""Archive the fork, dependency source packages and the pinned LGPL FFmpeg tree."""
import hashlib
import json
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

repo=Path(__file__).resolve().parents[1]
out=repo/'duolite/build/sources'
out.mkdir(parents=True,exist_ok=True)
pins=json.loads((repo/'duolite/runtime-sources.json').read_text())
electron=json.loads((repo/'node_modules/electron/package.json').read_text())['version']
assert electron==pins['electron'],'Update runtime source pins with the Electron dependency'
ffmpeg=out/'ffmpeg.tar.gz'
url='https://chromium.googlesource.com/chromium/third_party/ffmpeg/+archive/'+pins['ffmpeg_revision']+'.tar.gz'
with urllib.request.urlopen(url,timeout=180) as response, ffmpeg.open('wb') as f:
    shutil.copyfileobj(response,f)
with tarfile.open(ffmpeg) as t:
    assert t.getmembers(),'Empty FFmpeg source response'
source=out/'greenlight-source.tar'
subprocess.run(['git','-C',str(repo),'archive','--format=tar','--output='+str(source),'HEAD'],check=True)
pins['ffmpeg_sha256']=hashlib.file_digest(ffmpeg.open('rb'),'sha256').hexdigest()
pins['fork_commit']=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
(out/'provenance.json').write_text(json.dumps(pins,indent=2)+'\n')
version=json.loads((repo/'packages/desktop/package.json').read_text())['version']
archive=repo/('duolite/build/Greenlight-Duo-'+version+'-sources.tar.gz')
with tarfile.open(archive,'w:gz') as t:
    for p in sorted(out.iterdir()):t.add(p,arcname='sources/'+p.name)
print(archive)
