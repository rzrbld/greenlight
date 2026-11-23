#!/usr/bin/env python3
"""Download exact Debian source inputs for the redistributed runtime packages.
Run as root in the same runtime image that produced manifest.json.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text())
output = Path(sys.argv[2]).resolve()
output.mkdir(parents=True, exist_ok=True)
for p in Path('/etc/apt/sources.list.d').glob('*.sources'):
    p.write_text(re.sub(r'^Types: deb$', 'Types: deb deb-src', p.read_text(), flags=re.M))
subprocess.run(['apt-get', 'update'], check=True)
sources = set()
for package, version in manifest['debian_packages'].items():
    actual = subprocess.check_output(['dpkg-query','-W','-f=${Version}',package], text=True)
    if actual != version:
        raise RuntimeError('Runtime source/version mismatch: '+package)
    source = subprocess.check_output(['dpkg-query','-W','-f=${source:Package}=${source:Version}',package], text=True)
    sources.add(source)
for source in sorted(sources):
    subprocess.run(['apt-get','--download-only','--only-source','source',source],cwd=output,check=True)
(output/'source-packages.json').write_text(json.dumps(sorted(sources),indent=2)+'\n')
print('Downloaded corresponding sources for',len(sources),'Debian source packages')
