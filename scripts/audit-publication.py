#!/usr/bin/env python3
"""Audit tracked/staged public text; emit paths/rule names, never matched secrets."""
import argparse
import ipaddress
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
PATTERNS={
    'private-key': re.compile(r'-----BEGIN (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----'),
    'github-token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})\b'),
    'cloud-token': re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'tailscale-token': re.compile(r'\btskey-[A-Za-z0-9-]{15,}\b'),
    'api-token': re.compile(r'\bsk-[A-Za-z0-9_-]{24,}\b'),
    'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
    'home-path': re.compile(r'/(?:home|Users)/[A-Za-z0-9_.-]+(?:/|\b)'),
    'uuid': re.compile(r'\b[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}\b'),
    'mac-address': re.compile(r'\b(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b'),
    'ssh-identity': re.compile(r'\bssh-(?:rsa|ed25519)\s+[A-Za-z0-9+/=]{30,}'),
}
FORBIDDEN=('.pkg.tar','.tar.gz','.tar.xz','.tar.zst','.dtb','.img','.efi','.bin','.log','.pem','.key','.p12','.pfx')


def findings(path,data):
    result=[]
    if any(s in path for s in FORBIDDEN) or any(p in Path(path).parts for p in ('private','baselines','backups','diagnostics','.ssh','.aws')):
        result.append('private-or-binary-artifact')
    if b'\0' in data: return result+['binary-content']
    text=data.decode('utf-8',errors='replace')
    # These are public upstream firmware BUILD identities, not host UUIDs.
    # Retain them only in the reviewed source patches that enforce identity.
    firmware_ids={'DDF38191'+'-93B3-324A-BC8F-643006F5AC82','F493F03E'+'-CC40-3D89-9A08-5F259BA2B246'}
    for name,pattern in PATTERNS.items():
        matches=pattern.findall(text)
        if name=='uuid' and path in ('patches/linux-aurora-j514m.patch','patches/m1n1-aurora-j514m.patch'):
            matches=[v for v in matches if v not in firmware_ids]
        # PR457 retains public firmware identity fixtures as unchanged context.
        if name=='uuid' and path=='patches/linux-aurora-j514m-panel.patch':
            fixtures=firmware_ids | {'F493F03E'+'-CC40-3D89-9A08-5F259BA2B247'}
            matches=[v for v in matches if v.upper() not in fixtures]
        if matches:result.append(name)
    # This manifest is generated exclusively from pacman name/version fields.
    # Dotted package versions are not network endpoints.
    if path=='manifests/packages.txt' and all(re.fullmatch(r'[A-Za-z0-9@+_.-]+ [^\s/]+',line) for line in text.splitlines()):
        return result
    for raw in re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b',text):
        try:
            addr=ipaddress.ip_address(raw)
            if addr.is_private and not addr.is_loopback or int(addr)>>22 == 401:
                result.append('private-network-address');break
        except ValueError:pass
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--staged',action='store_true');args=parser.parse_args()
    command=['git','diff','--cached','--name-only','-z','--diff-filter=ACMR'] if args.staged else ['git','ls-files','--cached','--others','--exclude-standard','-z']
    names=sorted(set(subprocess.check_output(command,cwd=ROOT).decode().split('\0'))-{''})
    errors=[]
    for name in names:
        p=ROOT/name
        if p.is_symlink():errors.append((name,'symlink-not-reviewed'));continue
        if not p.is_file():continue
        data=subprocess.check_output(['git','show',':'+name],cwd=ROOT) if args.staged else p.read_bytes()
        errors.extend((name,rule) for rule in findings(name,data))
    for name,rule in errors:print(name+': '+rule)
    print(f'Audited {len(names)} public files; {len(errors)} findings. Manual review and independent scanning remain required.')
    return bool(errors)

if __name__=='__main__':raise SystemExit(main())
