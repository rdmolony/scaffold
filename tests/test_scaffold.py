import os
import subprocess
from pathlib import Path

from ploomber_scaffold import scaffold


def test_cli(tmp_directory):
    scaffold.cli(project_path='my_new_project')
    os.chdir('my_new_project')

    # setup command
    assert not subprocess.run(['invoke', 'setup'])

    # test command
    script = """
    eval "$(conda shell.bash hook)"
    conda activate my_new_project
    invoke test --inplace
    """
    Path('test.sh').write_text(script)

    assert not subprocess.run(['bash', 'test.sh'])
