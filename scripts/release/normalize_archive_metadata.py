"""Remove build-account ownership from a generated tar archive (payload unchanged)."""
from pathlib import Path
import argparse,os,tarfile,tempfile


def normalize(path):
    path=Path(path)
    handle,temp=tempfile.mkstemp(prefix='amy-public-',suffix='.tar.gz',dir=path.parent)
    os.close(handle)
    try:
        with tarfile.open(path) as source, tarfile.open(temp,'w:gz',format=tarfile.PAX_FORMAT) as target:
            for member in source:
                member.uid=member.gid=0
                member.uname=member.gname=''
                member.pax_headers={k:v for k,v in member.pax_headers.items() if k not in {'uid','gid','uname','gname'}}
                target.addfile(member,source.extractfile(member) if member.isfile() else None)
        os.replace(temp,path)
    finally:
        if os.path.exists(temp):os.unlink(temp)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('archive',type=Path);normalize(parser.parse_args().archive)
