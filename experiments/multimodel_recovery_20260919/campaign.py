"""Ten bounded native AMY sessions: five actual cloud models, two tasks each."""
from __future__ import annotations
import argparse
import asyncio
import copy
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.recovery_campaign_20260919 import campaign as previous
from core.execution_evidence import canonical, verify_run, evidence_span, record_bytes

write=previous.write
journal=previous.journal
MODELS=('deepseek-v4.1-flash','glm-5.3','glm-5.3-flash','qwen3.5:397b','deepseek-v4-pro:0813')
WORKERS=[(f'worker-{2*i+j+1:02}',model,branch) for i,model in enumerate(MODELS)
         for j,branch in enumerate(('ar1_benchmark','h2_validation'))]
LIMITS={'max_cycles':10,'max_transport_attempts':15,'duration_seconds':600,'shutdown_grace_seconds':180}


def laboratory_module():
    return importlib.import_module('experiments.multimodel_recovery_20260919.labs')


def mission(branch):
    return ('Conduct a bounded calibration benchmark using only '+branch+'. '+laboratory_module().describe()[branch]+
            ' Execute exactly the three preregistered cells; choose their order independently. After three successful distinct cells, synthesize and finish_session promptly. '
            'run_scientific_tool requires tool_name="'+branch+'", tool_input a strict JSON string containing parameters, and domain. '
            'Compare actual results, null findings and uncertainties; execution success is not discovery. No world priority or global-optimum claim. '
            'Never repeat identical parameters; prior receipts remain available. finish_session requires nonempty content and session_summary with exactly reason(string), '
            'experiment_ids(list of at least3 distinct known native receipt IDs), unresolved(list of strings), next_steps(list of strings). '
            'Use native experiment receipt IDs, not measurement labels. No other tools or models are permitted. '
            +laboratory_module().assessment_contract(branch))


def selected_workers(names=None):
    if names is None:return list(WORKERS)
    allowed={w[0]:w for w in WORKERS}
    if (not isinstance(names,list) or not names or any(not isinstance(n,str) for n in names)
            or len(set(names))!=len(names) or any(n not in allowed for n in names)):
        raise ValueError('workers must be a nonempty unique list of allowed worker names')
    return [allowed[n] for n in names]


def prepare(directory,worker_names=None):
    workers=selected_workers(worker_names)
    from amy import load_config, _evidence_config
    labs=laboratory_module()
    directory.mkdir(parents=True,exist_ok=False)
    sources={Path(__file__).resolve(),Path(labs.__file__).resolve(),Path(previous.__file__).resolve(),
             ROOT/'experiments/recovery_campaign_20260919/labs.py',ROOT/'amy.py',ROOT/'config.yaml',
             ROOT/'atlas/app/h2_rhf_certificate.py',ROOT/'atlas/app/h2_rhf_verifier.py',
             ROOT/'release_evidence/runtime/cloud-model-catalog.json'}
    for package in ('core','cognition','memory','skills','senses','communication','evolution'):
        sources.update((ROOT/package).glob('*.py'))
    frozen=sorted(sources)
    for name,model,branch in workers:
        cell=directory/name;cell.mkdir();contract=mission(branch)
        config=load_config(str(ROOT/'config.yaml'))
        config['mission']={'goal':contract,'description':branch+' native multi-model comparison','urgency':'high'}
        config.setdefault('heartbeat',{}).update(max_cycles=10,base_interval_seconds=1,focused_interval_seconds=1,idle_interval_seconds=1,
            max_cycles_before_reflection=2,continuous_mission=False,operating_contract=contract,
            allowed_actions=['run_scientific_tool','think_more','finish_session'],allowed_scientific_tools=[branch],
            require_tool_certificate=False,require_session_synthesis_validation=True,max_consecutive_decision_failures=3,
            max_total_decision_failures=5,memory_checkpoint_interval=20)
        config.setdefault('llm',{}).update(provider='ollama_cloud',base_url='https://ollama.com/api',total_timeout=150,read_timeout=150,
            max_concurrency=1,tool_observation_mode='certified_summary',experiment_receipt_context=True)
        for role in ('reasoner','fast'):
            config['llm'].setdefault(role,{}).update(model=model,temperature=.2,max_tokens=8192,num_ctx=65536,think=False)
        config['llm']['reflection']={'max_tokens':4096,'think':False}
        config.setdefault('atlas',{})['model']=model
        config.setdefault('memory',{}).update(namespace_by_mission=True,mission_namespace=name,mission_memory_root=str(cell/'memory'))
        config.setdefault('skills',{}).update(library_path=str(cell/'skills'),use_embedding_recall=False)
        config.setdefault('research',{}).update(sources=[],download_pdfs=False)
        config.setdefault('communication',{}).update(method='file',report_path=str(cell/'reports'),max_reports_per_day=0)
        protocol={'worker':name,'model':model,'branch':branch,'limits':LIMITS,'operating_contract':contract,
                  'native_entrypoint':'amy.AMY.start','operator_interventions_after_launch':0,
                  'scope':'Exploratory autonomous tool use, one session per model/task; not broad model ranking or scientific novelty.',
                  'profile':{'think':False,'max_tokens':8192,'num_ctx':65536,'temperature':.2,'reflection_think':False,'reflection_max_tokens':4096}}
        write(cell/'protocol.json',protocol)
        config['evidence']={'enabled':True,'root':str(cell/'runs'),'provenance_per_run':True,
                            'additional_sources':[str(p) for p in frozen]+[str(cell/'protocol.json')],
                            'autonomy_protocol_sha256':hashlib.sha256(canonical(protocol)).hexdigest()}
        write(cell/'effective_config.json',_evidence_config(config))
        sources.update([cell/'protocol.json',cell/'effective_config.json'])
    plan={'schema':'amy.multimodel_recovery.v1','workers':workers,'max_workers':len(workers),'max_cpu_jobs':2,'limits':LIMITS,
          'no_restarts':True,'hashes':{str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(sources)}}
    write(directory/'plan.json',plan);journal(directory,'prepared',plan_sha256=hashlib.sha256((directory/'plan.json').read_bytes()).hexdigest())
    return plan


def check_plan(directory):
    plan=json.loads((directory/'plan.json').read_text())
    rows=plan.get('workers')
    if (not isinstance(rows,list) or not rows or any(not isinstance(w,list) or len(w)!=3 for w in rows)
            or any(w not in [list(v) for v in WORKERS] for w in rows)
            or len({w[0] for w in rows})!=len(rows) or plan.get('max_workers')!=len(rows)):
        raise ValueError('worker subset must contain unique allowed identities and match max_workers')
    changed=[p for p,h in plan['hashes'].items() if not Path(p).is_file() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
    if changed:raise ValueError('Frozen source/config changed: '+','.join(changed))
    return plan


class Laboratory(previous.Laboratory):
    """Reuse receipt retention and strict input handling; new lab dispatcher only."""
    def __init__(self,directory,branch):
        super().__init__(directory,branch)
        self.successful_results=[]

    async def run_scientific_tool(self,tool_name,tool_input,domain='mathematics'):
        with evidence_span('multimodel.scientific_tool',{'name':tool_name,'input':tool_input}) as span:
            try:
                if tool_name!=self.branch:raise ValueError('wrong branch tool')
                params=previous.parse_input(tool_input)
                try:normalized=laboratory_module().normalized(tool_name,params)
                except ValueError:normalized=params  # lab persists invalid requests and rejection receipt
                key=hashlib.sha256(canonical({'name':tool_name,'parameters':normalized})).hexdigest()
                if key in self.seen:raise ValueError('Duplicate cell rejected; use prior receipt and select an uncompleted preregistered cell, or finish_session after all3.')
                self.seen.add(key);self.attempts+=1
                path=self.directory/'studies'/f'm{self.attempts:04}'
                result=await self._compute(tool_name,params,path)
                artifacts=[]
                for file in sorted(path.rglob('*')):
                    if file.is_file():artifacts.append({'path':str(file.relative_to(path)),'blob':record_bytes('multimodel-'+file.name,file.read_bytes())})
                if result.get('success') is True:
                    self.successes.append(key);self.successful_results.append(copy.deepcopy(result))
                observation=copy.deepcopy(result)
                if tool_name=='ar1_benchmark' and result.get('success'):
                    for value in observation['results'].values():
                        value.pop('calibration_scores',None);value.pop('evaluation_scores',None)
                observation.update(measurement_id=path.name,artifacts=artifacts,unique_successes=len(self.successes),scientific_truth_verified=False,
                    closure_guidance='After all3 cells submit the quantitative assessment and use native receipt IDs to finish_session; no discovery requirement.')
                return span.result(json.dumps(observation,allow_nan=False))
            except (ValueError,TypeError,KeyError) as exc:return span.result(json.dumps({'success':False,'error':str(exc)}))

    def validate(self,thought,history):
        result=super().validate(thought,history)
        result['errors'].extend(laboratory_module().assessment_errors(self.branch,thought.get('assessment'),self.successful_results))
        result['passed']=not result['errors']
        result['quantified_fields_verified']=result['passed']
        result['assessment']=copy.deepcopy(thought.get('assessment'))
        result['scope']='Operational closure, known native IDs (core), and bounded quantitative assessment; free prose, scientific truth and novelty are not certified.'
        return result

    async def _compute(self,name,params,path):
        lock=None
        while lock is None:
            for slot in range(2):
                handle=(self.directory.parent/f'cpu-slot-{slot}.lock').open('a+')
                try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB);lock=handle;break
                except BlockingIOError:handle.close()
            if lock is None:await asyncio.sleep(.2)
        try:
            task=asyncio.create_task(asyncio.to_thread(laboratory_module().run,name,params,path))
            try:return await asyncio.shield(task)
            except asyncio.CancelledError:await task;raise
        finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()


async def execute(directory,name):
    from amy import AMY
    import core.provenance as provenance
    plan=check_plan(directory)
    identities={w[0]:(w[1],w[2]) for w in plan['workers']}
    if name not in identities:raise ValueError('unknown worker')
    model,branch=identities[name];cell=directory/name
    if any((cell/p).exists() for p in ('runs','result.json','process.json')):raise FileExistsError('No worker restarts')
    config=json.loads((cell/'effective_config.json').read_text())
    write(cell/'process.json',{'pid':os.getpid(),'model':model,'started_utc':datetime.now(timezone.utc).isoformat()})
    provenance._provenance=provenance.ProvenanceManager(cell/'experiments')
    mind=AMY(config);lab=Laboratory(cell,branch)
    mind.heartbeat._atlas_tools=lab;mind.heartbeat._session_synthesis_validator=lab.validate
    started=time.monotonic();state={'model':model,'branch':branch,'transport_attempts':0,'stop_reason':None,'operator_decision_interventions':0}
    def stop(reason):
        if not state['stop_reason']:
            state['stop_reason']=reason;state['stop_elapsed']=time.monotonic()-started;journal(cell,'stop_requested',reason=reason)
        mind.heartbeat._running=False
    original=mind.reasoning.client._do_request
    async def bounded(endpoint,payload,api_key):
        if payload.get('model')!=model:stop('model_outside_protocol');raise RuntimeError('worker requested undeclared model')
        if state['transport_attempts']>=15 or state['stop_reason']:
            stop(state['stop_reason'] or 'transport_limit');raise RuntimeError('declared transport budget exhausted')
        state['transport_attempts']+=1
        return await original(endpoint=endpoint,payload=payload,api_key=api_key)
    mind.reasoning.client._do_request=bounded
    loop=asyncio.get_running_loop()
    for sig in (signal.SIGTERM,signal.SIGINT):loop.add_signal_handler(sig,stop,'signal_'+sig.name)
    journal(cell,'native_started',pid=os.getpid(),model=model)
    task=asyncio.create_task(mind.start());failure=None
    try:
        while not task.done():
            elapsed=time.monotonic()-started
            if elapsed>=600:stop('duration_limit')
            if state['stop_reason'] and elapsed-state['stop_elapsed']>180:task.cancel()
            write(cell/'status.json',{**state,'status':'running','elapsed_seconds':elapsed,'cycles':mind.heartbeat.ctx.cycle_number,'unique_successes':len(lab.successes)})
            try:await asyncio.wait_for(asyncio.shield(task),5)
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
    plan=check_plan(directory)
    if (directory/'scheduler.json').exists():raise FileExistsError('No scheduler restarts')
    state={'pid':os.getpid(),'status':'running','workers':{},'started_utc':datetime.now(timezone.utc).isoformat()}
    write(directory/'scheduler.json',state)
    env=dict(os.environ);env.update({k:'1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS')})
    children=[];current=asyncio.current_task();loop=asyncio.get_running_loop()
    for sig in (signal.SIGTERM,signal.SIGINT):loop.add_signal_handler(sig,current.cancel)
    try:
        for name,model,branch in plan['workers']:
            log=(directory/name/'console.log').open('wb')
            child=await asyncio.create_subprocess_exec(sys.executable,'-B',str(Path(__file__).resolve()),'worker','--output-root',str(directory),'--name',name,
                cwd=str(ROOT),env=env,stdout=log,stderr=subprocess.STDOUT)
            log.close();children.append((name,child));state['workers'][name]={'pid':child.pid,'model':model,'branch':branch,'exit_code':None}
            write(directory/'scheduler.json',state);journal(directory,'worker_started',worker=name,model=model,pid=child.pid)
        async def wait(name,child):
            code=await child.wait();state['workers'][name]['exit_code']=code
            write(directory/'scheduler.json',state);journal(directory,'worker_exited',worker=name,exit_code=code)
        await asyncio.wait_for(asyncio.gather(*(wait(name,child) for name,child in children)),900)
    finally:
        for _,child in children:
            if child.returncode is None:child.terminate()
        try:await asyncio.wait_for(asyncio.gather(*(child.wait() for _,child in children)),210)
        except asyncio.TimeoutError:
            for name,child in children:
                if child.returncode is None:child.kill();journal(directory,'worker_killed_after_shutdown_timeout',worker=name)
            await asyncio.gather(*(child.wait() for _,child in children))
        for name,child in children:state['workers'][name]['exit_code']=child.returncode
        state['status']='finished';state['finished_utc']=datetime.now(timezone.utc).isoformat();write(directory/'scheduler.json',state)
    return state


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['prepare','run','worker'])
    parser.add_argument('--output-root',required=True,type=Path);parser.add_argument('--name')
    parser.add_argument('--workers',help='Prepare only these comma-separated worker names; omitted means all10')
    args=parser.parse_args();directory=args.output_root.resolve()
    if args.workers is not None and args.command!='prepare':parser.error('--workers is valid only with prepare; run uses the frozen plan')
    if args.command=='prepare':
        names=args.workers.split(',') if args.workers is not None else None
        plan=prepare(directory,names)
        print(json.dumps({'prepared':str(directory),'workers':len(plan['workers']),'models':sorted({w[1] for w in plan['workers']})}));return 0
    if args.command=='worker':return asyncio.run(execute(directory,args.name))
    result=asyncio.run(coordinate(directory));return int(any(w['exit_code'] for w in result['workers'].values()))


if __name__=='__main__':raise SystemExit(main())
