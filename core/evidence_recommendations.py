"""Read a pinned catalog snapshot and resolve explicitly superseded recommendations.

A relationship is a curated annotation, not an independent truth judgement.
Original results remain visible. No database, source or experiment is modified.
"""
import hashlib,json,re,sqlite3
from pathlib import Path

def retrieve(db,expected_sha256,*,identifier=None,query=None,limit=5):
    if type(limit)!=int or not 1<=limit<=20:raise ValueError('limit must be 1..20')
    raw=Path(db).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=expected_sha256:raise ValueError('Catalog commitment mismatch')
    conn=sqlite3.connect(':memory:')
    try:
        conn.deserialize(raw);conn.execute('PRAGMA query_only=ON')
        records={r[0]:r for r in conn.execute('SELECT * FROM records')};links={}
        for ident,row in records.items():
            payload=json.loads(row[6]);parent=payload.get('supersedes_recommendation') if isinstance(payload,dict) else None
            if parent is not None:
                if type(parent)!=str or parent not in records:raise ValueError('Dangling recommendation relation')
                links.setdefault(parent,[]).append(ident)
        def leaves(ident,path=()):
            if ident in path:raise ValueError('Recommendation cycle')
            children=sorted(links.get(ident,[]))
            if not children:return [ident]
            return sorted({leaf for child in children for leaf in leaves(child,path+(ident,))})
        # Reject cycles even if this particular query would not encounter one.
        for ident in links:leaves(ident)
        if identifier is not None:ids=[identifier] if identifier in records else []
        else:
            terms=re.findall(r'\w+',query or '',flags=re.UNICODE)
            if not terms:return []
            match=' OR '.join('"'+t+'"' for t in terms)
            ids=[r[0] for r in conn.execute('SELECT id FROM search WHERE search MATCH ? ORDER BY bm25(search) LIMIT ?',(match,limit))]
        def checked(ident):
            id_,kind,source,source_hash,artifact,artifact_hash,payload=records[ident]
            for path,expected in ((source,source_hash),(artifact,artifact_hash)):
                if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=expected:raise ValueError('STALE_EVIDENCE: '+path)
            return {'id':id_,'kind':kind,'source':source,'source_sha256':source_hash,'artifact_source':artifact,'artifact_sha256':artifact_hash,'payload':json.loads(payload),'fresh_bytes_verified':True,'interpretation_verified':False}
        output=[]
        for ident in ids:
            lineage=[]
            def walk(current):
                row=checked(current)
                for child in sorted(links.get(current,[])):
                    lineage.append({'from':current,'to':child,'source_sha256':records[child][3]});walk(child)
                return row
            original=walk(ident);current=leaves(ident);superseded=current!=[ident]
            output.append({'matched_record':original,'recommendation_status':'superseded' if superseded else 'not_superseded_in_this_snapshot',
                           'current_recommendations':[checked(i) for i in current],'lineage':lineage,'multiple_current_recommendations':len(current)>1,
                           'scope':'Explicit recommendation lineage in a hash-pinned catalog. An older mathematical statement is not declared false; source freshness is not scientific truth.'})
        return output
    finally:conn.close()
