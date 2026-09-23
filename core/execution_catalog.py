"""Bounded execution identities, not summaries of scientific truth."""
import copy,hashlib,json

def execution_catalog(index, *, character_budget=12000, limit=64):
    rows=[];used=0
    for identifier,receipt in reversed(list(index.items())):
        if receipt['experiment_id']!=identifier:raise ValueError('receipt/index identity mismatch')
        observation=receipt.get('operational_observation',{})
        source=receipt.get('original_input', observation.get('input'))
        if not isinstance(source,dict):
            source={'text':None,'sha256':None,'bytes':None,'omitted_reason':'original_input_unavailable'}
        elif source.get('text') is not None:
            text=source['text'];raw=text.encode()
            if source['sha256']!=hashlib.sha256(raw).hexdigest() or source['bytes']!=len(raw):
                raise ValueError('request view hash/length mismatch')
        status=receipt.get('execution_success')
        if status is not None and type(status) is not bool:raise ValueError('boolean execution status required')
        entry={'experiment_id':identifier,'tool_name':receipt['tool_name'],
            'execution_success':status,'input':copy.deepcopy(source),'raw_output_sha256':receipt['raw_output_sha256']}
        if status is False:entry['error']=receipt.get('error')
        size=len(json.dumps(entry,ensure_ascii=False,allow_nan=False))
        if len(rows)>=limit or used+size>character_budget:continue
        rows.append(entry);used+=size
    rows.reverse()
    return {'total_executions':len(index),'visible_executions':rows,'omitted_executions':len(index)-len(rows),
        'scope':'Recorded execution identities and original inputs only. Success means the operational evaluator accepted the output; no new numerical result, certificate, interpretation or novelty is asserted.'}
