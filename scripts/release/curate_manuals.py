"""Build the selected public technical-reference index without changing code examples."""
from pathlib import Path
import hashlib,json,re
from urllib.parse import unquote,quote

LINK=re.compile(r'(?<!!)\[([^\]\n]+)\]\(([^)\n]+)\)')
FENCE=re.compile(r'^\s{0,3}(`{3,}|~{3,})')

def rewrite_links(text,path,root):
    lines=[];fence=None
    for line in text.splitlines(keepends=True):
        match=FENCE.match(line)
        if match:
            run=match.group(1)
            if fence is None:fence=(run[0],len(run))
            elif run[0]==fence[0] and len(run)>=fence[1] and not line[match.end():].strip():fence=None
            lines.append(line);continue
        if fence is not None:
            lines.append(line);continue
        def replace(m):
            target=unquote(m[2].split('#',1)[0].strip('<>'))
            if not target or re.match(r'[A-Za-z][\w+.-]*:',target):return m[0]
            if (path.parent/target).exists():return m[0]
            return m[1]+' (reference outside this distribution)'
        lines.append(LINK.sub(replace,line))
    return ''.join(lines)

def curate(root,policy):
    root=Path(root);manifest_path=root/'docs/en/TRANSLATION_MANIFEST.json'
    old=json.loads(manifest_path.read_text());selected=set(policy['english_manuals']);rows=[]
    for row in old['documents']:
        if row['english_path'] not in selected:continue
        p=root/row['english_path'];p.write_text(rewrite_links(p.read_text(),p,root))
        row=dict(row);row['english_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();rows.append(row)
    if {r['english_path'] for r in rows}!=selected:raise ValueError('Selected manual missing from translation manifest')
    manifest_path.write_text(json.dumps({'scope':'Selected English technical references; original hashes identify the sources, translated hashes identify these public derivatives. Historical claims are not revalidated.','documents':rows},indent=2)+'\n')
    lines=['# Atlas technical references','',f'{len(rows)} selected English reference documents for Atlas domains, services and interfaces. For current installation and runnable AMY workflows, start with [environment setup](../ENVIRONMENT.md), the [tool guide](../ATLAS_TOOL_GUIDE.md) and [reproducibility instructions](REPRODUCIBILITY.md).','','These references describe optional and historical Atlas subsystems. Their presence does not mean every described integration is installed or validated. Translations preserve source examples; individual references can describe resources outside this distribution. Internal plans, generated manuscript drafts and session reports are omitted.','', 'Maintainer: **Ganador1**. Translation-source and public-document hashes are recorded in `en/TRANSLATION_MANIFEST.json`.','']
    for row in rows:
        p=root/row['english_path'];title=next((line[2:].strip() for line in p.read_text().splitlines() if line.startswith('# ')),p.stem.replace('_',' '));title=title.replace('[','').replace(']','')
        lines.append(f'- [{title}]({quote(str(Path(row["english_path"]).relative_to("docs")))})')
    (root/'docs/ENGLISH_MANUALS.md').write_text('\n'.join(lines)+'\n')
