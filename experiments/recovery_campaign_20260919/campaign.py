"""Prepare immutable protocols and run ten bounded native AMY workers.

No alternative decision loop or replacement reasoner: every worker uses AMY.start.
"""
from __future__ import annotations
import argparse
import asyncio
import copy
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from core.execution_evidence import canonical, evidence_span, record_bytes, record_event, verify_run
from experiments.recovery_campaign_20260919 import labs

MODEL = 'deepseek-v4.1-flash:cloud'
LIMITS = {'max_cycles':12,'max_transport_attempts':20,'duration_seconds':1200,'shutdown_grace_seconds':180}
WORKERS = [(f'worker-{i:02}', 'ar1_benchmark' if i<=4 else 'ssh_fixed_resource' if i<=7 else 'autocorrelation_search', i<=2) for i in range(1,11)]


def write(path, obj):
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_bytes(canonical(obj)+b'\n'); os.replace(tmp,path)


def journal(directory,event,**fields):
    path = directory/'observer.jsonl'
    previous = json.loads(path.read_bytes().splitlines()[-1])['sha256'] if path.exists() else ''
    row = {'event':event,'utc':datetime.now(timezone.utc).isoformat(),'previous_sha256':previous,**fields}
    row['sha256'] = hashlib.sha256(canonical(row)).hexdigest()
    with path.open('ab') as out: out.write(canonical(row)+b'\n')


def mission(branch):
    return ('Conduct a bounded reproducible investigation using only '+branch+'. '+labs.describe()[branch]+
            ' Choose and execute at least three distinct meaningful requests. After three successful distinct requests, synthesize and finish_session promptly; do not keep running merely to fill the cycle budget. '
            'Native action run_scientific_tool requires tool_name="'+branch+'", tool_input a strict JSON string containing parameters, and domain. '
            'Compare results honestly, including null findings and uncertainties. Execution success does not establish discovery. No claims of world priority or global optimum. '
            'Do not repeat an identical request; its receipt remains available. finish_session requires nonempty content and session_summary with exactly reason(string), experiment_ids(list of at least3 distinct known receipt IDs), unresolved(list of strings), next_steps(list of strings). '
            'Cite actual native experiment receipt IDs from context, not measurement directory labels. No additional models or tools are permitted.')


def prepare(directory):
    from amy import load_config, _evidence_config
    directory.mkdir(parents=True,exist_ok=False)
    source_files = {Path(__file__).resolve(), Path(labs.__file__).resolve(), ROOT/'config.yaml', labs.BEST,
                    ROOT/'amy.py', ROOT/'atlas/app/ssh_certificate_tool.py', ROOT/'atlas/app/ssh_spectral_certificate.py'}
    for package in ('core','cognition','memory','skills','senses','communication','evolution'):
        source_files.update((ROOT/package).glob('*.py'))
    for package in ('autocorrelation_resilient_20260909','autocorrelation_exact_20260906'):
        source_files.update((ROOT/'experiments'/package).glob('*.py'))
    files = sorted(source_files)
    for name, branch, think in WORKERS:
        cell = directory/name; cell.mkdir()
        contract = mission(branch)
        config = load_config(str(ROOT/'config.yaml'))
        config['mission'] = {'goal':contract,'description':branch+' bounded recovery study','urgency':'high'}
        config.setdefault('heartbeat',{}).update(max_cycles=12,base_interval_seconds=1,focused_interval_seconds=1,idle_interval_seconds=1,
            max_cycles_before_reflection=2,continuous_mission=False,operating_contract=contract,
            allowed_actions=['run_scientific_tool','think_more','finish_session'],allowed_scientific_tools=[branch],
            require_tool_certificate=False,require_session_synthesis_validation=True,
            max_consecutive_decision_failures=3,max_total_decision_failures=5,memory_checkpoint_interval=20)
        config.setdefault('llm',{}).update(total_timeout=180,read_timeout=180,max_concurrency=1,
            tool_observation_mode='certified_summary',experiment_receipt_context=True)
        for role in ('reasoner','fast'):
            config['llm'].setdefault(role,{}).update(model=MODEL,temperature=.2,max_tokens=16384 if think else 8192,num_ctx=65536,think=think)
        config['llm']['reflection'] = {'max_tokens':4096,'think':False}
        config.setdefault('atlas',{})['model'] = MODEL
        config.setdefault('memory',{}).update(namespace_by_mission=True,mission_namespace=name,mission_memory_root=str(cell/'memory'))
        config.setdefault('skills',{}).update(library_path=str(cell/'skills'),use_embedding_recall=False)
        config.setdefault('research',{}).update(sources=[],download_pdfs=False)
        config.setdefault('communication',{}).update(method='file',report_path=str(cell/'reports'),max_reports_per_day=0)
        protocol = {'worker':name,'branch':branch,'model':MODEL,'think':think,'limits':LIMITS,
                    'native_entrypoint':'amy.AMY.start','operating_contract':contract,
                    'operator_interventions_after_launch':0,'scope':'Bounded exploratory measurements; not a novelty claim.',
                    'profile_comparison':'AR1 workers01/02 thinktrue16384 versus03/04 thinkfalse8192, identical mission; other workers candidate profile.'}
        write(cell/'protocol.json',protocol)
        config['evidence'] = {'enabled':True,'root':str(cell/'runs'),'provenance_per_run':True,
                              'additional_sources':[str(p) for p in files]+[str(cell/'protocol.json')],
                              'autonomy_protocol_sha256':hashlib.sha256(canonical(protocol)).hexdigest()}
        write(cell/'effective_config.json',_evidence_config(config))
        files_for_cell = [cell/'protocol.json',cell/'effective_config.json']
        source_files.update(files_for_cell)
    plan = {'schema':'amy.recovery_campaign.v1','workers':WORKERS,'max_workers':10,'max_transport_per_worker':20,
            'max_cpu_jobs':2,'no_restarts':True,'limits':LIMITS,
            'hashes':{str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source_files)}}
    write(directory/'plan.json',plan)
    journal(directory,'prepared',plan_sha256=hashlib.sha256((directory/'plan.json').read_bytes()).hexdigest())
    return plan


def check_plan(directory):
    plan = json.loads((directory/'plan.json').read_text())
    if plan['workers'] != [list(v) for v in WORKERS]: raise ValueError('worker plan changed')
    changed = [p for p,h in plan['hashes'].items() if not Path(p).is_file() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
    if changed: raise ValueError('Frozen sources/config changed: '+', '.join(changed))
    return plan


def parse_input(text):
    if not isinstance(text,str) or len(text.encode())>16384: raise ValueError('tool_input must be JSON string <=16384bytes')
    def unique(pairs):
        result = {}
        for k,v in pairs:
            if k in result: raise ValueError('duplicate JSON key: '+k)
            result[k]=v
        return result
    obj = json.loads(text,object_pairs_hook=unique,parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite JSON')))
    if not isinstance(obj,dict): raise ValueError('parameters must be a JSON object')
    return obj


class Laboratory:
    def __init__(self,directory,branch):
        self.directory=directory; self.branch=branch; self.seen=set(); self.successes=[]; self.attempts=0

    async def _compute(self,name,params,path):
        lock = None
        while lock is None:
            for slot in range(2):
                handle = (self.directory.parent/f'cpu-slot-{slot}.lock').open('a+')
                try: fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB); lock=handle; break
                except BlockingIOError: handle.close()
            if lock is None: await asyncio.sleep(.2)
        try:
            task=asyncio.create_task(asyncio.to_thread(labs.run,name,params,path))
            try: return await asyncio.shield(task)
            except asyncio.CancelledError:
                await task  # keep CPU slot until actual computation ends
                raise
        finally:
            fcntl.flock(lock,fcntl.LOCK_UN);lock.close()

    async def run_scientific_tool(self,tool_name,tool_input,domain='mathematics'):
        with evidence_span('recovery.scientific_tool',{'name':tool_name,'input':tool_input}) as span:
            try:
                if tool_name!=self.branch: raise ValueError('wrong branch tool')
                params=parse_input(tool_input)
                key=hashlib.sha256(canonical({'name':tool_name,'parameters':params})).hexdigest()
                if key in self.seen: raise ValueError('Duplicate request rejected; use prior receipt, choose different parameters, or finish_session after3successes.')
                self.seen.add(key);self.attempts+=1
                path=self.directory/'studies'/f'm{self.attempts:04}'
                result=await self._compute(tool_name,params,path)
                artifacts=[]
                for file in sorted(path.rglob('*')):
                    if file.is_file(): artifacts.append({'path':str(file.relative_to(path)), 'blob':record_bytes('recovery-'+file.name,file.read_bytes())})
                if result.get('success') is True: self.successes.append(key)
                observation=copy.deepcopy(result)
                if tool_name=='ar1_benchmark' and result.get('success'):
                    for value in observation['results'].values():
                        value.pop('calibration_scores',None);value.pop('evaluation_scores',None)
                observation.update(measurement_id=path.name,artifacts=artifacts,unique_successes=len(self.successes),scientific_truth_verified=False,
                                   closure_guidance='After3successes use native receipt IDs and finish_session; no requirement to find improvement.')
                return span.result(json.dumps(observation,allow_nan=False))
            except (ValueError,TypeError,KeyError) as exc:
                return span.result(json.dumps({'success':False,'error':str(exc)}))

    def validate(self,thought,history):
        ids=thought.get('session_summary',{}).get('experiment_ids',[])
        errors=[]
        if len(self.successes)<3: errors.append('Need at least3 distinct successful scientific requests before closure.')
        if len(set(ids))<3: errors.append('Cite at least3 distinct native experiment receipt IDs.')
        return {'passed':not errors,'errors':errors,'scientific_truth_verified':False,'scope':'Operational closure and ID count only; core checks ID membership. Scientific prose and novelty are not verified.'}


async def execute(directory,name):
    from amy import AMY
    import core.provenance as provenance
    check_plan(directory)
    if name not in {w[0] for w in WORKERS}: raise ValueError('unknown worker')
    cell=directory/name
    if any((cell/p).exists() for p in ('runs','result.json','process.json')): raise FileExistsError('No worker restarts')
    cfg=json.loads((cell/'effective_config.json').read_text()); protocol=json.loads((cell/'protocol.json').read_text())
    write(cell/'process.json',{'pid':os.getpid(),'started_utc':datetime.now(timezone.utc).isoformat()})
    provenance._provenance=provenance.ProvenanceManager(cell/'experiments')
    mind=AMY(cfg);lab=Laboratory(cell,protocol['branch'])
    mind.heartbeat._atlas_tools=lab;mind.heartbeat._session_synthesis_validator=lab.validate
    started=time.monotonic();state={'transport_attempts':0,'stop_reason':None,'operator_decision_interventions':0}
    def stop(reason):
        if not state['stop_reason']:
            state['stop_reason']=reason;state['stop_elapsed']=time.monotonic()-started
            journal(cell,'stop_requested',reason=reason)
        mind.heartbeat._running=False
    original=mind.reasoning.client._do_request
    async def bounded(endpoint,payload,api_key):
        if payload.get('model')!=MODEL: stop('model_outside_protocol');raise RuntimeError('undeclared model')
        if state['transport_attempts']>=20 or state['stop_reason']:
            stop(state['stop_reason'] or 'transport_limit');raise RuntimeError('declared transport budget exhausted')
        state['transport_attempts']+=1
        return await original(endpoint=endpoint,payload=payload,api_key=api_key)
    mind.reasoning.client._do_request=bounded
    loop=asyncio.get_running_loop()
    for sig in (signal.SIGTERM,signal.SIGINT):loop.add_signal_handler(sig,stop,'signal_'+sig.name)
    journal(cell,'native_started',pid=os.getpid())
    task=asyncio.create_task(mind.start());failure=None
    try:
        while not task.done():
            elapsed=time.monotonic()-started
            if elapsed>=1200:stop('duration_limit')
            if state['stop_reason'] and elapsed-state['stop_elapsed']>180:task.cancel()
            write(cell/'status.json',{**state,'status':'running','elapsed_seconds':elapsed,'cycles':mind.heartbeat.ctx.cycle_number,'unique_successes':len(lab.successes)})
            try: await asyncio.wait_for(asyncio.shield(task),5)
            except asyncio.TimeoutError:pass
        await task
    except BaseException as exc:failure={'type':type(exc).__name__,'error':str(exc)}
    finally:
        if not task.done():task.cancel();await asyncio.gather(task,return_exceptions=True)
    path=getattr(mind,'evidence_path',None)
    result={**state,'status':'finished','runtime_failure':failure,'elapsed_seconds':time.monotonic()-started,
            'cycles':mind.heartbeat.ctx.cycle_number,'unique_successes':len(lab.successes),
            'native_stop_reason':getattr(mind.heartbeat,'stop_reason',None),'evidence_path':str(path) if path else None,
            'integrity':verify_run(path) if path else None,'finished_utc':datetime.now(timezone.utc).isoformat()}
    write(cell/'result.json',result);write(cell/'status.json',result);journal(cell,'native_finished',result=result)
    return 1 if failure else 0


async def coordinate(directory):
    check_plan(directory)
    if (directory/'scheduler.json').exists():raise FileExistsError('No scheduler restarts')
    state={'pid':os.getpid(),'status':'running','workers':{},'started_utc':datetime.now(timezone.utc).isoformat()}
    write(directory/'scheduler.json',state)
    env=dict(os.environ)
    env.update({k:'1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')})
    children=[]
    current=asyncio.current_task()
    loop=asyncio.get_running_loop()
    for sig in (signal.SIGTERM,signal.SIGINT):loop.add_signal_handler(sig,current.cancel)
    try:
        for name,branch,think in WORKERS:
            log=(directory/name/'console.log').open('wb')
            child=await asyncio.create_subprocess_exec(sys.executable,'-B',str(Path(__file__).resolve()),'worker','--output-root',str(directory),'--name',name,
                                                       cwd=str(ROOT),env=env,stdout=log,stderr=subprocess.STDOUT)
            log.close();children.append((name,child));state['workers'][name]={'pid':child.pid,'exit_code':None}
            write(directory/'scheduler.json',state);journal(directory,'worker_started',worker=name,pid=child.pid)
        async def wait(name,child):
            code=await child.wait();state['workers'][name]['exit_code']=code
            write(directory/'scheduler.json',state);journal(directory,'worker_exited',worker=name,exit_code=code)
        await asyncio.wait_for(asyncio.gather(*(wait(name,child) for name,child in children)),1500)
    finally:
        for _,child in children:
            if child.returncode is None:child.terminate()
        try:await asyncio.wait_for(asyncio.gather(*(child.wait() for _,child in children)),210)
        except asyncio.TimeoutError:
            for name,child in children:
                if child.returncode is None:
                    child.kill();journal(directory,'worker_killed_after_shutdown_timeout',worker=name)
            await asyncio.gather(*(child.wait() for _,child in children))
        for name,child in children:state['workers'][name]['exit_code']=child.returncode
        state['status']='finished';state['finished_utc']=datetime.now(timezone.utc).isoformat();write(directory/'scheduler.json',state)
    return state


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['prepare','run','worker']);parser.add_argument('--output-root',required=True,type=Path)
    parser.add_argument('--name');args=parser.parse_args();directory=args.output_root.resolve()
    if args.command=='prepare':prepare(directory);print(json.dumps({'prepared':str(directory),'workers':10}));return 0
    if args.command=='worker':return asyncio.run(execute(directory,args.name))
    state=asyncio.run(coordinate(directory));return int(any(w['exit_code'] for w in state['workers'].values()))


if __name__=='__main__':raise SystemExit(main())
