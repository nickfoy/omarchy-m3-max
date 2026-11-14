#!/usr/bin/env python3
"""Read-only hardware checks; public output is built from explicit fields."""
import argparse
import ctypes
import ctypes.util
import json
import os
from pathlib import Path
import platform
import struct
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def result(status, *evidence, **fields):
    return dict(status=status, evidence=list(evidence), **fields)


def read(path):
    try:
        return path.read_text().strip()
    except (OSError, UnicodeError):
        return None


def run(args):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=20, check=False)
        return p.stdout if p.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def read_hardware(root=Path('/')):
    compatible = read(root / 'proc/device-tree/compatible')
    mem = read(root / 'proc/meminfo')
    try:
        memory = round(int(next(x.split()[1] for x in mem.splitlines() if x.startswith('MemTotal:'))) / 1024**2)
    except (AttributeError, StopIteration, ValueError):
        memory = None
    release=read(root/'etc/os-release') or ''
    os_id=next((line.split('=',1)[1].strip(chr(34)) for line in release.splitlines() if line.startswith('ID=')),None)
    package=run(['pacman','-Q','omarchy'])
    omarchy_version=package.strip().split(' ',1)[1] if package and package.startswith('omarchy ') else None
    return dict(os_id=os_id,omarchy_version=omarchy_version,model_identifier=read(root/'sys/class/dmi/id/product_name'),
                compatible=[x for x in compatible.split('\0') if x] if compatible else [],
                architecture=platform.machine(), cpu_cores=os.cpu_count(), memory_gib=memory)


def hardware_gate(hw):
    evidence = ['Hardware requirements loaded from manifests/known-good.json; native Omarchy on Arch Linux ARM required.']
    try:
        manifest=json.loads((ROOT/'manifests/known-good.json').read_text())
        expected=manifest['hardware']
        model,board,soc,cores,memory=(expected[k] for k in ('model_identifier','board','soc','cpu_cores','memory_gib'))
    except (OSError,ValueError,KeyError,TypeError):
        return result('UNKNOWN', 'Known-good hardware manifest unavailable or invalid.')
    if not hw.get('model_identifier') or not hw.get('compatible'):
        return result('UNKNOWN', *evidence, 'Missing DMI or device-tree evidence.', hardware=hw)
    if hw['model_identifier'] != model or not {f'apple,{board}',f'apple,{soc}'}.issubset(hw['compatible']):
        return result('UNSUPPORTED', *evidence, hardware=hw)
    if not hw.get('architecture') or not hw.get('os_id'):
        return result('UNKNOWN', *evidence, 'OS or architecture evidence unavailable.', hardware=hw)
    if hw['os_id']!='archarm':
        return result('UNSUPPORTED', *evidence, 'Requires native Omarchy on Arch Linux ARM.', hardware=hw)
    if not hw.get('omarchy_version'):
        return result('UNKNOWN', *evidence, 'Omarchy package evidence unavailable.', hardware=hw)
    if hw.get('architecture') not in ('aarch64','arm64'):
        return result('UNSUPPORTED', *evidence, hardware=hw)
    if hw.get('cpu_cores') is None or hw.get('memory_gib') is None:
        return result('UNKNOWN', *evidence, hardware=hw)
    if hw['cpu_cores'] != cores or not memory-2 <= hw['memory_gib'] <= memory:
        return result('UNVERIFIED', *evidence, 'Board matches but configuration differs.', hardware=hw)
    return result('VERIFIED', *evidence, hardware=hw)


def egl_renderer():
    """Create an actual surfaceless EGL/GLES context; never infer from installed files."""
    display = context = surface = None
    try:
        egl = ctypes.CDLL(ctypes.util.find_library('EGL') or 'libEGL.so.1')
        gl = ctypes.CDLL(ctypes.util.find_library('GLESv2') or 'libGLESv2.so.2')
        P, I = ctypes.c_void_p, ctypes.c_int
        for name, restype, args in [
            ('eglGetPlatformDisplay',P,[ctypes.c_uint,P,ctypes.POINTER(I)]),
            ('eglInitialize',ctypes.c_uint,[P,ctypes.POINTER(I),ctypes.POINTER(I)]),
            ('eglBindAPI',ctypes.c_uint,[ctypes.c_uint]),
            ('eglChooseConfig',ctypes.c_uint,[P,ctypes.POINTER(I),ctypes.POINTER(P),I,ctypes.POINTER(I)]),
            ('eglCreatePbufferSurface',P,[P,P,ctypes.POINTER(I)]),
            ('eglCreateContext',P,[P,P,P,ctypes.POINTER(I)]),
            ('eglMakeCurrent',ctypes.c_uint,[P,P,P,P]),
            ('eglDestroyContext',ctypes.c_uint,[P,P]),
            ('eglDestroySurface',ctypes.c_uint,[P,P]),
            ('eglTerminate',ctypes.c_uint,[P])]:
            fn = getattr(egl,name); fn.restype=restype; fn.argtypes=args
        display = egl.eglGetPlatformDisplay(0x31DD, None, None)
        major, minor = I(), I()
        if not display or not egl.eglInitialize(display,ctypes.byref(major),ctypes.byref(minor)):
            return None
        egl.eglBindAPI(0x30A0)
        attrs=(I*9)(0x3033,1,0x3040,4,0x3024,8,0x3025,8,0x3038)
        cfg, count = P(), I()
        if not egl.eglChooseConfig(display,attrs,ctypes.byref(cfg),1,ctypes.byref(count)) or count.value == 0:
            return None
        surface=egl.eglCreatePbufferSurface(display,cfg,(I*5)(0x3057,1,0x3056,1,0x3038))
        context=egl.eglCreateContext(display,cfg,None,(I*3)(0x3098,2,0x3038))
        if not context or not surface or not egl.eglMakeCurrent(display,surface,surface,context):
            return None
        gl.glGetString.restype=ctypes.c_char_p; gl.glGetString.argtypes=[ctypes.c_uint]
        value=gl.glGetString(0x1F01)
        return value.decode('utf-8','replace') if value else None
    except (OSError, AttributeError):
        return None
    finally:
        if display:
            egl.eglMakeCurrent(display,None,None,None)
            if context: egl.eglDestroyContext(display,context)
            if surface: egl.eglDestroySurface(display,surface)
            egl.eglTerminate(display)


def gpu_result(renderer, drivers):
    evidence = ['Renderer queried from a live EGL/GLES context.', 'Render-node drivers queried from sysfs.']
    fields = dict(renderer=renderer, render_node_drivers=drivers)
    if renderer and any(x in renderer.lower() for x in ('llvmpipe','softpipe')):
        return result('FAIL', *evidence, 'Software rendering detected.', **fields)
    if not drivers or all(x is None for x in drivers):
        return result('FAIL', *evidence, 'No bound render-node driver.', **fields)
    if not renderer:
        return result('UNKNOWN', *evidence, 'Live renderer unavailable.', **fields)
    if 'Apple M3 Max' in renderer and 'asahi-g15' in drivers:
        return result('PASS', *evidence, **fields)
    return result('UNKNOWN', *evidence, 'Renderer and driver do not establish the expected pair.', **fields)


def vulkan_properties(raw):
    # Vulkan 1.0 VkPhysicalDeviceProperties starts with five uint32_t fields,
    # followed by deviceName[256]. UUID and limits are deliberately excluded.
    api, _driver, vendor, _device, kind=struct.unpack_from('=IIIII',raw)
    return dict(apiVersion=api,vendorID=vendor,deviceType=kind,
                name=bytes(raw[20:276]).split(b'\0',1)[0].decode('utf-8','replace'))


def vulkan_devices():
    """Loader enumeration only; this does not establish Vulkan compute support."""
    instance=ctypes.c_void_p()
    try:
        vk=ctypes.CDLL(ctypes.util.find_library('vulkan') or 'libvulkan.so.1')
        P=ctypes.c_void_p
        class CreateInfo(ctypes.Structure):
            _fields_=[('sType',ctypes.c_uint32),('pNext',P),('flags',ctypes.c_uint32),
                      ('pApplicationInfo',P),('enabledLayerCount',ctypes.c_uint32),
                      ('ppEnabledLayerNames',P),('enabledExtensionCount',ctypes.c_uint32),
                      ('ppEnabledExtensionNames',P)]
        vk.vkCreateInstance.argtypes=[ctypes.POINTER(CreateInfo),P,ctypes.POINTER(P)]
        vk.vkCreateInstance.restype=ctypes.c_int32
        vk.vkDestroyInstance.argtypes=[P,P]; vk.vkDestroyInstance.restype=None
        vk.vkEnumeratePhysicalDevices.argtypes=[P,ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(P)]
        vk.vkEnumeratePhysicalDevices.restype=ctypes.c_int32
        vk.vkGetPhysicalDeviceProperties.argtypes=[P,P]; vk.vkGetPhysicalDeviceProperties.restype=None
        info=CreateInfo(); info.sType=1
        if vk.vkCreateInstance(ctypes.byref(info),None,ctypes.byref(instance))!=0:
            return {'state':'unavailable','qualification':'enumeration only','devices':[]}
        count=ctypes.c_uint32()
        if vk.vkEnumeratePhysicalDevices(instance,ctypes.byref(count),None)!=0 or count.value>256:
            return {'state':'unavailable','qualification':'enumeration only','devices':[]}
        devices=(P*count.value)()
        code=vk.vkEnumeratePhysicalDevices(instance,ctypes.byref(count),devices)
        if code!=0:
            return {'state':'unavailable','qualification':'enumeration only','devices':[]}
        found=[]
        for device in devices[:count.value]:
            # Aligned storage exceeds the fixed Vulkan 1.0 properties structure.
            storage=(ctypes.c_uint64*512)()
            vk.vkGetPhysicalDeviceProperties(device,ctypes.byref(storage))
            found.append(vulkan_properties(bytes(storage)))
        return {'state':'available','qualification':'enumeration only; not compute qualification','devices':found}
    except (OSError,AttributeError):
        return {'state':'unavailable','qualification':'enumeration only','devices':[]}
    finally:
        if instance.value: vk.vkDestroyInstance(instance,None)


def verify_gpu():
    drivers=[]
    for node in sorted(Path('/sys/class/drm').glob('renderD*')):
        driver=node/'device/driver'
        drivers.append(driver.resolve().name if driver.exists() else None)
    value=gpu_result(egl_renderer(),drivers)
    value['hyprland_renderer']='unavailable: no stable structured renderer query'
    value['vulkan']=vulkan_devices()
    return value


def display_result(drm, monitors, lid_closed):
    evidence=['Kernel DRM connector states compared with hyprctl active monitors.']
    if not drm or monitors is None:
        return result('UNKNOWN', *evidence, 'DRM or compositor query unavailable.')
    failures=[]; unknown=[]
    if not any(name.startswith(('eDP','LVDS','DSI')) for name in drm):
        unknown.append('Expected internal DRM connector evidence unavailable.')
    for name,state in drm.items():
        internal=name.startswith(('eDP','LVDS','DSI'))
        if state != 'connected':
            if internal and lid_closed is not True:
                (failures if lid_closed is False and state=='disconnected' else unknown).append(name+': internal connector not confirmed connected')
            continue
        m=next((m for m in monitors if m.get('name')==name),None)
        active=m and not m.get('disabled',False) and m.get('width',0)>0 and m.get('height',0)>0
        if internal and lid_closed is True and not active:
            continue
        if not active:
            (unknown if internal and lid_closed is None else failures).append(name+': connected but inactive')
        elif m.get('refreshRate') == 0:
            failures.append(name+': zero refresh mode')
        elif internal and lid_closed is not True:
            refresh=m.get('refreshRate')
            if refresh is None: unknown.append(name+': refresh unavailable')
            elif not 115 <= refresh <= 125: failures.append(name+': internal refresh is not approximately 120 Hz')
    return result('FAIL' if failures else 'UNKNOWN' if unknown else 'PASS', *evidence, *failures, *unknown, connectors=drm)


def lid_state(root=Path('/')):
    lids=[read(p) for p in (root/'proc/acpi/button/lid').glob('*/state')]
    if any('closed' in (s or '') for s in lids): return True
    if any('open' in (s or '') for s in lids): return False
    for p in (root/'sys/class/input').glob('*/capabilities/sw'):
        try:
            has_lid=int((read(p) or '').split()[-1],16)&1
        except (ValueError, IndexError):
            continue
        if has_lid:
            state=run(['busctl','--timeout=2','get-property','org.freedesktop.login1',
                       '/org/freedesktop/login1','org.freedesktop.login1.Manager','LidClosed'])
            return True if state and state.strip()=='b true' else False if state and state.strip()=='b false' else None
    return None


def verify_displays():
    drm={}
    for p in Path('/sys/class/drm').glob('card*-*/status'):
        drm[p.parent.name.split('-',1)[1]]=read(p)
    raw=run(['hyprctl','monitors','all','-j'])
    try:
        monitors=json.loads(raw) if raw else None
        if not isinstance(monitors,list): monitors=None
    except ValueError: monitors=None
    lid=lid_state()
    value=display_result(drm,monitors,lid)
    value['lid_closed']=lid
    return value


def packages():
    output=run(['pacman','-Q'])
    return dict(line.split(' ',1) for line in output.splitlines() if ' ' in line) if output is not None else None


def inventory():
    hw=read_hardware()
    pkgs=packages()
    complete=pkgs is not None and hardware_gate(hw)['status']=='VERIFIED'
    return result('PASS' if complete else 'UNKNOWN', 'Public-safe allowlist: hardware identity, kernel, package versions, connector state only.', hardware=hw, kernel=platform.release(), packages=pkgs, connectors={p.parent.name.split('-',1)[1]:read(p) for p in Path('/sys/class/drm').glob('card*-*/status')})


def package_comparison(before, after, critical_only=False):
    differences={k:{'baseline':before.get(k),'current':after.get(k)} for k in sorted(before.keys() if critical_only else before.keys()|after.keys()) if before.get(k)!=after.get(k)}
    return result('DIFFERENT' if differences else 'PASS', 'Package differences are observations, not a failure diagnosis.', differences=differences)


def capture(output, include_root=False):
    output=Path(output).expanduser().resolve()
    if output==ROOT or ROOT in output.parents:
        raise ValueError('Baseline captures must be outside the repository.')
    previous_umask=os.umask(0o077)
    try:
        output.mkdir(mode=0o700,parents=True,exist_ok=False)
        os.chmod(output,0o700)
        data=inventory()
        (output/'inventory.json').write_text(json.dumps(data,indent=2)+'\n')
        configs=[Path.home()/'.config/hypr',Path.home()/'.config/omarchy']
        if include_root:
            configs += [Path('/etc/pacman.conf'),Path('/etc/pacman.d'),Path('/var/lib/pacman/local')]
        with tarfile.open(output/'private-configs.tar.gz','w:gz') as archive:
            for i,path in enumerate(configs):
                if path.exists(): archive.add(path,arcname=f'config-{i}',recursive=True)
        for p in output.iterdir(): os.chmod(p,0o600)
        status='PASS' if data.get('status')=='PASS' else 'UNKNOWN'
        return result(status,'Private files captured; completeness follows the inventory status, not archive creation.','Never automatically promoted to known-good. Archive may contain sensitive configuration; do not publish.', inventory_status=data.get('status','UNKNOWN'))
    finally:
        os.umask(previous_umask)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for name in ('inventory','verify-gpu','verify-displays','check-hardware','capture-baseline','compare-baseline'):
        p=sub.add_parser(name); p.add_argument('--json',action='store_true')
        if name=='capture-baseline':
            p.add_argument('--output',required=True); p.add_argument('--include-root',action='store_true',help='Read system package database/configs without sudo')
        if name=='compare-baseline': p.add_argument('baseline',type=Path,nargs='?',default=ROOT/'manifests')
    args=parser.parse_args(argv)
    try:
        if args.command=='inventory': data=inventory()
        elif args.command=='verify-gpu': data=verify_gpu()
        elif args.command=='verify-displays': data=verify_displays()
        elif args.command=='check-hardware': data=hardware_gate(read_hardware())
        elif args.command=='capture-baseline': data=capture(args.output,args.include_root)
        else:
            gate=hardware_gate(read_hardware())
            if gate['status']!='VERIFIED': data=gate
            else:
                baseline_path=args.baseline/'inventory.json'
                if not baseline_path.exists(): baseline_path=args.baseline/'known-good.json'
                baseline=json.loads(baseline_path.read_text())
                current=packages()
                data=package_comparison(baseline['packages'],current,critical_only=baseline_path.name=='known-good.json') if baseline.get('packages') is not None and current is not None else result('UNKNOWN','Package inventory unavailable.')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        data=result('UNKNOWN', 'Operation could not obtain required evidence.', error=type(exc).__name__)
    print(json.dumps(data,indent=2) if args.json else '\n'.join([data['status']]+data.get('evidence',[])))
    return 0 if data['status'] in ('PASS','VERIFIED','DIFFERENT') else 1 if data['status'] in ('FAIL','UNSUPPORTED') else 2

if __name__=='__main__':
    raise SystemExit(main())
