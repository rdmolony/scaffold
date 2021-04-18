from itertools import chain
from glob import iglob
import os
import subprocess
from pathlib import Path
import shutil
import zipfile
import tarfile

import pytest


def git_tracked_files():
    out = subprocess.run(['git', 'ls-tree', '-r', 'HEAD', '--name-only'],
                         check=True,
                         capture_output=True)
    return out.stdout.decode().splitlines()


def glob_all(path):
    hidden = iglob(str(path / '**' / '.*'), recursive=True)
    normal = iglob(str(path / '**'), recursive=True)
    return chain(hidden, normal)


def files_in_directory(path, exclude_pyc=True):
    path = Path(path)
    files = [
        str(Path(f).relative_to(path)) for f in glob_all(path)
        if '__pycache__' not in f and Path(f).is_file()
    ]

    if exclude_pyc:
        files = [f for f in files if '.pyc' not in f]

    return files


def extract_zip(path, tmp_path):
    with zipfile.ZipFile(path, 'r') as zip_ref:
        zip_ref.extractall(tmp_path)


def extract_tar(path, tmp_path):
    with tarfile.open(path, "r:gz") as tar:
        tar.extractall(tmp_path)


def get_dir_name(tmp_path):
    if any('.dist-info' in f for f in os.listdir(tmp_path)):
        # wheel
        return Path(tmp_path, 'package_name', 'assets')
    else:
        # source dist
        dir_name = os.listdir(tmp_path)[0]
        return Path(tmp_path, dir_name, 'src', 'package_name', 'assets')


def assert_same_files(reference, directory):
    expected = set(reference)
    existing = set(directory)

    missing = expected - existing
    extra = existing - expected

    if missing:
        raise ValueError(f'missing files: {missing}')

    if extra:
        raise ValueError(f'extra files: {extra}')


@pytest.mark.parametrize(
    'fmt, extractor',
    [
        ['bdist_wheel', extract_zip],
        ['sdist', extract_tar],
    ],
)
def test_dist(fmt, extractor, tmp_path):
    """Make sure the wheel does not contain stuff it shouldn't have
    """
    if Path('build').exists():
        shutil.rmtree('build')

    if Path('dist').exists():
        shutil.rmtree('dist')

    subprocess.run(['python', 'setup.py', fmt], check=True)
    extractor(Path('dist', os.listdir('dist')[0]), tmp_path)

    path_dist = get_dir_name(tmp_path)

    reference = [
        str(Path(f).relative_to('src/package_name/template'))
        for f in git_tracked_files() if 'package_name/template' in f
    ]

    generated = files_in_directory(path_dist, exclude_pyc=False)

    assert_same_files(reference, generated)
