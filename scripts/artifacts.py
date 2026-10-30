"""Stage outputs safely without following pre-existing filesystem links.

These helpers protect evidence from accidental output paths, not concurrent
hostile directory changes. Unrelated output-directory files are preserved.
"""
from contextlib import contextmanager
import os
from pathlib import Path
import stat
import tempfile


def _absolute(path):
    raw = Path(path).expanduser().absolute()
    # Canonicalize only the operating system's trusted temporary-root prefix
    # (for example /var -> /private/var on macOS). User-created links below
    # that prefix are still inspected and rejected rather than resolved away.
    temporary_root = Path(tempfile.gettempdir()).absolute()
    if raw.is_relative_to(temporary_root):
        raw = temporary_root.resolve() / raw.relative_to(temporary_root)
    return raw


def is_link(path):
    """Recognize symlinks and Windows reparse points, including junctions."""
    path = Path(path)
    if path.is_symlink():
        return True
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return bool(getattr(info, 'st_file_attributes', 0)
                & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0))


def _check_ancestors(path):
    for candidate in (path, *path.parents):
        if is_link(candidate):
            raise ValueError('Refusing symlink output path: ' + str(candidate))
        if candidate != path and candidate.exists() and not candidate.is_dir():
            raise ValueError('Output parent is not a directory: ' + str(candidate))


def _check_file(path):
    _check_ancestors(path)
    if path.exists():
        info = path.stat()
        if not stat.S_ISREG(info.st_mode):
            raise ValueError('Output is not a regular file: ' + str(path))
        if info.st_nlink != 1:
            raise ValueError('Refusing hard-linked output file: ' + str(path))


def _check_tree(directory):
    _check_ancestors(directory)
    if directory.exists() and not directory.is_dir():
        raise ValueError('Output destination is not a directory: ' + str(directory))
    if not directory.exists():
        return
    def failed_walk(error):
        raise ValueError('Cannot inspect output directory: ' + str(error)) from error
    for parent, directories, files in os.walk(directory, followlinks=False, onerror=failed_walk):
        for name in directories:
            path = Path(parent) / name
            _check_ancestors(path)
            if not path.is_dir():
                raise ValueError('Output member is not a directory: ' + str(path))
        for name in files:
            _check_file(Path(parent) / name)


def prepare_output_dir(path, root):
    """Check the entire existing destination before generating any outputs."""
    raw = _absolute(path)
    _check_ancestors(raw)
    directory = raw.resolve()
    root = Path(root).resolve()
    if directory == root or (root in directory.parents and not directory.is_relative_to(root / 'build')):
        raise ValueError('Write outputs to build/ or outside the checkout; frozen project files must not be overwritten')
    _check_tree(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


@contextmanager
def atomic_open(path, *, encoding='utf-8', newline=''):
    """Yield a text stream; publish only after a successful context exit."""
    path = _absolute(path)
    _check_file(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding=encoding, newline=newline,
                                         dir=path.parent, prefix='.' + path.name + '.', delete=False) as handle:
            temporary = Path(handle.name)
            yield handle
        _check_file(path)
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_text(path, content, *, encoding='utf-8'):
    with atomic_open(path, encoding=encoding, newline='\n') as handle:
        handle.write(content)


def write_bytes(path, content):
    path = _absolute(path)
    _check_file(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', dir=path.parent, prefix='.' + path.name + '.', delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        _check_file(path)
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


@contextmanager
def output_transaction(destination, *, root):
    """Validate a complete calculation before publishing each file atomically.

    A failed calculation or comparison publishes none of the attempt's files.
    Existing unrelated inputs/logs are retained. Publication across multiple
    files is not claimed to be a single filesystem-atomic directory operation.
    """
    destination = prepare_output_dir(destination, root)
    with tempfile.TemporaryDirectory(prefix='patoshi-output-') as temporary:
        staged = Path(temporary).resolve()
        yield staged
        _check_tree(staged)
        _check_tree(destination)
        files = sorted(path for path in staged.rglob('*') if path.is_file())
        for path in files:
            _check_file(destination / path.relative_to(staged))
        for path in files:
            write_bytes(destination / path.relative_to(staged), path.read_bytes())
