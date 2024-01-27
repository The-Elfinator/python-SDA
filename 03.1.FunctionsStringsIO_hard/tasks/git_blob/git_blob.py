import zlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class BlobType(Enum):
    """Helper class for holding blob type"""
    COMMIT = b'commit'
    TREE = b'tree'
    DATA = b'blob'

    @classmethod
    def from_bytes(cls, type_: bytes) -> 'BlobType':
        for member in cls:
            if member.value == type_:
                return member
        assert False, f'Unknown type {type_.decode("utf-8")}'


@dataclass
class Blob:
    """Any blob holder"""
    type_: BlobType
    content: bytes


@dataclass
class Commit:
    """Commit blob holder"""
    tree_hash: str
    parents: list[str]
    author: str
    committer: str
    message: str


@dataclass
class Tree:
    """Tree blob holder"""
    children: dict[str, Blob]


def read_blob(path: Path) -> Blob:
    """
    Read blob-file, decompress and parse header
    :param path: path to blob-file
    :return: blob-file type and content
    """
    with open(path, 'rb') as file:
        content = file.read()
    decompressed_content = zlib.decompress(content)
    type_bytes, content = decompressed_content.split(b'\x00', 1)
    type_ = BlobType.from_bytes(type_bytes.split()[0])
    return Blob(type_=type_, content=content)


def traverse_objects(obj_dir: Path) -> dict[str, Blob]:
    """
    Traverse directory with git objects and load them
    :param obj_dir: path to git "objects" directory
    :return: mapping from hash to blob with every blob found
    """
    ret = {}
    for sub_dir in obj_dir.iterdir():
        if sub_dir.is_dir():
            for file in sub_dir.iterdir():
                if file.is_file():
                    hash_of_obj = sub_dir.name + file.name
                    blob = read_blob(file)
                    ret[hash_of_obj] = blob
    return ret


def parse_commit(blob: Blob) -> Commit:
    """
    Parse commit blob
    :param blob: blob with commit type
    :return: parsed commit
    """
    all_lines = blob.content.decode('utf-8').splitlines()
    line_of_tree = all_lines[0].split()
    tree_hash = line_of_tree[1]
    parents = []
    author, committer, message = "", "", ""
    for line_not_stripped in all_lines[1:]:
        line = line_not_stripped.strip()
        if line.startswith("parent"):
            hash_of_parent = line.split()[1]
            parents.append(hash_of_parent)
        elif line.startswith("author"):
            author = line[7:]
        elif line.startswith("committer"):
            committer = line[10:]
        else:
            message = all_lines[-1].strip()
            break

    return Commit(tree_hash=tree_hash, parents=parents, author=author, committer=committer, message=message)


def parse_tree(blobs: dict[str, Blob], tree_root: Blob, ignore_missing: bool = True) -> Tree:
    """
    Parse tree blob
    :param blobs: all read blobs (by traverse_objects)
    :param tree_root: tree blob to parse
    :param ignore_missing: ignore blobs which were not found in objects directory
    :return: tree contains children blobs (or only part of them found in objects directory)
    NB. Children blobs are not being parsed according to type.
        Also nested tree blobs are not being traversed.
    """
    content = tree_root.content
    children = {}
    ind_start = 0
    while ind_start < len(content):
        start = content.find(b' ', ind_start) + 1
        end = content.find(b'\x00', ind_start)
        name = content[start:end].decode('utf-8')
        blob_hash = content[end + 1:end + 21].hex()
        ind_start = end + 21 + 1
        if blob_hash in blobs:
            blob_content = blobs[blob_hash].content
            type_ = blobs[blob_hash].type_
            children[name] = Blob(type_=type_, content=blob_content)

    return Tree(children=children)


def find_initial_commit(blobs: dict[str, Blob]) -> Commit:
    """
    Iterate over blobs and find initial commit (without parents)
    :param blobs: blobs read from objects dir
    :return: initial commit
    """
    for blob_hash, blob in blobs.items():
        if blob.type_ == BlobType.COMMIT:
            commit = parse_commit(blob)
            if not commit.parents:
                return commit
    raise ValueError("Error! No initial commit found!")


def search_file_recursively(blobs: dict[str, Blob], tree_root: Blob, filename: str) -> Blob | None:
    if tree_root.type_ == BlobType.TREE:
        tree = parse_tree(blobs, tree_root, ignore_missing=False)
        if filename in tree.children:
            return tree.children[filename]
        for name, child_blob in tree.children.items():
            if child_blob.type_ == BlobType.TREE:
                ret = search_file_recursively(blobs, child_blob, filename)
                if ret is not None:
                    return ret
    return None


def search_file(blobs: dict[str, Blob], tree_root: Blob, filename: str) -> Blob:
    """
    Traverse tree blob (can have nested tree blobs) and find requested file,
    check if file was not found (assertion).
    :param blobs: blobs read from objects dir
    :param tree_root: root blob for traversal
    :param filename: requested file
    :return: requested file blob
    """
    ret = search_file_recursively(blobs, tree_root, filename)
    if ret is None:
        raise ValueError("File not found")
    return ret
