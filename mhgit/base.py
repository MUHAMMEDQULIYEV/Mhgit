from . import data
import os

def write_tree(directory='.'):
    with os.scandir(directory) as it:
        for entry in it:
            full=f"{directory}/{entry.name}"
            if is_ignored(full):
                continue
                
            if entry.is_file(follow_symlinks=False):
                with open(full,"rb") as f:
                    print(data.hash_object(f.read()),full)
              #TODO write in file to object store
            elif entry.is_dir(follow_symlinks=False):
                write_tree(full)

def _iter_tree_entiries(oid):
    if not oid:
        return
    tree=data.get_object(oid,'tree')
    for entry in tree.decode().splitlines():
        type_,oid,name=entry.split(' ',2)
        yield type_,oid,name

def get_tree(oid,base_path="./"):
    result={}
    for type_,oid,name,in _iter_tree_entiries(oid):
        assert "/" not in name
        assert name not in ('..', '.')
        path=base_path+name
        if type_=="blob":
            result[path]=oid
        elif type_="tree":
            result.update(get_tree(oid,f'{path}/'))
        else:
            assert False, f'Unknown tree entry {type_}'
    return result

def read_tree(tree_oid):
    for path,oid in get_tree(tree_oid,base_path="./").items():
        os.makedirs(os.path.dirname(path),exist_ok=True)
        with open(path,"wb") as f:
            f.write(data.get_object(oid))
    # TODO actual create the tree object
def is_ignored(path):
    return ".mhgit" in path.split("/")
