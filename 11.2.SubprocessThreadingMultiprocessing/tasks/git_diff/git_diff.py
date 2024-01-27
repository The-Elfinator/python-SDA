import os
import subprocess
from pathlib import Path


def get_changed_dirs(git_path: Path, from_commit_hash: str, to_commit_hash: str) -> set[Path]:
    """
    Get directories which content was changed between two specified commits
    :param git_path: path to git repo directory
    :param from_commit_hash: hash of commit to do diff from
    :param to_commit_hash: hash of commit to do diff to
    :return: sequence of changed directories between specified commits
    """
    os.chdir(git_path)
    diff_output = subprocess.check_output(["git", "diff", "--name-only", from_commit_hash, to_commit_hash],
                                          universal_newlines=True)
    changed_files = diff_output.strip().split('\n')
    return {Path(file).resolve().parent for file in changed_files}
