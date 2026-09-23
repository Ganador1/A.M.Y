"""Offline numerical replay of the public calibration measurements."""
from pathlib import Path
import copy,hashlib,json,math
from fractions import Fraction
import numpy as np
from ar1_replay import ar1_benchmark
from h2_verifier import verify_h2_rhf_certificate
ROOT=Path(__file__).resolve().parent

def same(a,b):
    if type(a) is not type(b):return False
    if isinstance(a,float):return math.isclose(a,b,rel_tol=0,abs_tol=1e-12)
    if isinstance(a,dict):return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return a==b

def main():
    manifest=json.loads((ROOT/'MANIFEST.json').read_text())
    for rel,digest in manifest['sha256'].items():
        p=ROOT/rel
        if p.is_symlink() or ROOT not in p.resolve().parents:raise ValueError('unsafe manifest path')
        if hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise ValueError('hash mismatch: '+rel)
    counts={'ar1':0,'h2':0,'retained_failed_requests':0}
    for p in sorted((ROOT/'measurements').glob('campaign-*/worker-*/*/result.json')):
        old=json.loads(p.read_text());request=json.loads((p.parent/'request.json').read_text())
        if old['success'] is not True:
            # The single failed request has an extra wrapper; it is outside the one-field H2 contract.
            if request['name']!='h2_validation' or set(request['parameters'])=={'distance_angstrom'}:raise ValueError('unexpected failure case')
            counts['retained_failed_requests']+=1;continue
        if request['name']=='ar1_benchmark':
            new=ar1_benchmark(request['parameters']);new['effective_input']=request['parameters']
            if not same(new,old):raise ValueError('AR1 replay differs: '+str(p.relative_to(ROOT)))
            counts['ar1']+=1
        elif request['name']=='h2_validation':
            cert=json.loads((p.parent/'certificate.json').read_text())
            if not verify_h2_rhf_certificate(cert)['valid']:raise ValueError('H2 certificate invalid')
            if Fraction(str(request['parameters']['distance_angstrom']))!=Fraction(str(cert['input']['distance_angstrom'])):raise ValueError('input binding differs')
            if not same(cert['summary'],old['summary']):raise ValueError('summary differs')
            bad=copy.deepcopy(cert);bad['state']['total_energy']+=.1
            if verify_h2_rhf_certificate(bad)['valid']:raise ValueError('H2 corruption accepted')
            counts['h2']+=1
        else:raise ValueError('unknown measurement')
    if counts!={'ar1':23,'h2':28,'retained_failed_requests':1}:raise ValueError('incomplete dataset')
    print(json.dumps({'passed':True,'counts':counts,'numpy_version':np.__version__,
      'scope':'AR1 producer replay and H2 numerical consistency with supplied integrals. Original conversations, full native chains, model ranking and novelty are not verified.'},indent=2))
if __name__=='__main__':main()
