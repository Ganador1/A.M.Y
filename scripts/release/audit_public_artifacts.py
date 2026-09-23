"""Scan release archives locally without disclosing matched credential values."""
from pathlib import Path
import argparse,hashlib,json,re,sys,tarfile,zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from scripts.release.privacy import findings,load_identifiers
from scripts.release.check_release import unsafe_member


def audit(directory,identifiers,credentials=()):
    results=[]
    for p in sorted(Path(directory).iterdir()):
        if not (p.name.endswith('.tar.gz') or p.suffix=='.whl'):continue
        errors=[];count=0
        def check(name,data):
            nonlocal count
            count+=1
            issues=findings(name,identifiers)
            if unsafe_member(name):issues.append('unsafe_member')
            try:text=data.decode('utf-8')
            except UnicodeError:issues.append('unexpected_binary');text=''
            issues+=findings(text,identifiers)
            if any(value in text for value in credentials):issues.append('known_credential')
            if re.search(r'[\w.+-]+@(?:gmail|hotmail|outlook|yahoo|icloud|protonmail|proton)\.[A-Za-z.]+',text,re.I):issues.append('personal_email')
            if issues:errors.append({'member':name,'categories':sorted(set(issues))})
        if p.suffix=='.whl':
            with zipfile.ZipFile(p) as z:
                for n in z.namelist():
                    if not n.endswith('/'):check(n,z.read(n))
        else:
            with tarfile.open(p) as t:
                for m in t:
                    if m.issym() or m.islnk():errors.append({'member':m.name,'categories':['link']})
                    if m.isfile():check(m.name,t.extractfile(m).read())
                    if findings(m.uname+' '+m.gname,identifiers):errors.append({'member':m.name,'categories':['personal_archive_owner']})
        results.append({'artifact':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'files':count,'errors':errors})
    return {'passed':bool(results) and not any(x['errors'] for x in results),'artifacts':results,'scope':'Known private identifiers, configured credential values, common token patterns, personal paths/emails and archive member safety. Not a guarantee of anonymity or a Git-history audit.'}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True);p.add_argument('--private-identifiers',type=Path,required=True);p.add_argument('--credential-file',type=Path,action='append',default=[]);a=p.parse_args();values=[]
    for f in a.credential_file:
        for line in f.read_text().splitlines():
            if '=' not in line or line.lstrip().startswith('#'):continue
            key,value=line.split('=',1);value=value.strip().strip('\"\'')
            if re.search(r'key|secret|token|password',key,re.I) and len(value)>=12 and not re.search(r'example|your_|placeholder|changeme',value,re.I):values.append(value)
    result=audit(a.directory,load_identifiers(a.private_identifiers),values);print(json.dumps(result,indent=2));sys.exit(not result['passed'])
