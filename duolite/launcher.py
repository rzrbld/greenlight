#!/usr/bin/env python3
"""Run the app-owned desktop session; never install a system service."""
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT/'runtime'
PROFILE = Path(os.environ.get('XDG_CONFIG_HOME', '/data/home/.config'))/'greenlight-duo'
CACHE = Path(os.environ.get('XDG_CACHE_HOME', '/data/home/.cache'))/'greenlight-duo'

def hardware():
    values = dict(os.environ)
    path = Path('/etc/banana/hardware.env')
    if path.exists():
        for line in path.read_text().splitlines():
            m = re.fullmatch(r'(?:export )?(BANANA_\w+)=(\S+)', line)
            if m:
                values.setdefault(m[1], m[2].strip('"\''))
    top, bottom = values.get('BANANA_TOP', ''), values.get('BANANA_BOTTOM', '')
    if not re.fullmatch(r'[A-Za-z]+-\d+', top) or not re.fullmatch(r'[A-Za-z]+-\d+', bottom):
        raise RuntimeError('Greenlight Duo needs the OS panel metadata in /etc/banana/hardware.env')
    rotation = int(values.get('BANANA_TOP_ROTATION', '0'))
    if rotation not in (0, 90, 180, 270):
        raise RuntimeError('Invalid panel rotation')
    return top, bottom, rotation

def wait_path(path, process, seconds=15):
    deadline = time.monotonic()+seconds
    while time.monotonic()<deadline:
        if process.poll() is not None:
            raise RuntimeError('Desktop runtime exited; see '+str(CACHE))
        if path.exists():
            return
        time.sleep(.1)
    raise RuntimeError('Desktop runtime did not become ready; see '+str(CACHE))

def main():
    if os.uname().machine != 'aarch64':
        raise RuntimeError('This package is for Linux ARM64')
    PROFILE.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    top, bottom, rotation = hardware()
    # OS metadata rotates app buffers; Weston describes the inverse output transform.
    output_rotation = (-rotation) % 360
    run = Path(tempfile.mkdtemp(prefix='greenlight-', dir='/run'))
    children, logs = [], []
    env = dict(os.environ)
    env.update({
        'GREENLIGHT_DUOLITE': '1', 'XDG_RUNTIME_DIR': str(run),
        'XDG_CONFIG_HOME': str(PROFILE.parent), 'XDG_CACHE_HOME': str(CACHE.parent),
        'XDG_SESSION_TYPE': 'wayland', 'WAYLAND_DISPLAY': 'greenlight-wayland',
        'LIBSEAT_BACKEND': 'seatd', 'SEATD_SOCK': '/run/seatd.sock', 'SEATD_VTBOUND': '0',
        'LD_LIBRARY_PATH': str(RUNTIME/'lib')+(':'+env['LD_LIBRARY_PATH'] if env.get('LD_LIBRARY_PATH') else ''),
        'XKB_CONFIG_ROOT': str(RUNTIME/'share/X11/xkb'),
        'GSETTINGS_SCHEMA_DIR': str(RUNTIME/'share/glib-2.0/schemas'),
        'WESTON_MODULE_MAP': ';'.join(name+'='+str(RUNTIME/'modules'/name) for name in ['drm-backend.so','gl-renderer.so','kiosk-shell.so']),
        'LANG': 'C.UTF-8', 'GSETTINGS_BACKEND':'memory',
    })
    for key in ['DISPLAY', 'EGL_PLATFORM', 'DEBUG']:
        env.pop(key, None)
    fontconfig = run/'fonts.conf'
    fontconfig.write_text('<fontconfig><dir>'+str(RUNTIME/'share/fonts')+'</dir><dir>/usr/share/fonts</dir><cachedir>'+str(CACHE/'fonts')+'</cachedir></fontconfig>')
    env['FONTCONFIG_FILE'] = str(fontconfig)
    config = run/'weston.ini'
    config.write_text('[core]\nxwayland=false\nrequire-input=false\nidle-time=0\n'
        '[output]\nname='+top+'\nmode=preferred\ntransform='+('normal' if output_rotation==0 else 'rotate-'+str(output_rotation))+'\nscale=2\n'
        '[output]\nname='+bottom+'\nmode=off\n')
    busconfig = run/'dbus.conf'
    busconfig.write_text('<busconfig><type>session</type><listen>unix:path='+str(run/'bus')+'</listen><auth>EXTERNAL</auth>'
        '<policy context="default"><allow send_destination="*" eavesdrop="true"/><allow eavesdrop="true"/><allow own="*"/></policy></busconfig>')
    env['DBUS_SESSION_BUS_ADDRESS'] = 'unix:path='+str(run/'bus')
    def start(args, name):
        log = (CACHE/(name+'.log')).open('w')
        logs.append(log)
        proc = subprocess.Popen([str(x) for x in args], env=env, stdout=log, stderr=subprocess.STDOUT)
        children.append(proc)
        return proc
    def stop(signum, frame):
        raise SystemExit(128+signum)
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    try:
        # Debian seatd 0.7 uses its standard transient socket, not a -s flag.
        # Reuse an existing server without taking ownership of its lifetime.
        if not Path('/run/seatd.sock').exists():
            seatd = start([RUNTIME/'bin/seatd'], 'seatd')
            wait_path(Path('/run/seatd.sock'), seatd)
        bus = start([RUNTIME/'bin/dbus-daemon', '--nofork', '--nopidfile', '--config-file='+str(busconfig)], 'dbus')
        wait_path(run/'bus', bus)
        compositor = start([RUNTIME/'bin/weston', '--backend=drm-backend.so', '--shell=kiosk-shell.so', '--config='+str(config), '--socket=greenlight-wayland', '--log='+str(CACHE/'weston.log')], 'desktop')
        wait_path(run/'greenlight-wayland', compositor)
        args = [ROOT/'electron/greenlight-duo', '--no-sandbox', '--ozone-platform=wayland', '--use-gl=angle', '--use-angle=gles', '--alsa-output-device=default', '--alsa-input-device=default', '--fullscreen']
        if os.environ.get('GREENLIGHT_DUO_DIAGNOSTICS') == '1':
            args += ['--remote-debugging-address=127.0.0.1', '--remote-debugging-port=9225']
        app = start(args, 'app')
        return app.wait()
    finally:
        for proc in reversed(children):
            if proc.poll() is None:
                proc.terminate()
        for proc in reversed(children):
            try:
                proc.wait(timeout=4)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
        for log in logs:
            log.close()
        shutil.rmtree(run, ignore_errors=True)

if __name__ == '__main__':
    raise SystemExit(main())
