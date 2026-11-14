#!/usr/bin/env python3
"""Check local Markdown links and agent references without running host changes."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]

def main():
    errors=[]
    for p in ROOT.rglob('*.md'):
        if '.git' in p.parts:continue
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            if '://' in link or link.startswith('#') or link.startswith('mailto:'):continue
            target=link.split('#',1)[0]
            if target and not (p.parent/target).exists():errors.append(f'{p.relative_to(ROOT)}: missing link {target}')
    for name in ['AGENTS.md','prompts/install.md','prompts/update.md']:
        text=(ROOT/name).read_text()
        for ref in re.findall(r'\b(?:scripts|manifests|config|docs)/[A-Za-z0-9_./-]+\.(?:sh|py|json|md)',text):
            if not (ROOT/ref).exists():errors.append(name+': missing '+ref)
        if 'check-hardware.sh' not in text:errors.append(name+': no hardware gate')
    for line in errors:print(line)
    print(f'Document/reference check: {len(errors)} errors')
    return bool(errors)
if __name__=='__main__':raise SystemExit(main())
