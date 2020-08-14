from typing import Sequence, Union, Mapping, List
import shutil
from subprocess import CompletedProcess

from exceptions import OutputError


def check_output(proc: CompletedProcess):
    try:
        assert proc.returncode == 0
    except AssertionError:
        raise OutputError(f"Invalid output: {proc}")



def concat(files: Sequence[str],
           output: str,
           rm: bool = False):
    with open(output, 'wb') as wf:
        for f in files:
            with open(f, 'rb') as rf:
                shutil.copyfileobj(rf, wf)


def flatten(arg_map: Mapping[str, str]) -> List[str]:
    flattened = []
    if arg_map is not None:
        for key in arg_map.keys():
            flattened.append("-" + key)
            flattened.append(arg_map[key])
    return flattened

