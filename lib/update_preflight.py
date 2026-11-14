#!/usr/bin/env python3
"""Conservative report-only package plan assessment; never installs packages."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / 'config/pacman/protection-policy.json').read_text())
CODES = {'SAFE': 0, 'REVIEW REQUIRED': 2, 'BLOCKED': 1}

def atom(value):
    return re.split(r'[<>=]', value, maxsplit=1)[0]

def assess(plan, scope='pacman'):
    blocked, review = [], []
    if not isinstance(plan, dict):
        return {'status':'BLOCKED','reasons':['Plan must be an object.'],'exit_code':1}
    if plan.get('schema_version') != 1: blocked.append('Unknown or missing plan schema.')
    if plan.get('hardware_status') != 'VERIFIED': blocked.append('Hardware baseline is not verified.')
    for key in ('complete','solver_success'):
        if plan.get(key) is not True: blocked.append(f'{key} must be explicitly true.')
    if plan.get('metadata_fresh') is not True: review.append('Repository metadata freshness is not established.')
    if plan.get('ignored_packages'): blocked.append('Ignored packages can produce an unsupported partial upgrade; use a complete transaction.')
    if plan.get('incompatibilities'): blocked.append('Known incompatibilities: ' + str(plan['incompatibilities']))
    transactions = plan.get('transactions')
    if not isinstance(transactions,list): blocked.append('Missing transaction list.'); transactions=[]
    protected={name:group['reason'] for group in POLICY['groups'].values() for name in group['packages']}
    for item in transactions:
        if not isinstance(item,dict) or not all(k in item for k in ('name','old_version','new_version','operation','depends','provides','conflicts','replaces','files')):
            blocked.append('Incomplete transaction entry.'); continue
        if not all(item[k] is None or isinstance(item[k],str) for k in ('old_version','new_version')):
            blocked.append('Invalid version metadata.'); continue
        if item['operation'] not in ('install','upgrade','remove','downgrade','reinstall'):
            blocked.append('Unknown transaction operation.'); continue
        for field in ('name','operation'):
            if not isinstance(item[field],str): blocked.append('Invalid transaction field.')
        if not isinstance(item['name'],str): continue
        if item['operation'] in ('remove','downgrade','reinstall'): review.append(f"{item['name']}: {item['operation']} requires review.")
        related={item['name']}
        for field in ('depends','provides','conflicts','replaces'):
            values=item.get(field,[])
            if not isinstance(values,list) or not all(isinstance(v,str) for v in values):
                blocked.append('Invalid dependency metadata.'); continue
            related.update(atom(v) for v in values)
        for name in sorted(related & protected.keys()): review.append(f"{item['name']} touches {name}: {protected[name]}.")
        files=item.get('files',[])
        if not isinstance(files,list) or not all(isinstance(f,str) for f in files): blocked.append('Invalid file metadata.'); continue
        if any(f.lstrip('/').startswith(tuple(POLICY['protected_paths'])) for f in files): review.append(f"{item['name']} touches protected boot/platform configuration paths.")
    comparisons=plan.get('repository_comparisons',[])
    if not isinstance(comparisons,list):
        blocked.append('Invalid repository comparison metadata.'); comparisons=[]
    for comparison in comparisons:
        if not isinstance(comparison,dict) or not all(isinstance(comparison.get(k),str) for k in ('name','installed_version','repository_version','relation')):
            blocked.append('Incomplete repository comparison metadata.'); continue
        if comparison['relation']=='local-newer': review.append(f"{comparison['name']}: installed {comparison['installed_version']} is newer than repository {comparison['repository_version']}; retain local provenance during review.")
    if plan.get('runtime_uninspected'):
        review.append('Candidate add list solved; incoming file/scriptlet metadata and full removal operations remain uninspected. This is not an exact transaction approval.')
    if scope=='omarchy': review.append('Outer Omarchy checkout, keyrings, migrations, removals, AUR and tool updates require separate review; this package report does not approve them.')
    status='BLOCKED' if blocked else 'REVIEW REQUIRED' if review else 'SAFE'
    return {'status':status,'exit_code':CODES[status],'reasons':list(dict.fromkeys(blocked+review)) or ['Complete supplied scenario has no identified protected boundary.'], 'scope':scope,'transactions':transactions,'repository_comparisons':plan.get('repository_comparisons',[]),'report_only':True,'limitations':['Scenario assessment is not permission to update.','Dependency aliases are inspected one hop; this is not a complete ABI or reverse-dependency proof.','Package scriptlets, hooks and runtime compatibility are not executed or certified.']}

def run(args):
    return subprocess.run(args, text=True, capture_output=True, timeout=180, check=False)

def runtime_plan(refresh):
    baseline=json.loads((ROOT/'manifests/known-good.json').read_text())
    if not isinstance(baseline.get('packages'),dict) or not baseline['packages'] or not isinstance(baseline.get('hardware'),dict):
        raise ValueError('Missing package or hardware baseline metadata.')
    gate=run([str(ROOT/'scripts/check-hardware.sh'),'--json'])
    hardware=json.loads(gate.stdout).get('status','UNKNOWN')
    ignores=run(['pacman-conf','IgnorePkg'])
    ignoregroups=run(['pacman-conf','IgnoreGroup'])
    if ignores.returncode or ignoregroups.returncode: raise ValueError('Cannot inspect effective IgnorePkg/IgnoreGroup configuration.')
    ignored=ignores.stdout.split()+ignoregroups.stdout.split()
    plan=dict(schema_version=1,hardware_status=hardware,complete=False,solver_success=False,metadata_fresh=refresh,transactions=[],ignored_packages=ignored,incompatibilities=[])
    if hardware != 'VERIFIED':
        return plan
    # Copies only private state. Never refreshes the live database or installs.
    state=Path(os.environ.get('XDG_STATE_HOME', str(Path.home()/'.local/state')))/'omarchy-m3-max'
    state.mkdir(mode=0o700,parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='preflight-',dir=state) as directory:
        work=Path(directory); work.chmod(0o700)
        db=work/'db'; db.mkdir(); (work/'cache').mkdir()
        shutil.copytree('/var/lib/pacman/local',db/'local')
        before=run(['pacman','-Q']).stdout
        if refresh:
            sync=run(['fakeroot','--','pacman','-Sy','--dbpath',str(db),'--cachedir',str(work/'cache'),'--logfile',str(work/'pacman.log'),'--disable-sandbox-filesystem'])
            if sync.returncode: raise ValueError('Isolated repository refresh failed.')
        else:
            shutil.copytree('/var/lib/pacman/sync',db/'sync')
        solved=run(['pacman','-Sup','--dbpath',str(db),'--logfile',str(work/'pacman.log'),'--color','never','--print-format','%n|%v|%D|%P|%H|%R'])
        if solved.returncode: raise ValueError('Isolated package solve failed.')
        if before!=run(['pacman','-Q']).stdout: raise ValueError('Installed packages changed during inspection.')
        installed=dict(line.split(' ',1) for line in before.splitlines())
        listing=run(['pacman','-Sl','--dbpath',str(db),'--color','never'])
        if listing.returncode: raise ValueError('Cannot inspect repository version comparisons.')
        repository={}
        for row in listing.stdout.splitlines():
            fields=row.split()
            if len(fields)>=3: repository.setdefault(fields[1],fields[2])
        comparisons=[]
        for name in baseline['packages']:
            if name in installed and name in repository:
                compared=run(['vercmp',installed[name],repository[name]])
                if compared.returncode: raise ValueError('Cannot compare package versions.')
                if int(compared.stdout)>0:
                    comparisons.append(dict(name=name,installed_version=installed[name],repository_version=repository[name],relation='local-newer'))
        plan['repository_comparisons']=comparisons
        for line in solved.stdout.splitlines():
            parts=line.split('|')
            if len(parts)!=6: raise ValueError('Ambiguous solver output.')
            name,version,depends,provides,conflicts,replaces=parts
            plan['transactions'].append(dict(name=name,old_version=installed.get(name),new_version=version,operation='upgrade' if name in installed else 'install',depends=depends.split(),provides=provides.split(),conflicts=conflicts.split(),replaces=replaces.split(),files=[]))
        plan['solver_success']=True
        # A clean CLI solve establishes a candidate add list only.
        # Uninspected metadata always requires review; no exact approval is claimed.
        plan['complete']=True
        plan['runtime_uninspected']=True
        if solved.stderr.strip():
            # Questions, conflicts and replacements are not silently answered.
            plan['complete']=False
            plan['incompatibilities'].append('Solver emitted diagnostics requiring explicit review of the transaction.')
            # Include only known installed package names and version tokens, never raw diagnostics.
            comparisons=list(plan['repository_comparisons'])
            for diagnostic in solved.stderr.splitlines():
                match=re.search(r'^warning: ([a-zA-Z0-9@._+:-]+): local \(([^ )]+)\) is newer than .*\(([^ )]+)\)',diagnostic)
                if match and match[1] in installed:
                    comparisons.append(dict(name=match[1],installed_version=match[2],repository_version=match[3],relation='local-newer'))
            plan['repository_comparisons']=comparisons
    return plan

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json',action='store_true')
    group=parser.add_mutually_exclusive_group(); group.add_argument('--plan',type=Path); group.add_argument('--refresh',action='store_true')
    parser.add_argument('--scope',choices=('pacman','omarchy'),default='pacman')
    args=parser.parse_args()
    os.umask(0o077)
    try:
        plan=json.loads(args.plan.read_text()) if args.plan else runtime_plan(args.refresh)
        result=assess(plan,args.scope)
        result['simulated']=bool(args.plan)
        if not args.plan: result['reasons'].append('Runtime candidate report omits incoming file paths/scriptlets and cannot authorize an exact transaction; exact transaction reader is not implemented.')
    except (OSError,ValueError,TypeError,subprocess.SubprocessError) as error:
        result={'status':'BLOCKED','exit_code':1,'report_only':True,'reasons':[str(error)]}
    if args.json:
        print(json.dumps(result,indent=2))
    else:
        print(result['status']+'\n'+'\n'.join(result['reasons']))
        for item in result.get('transactions',[]):
            print(f"{item['name']}: {item['old_version']} -> {item['new_version']} ({item['operation']})")
    return result['exit_code']
if __name__=='__main__': raise SystemExit(main())
