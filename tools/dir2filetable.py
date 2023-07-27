#!/usr/bin/env python3
"""
Print a table with information about the files contained in
a directory on a filesystem. File information is compliant
with the tabby convention for a collection-of-files dataset
(see: https://docs.datalad.org/projects/tabby/en/latest/conventions/tby-ds1.html)
and includes:
    - the file path (column: path[POSIX])
    - the file content checksum, using a specified hash algorithm
      which defaults to md5 (column: checksum[md5])
    - the file size in bytes (column: size[bytes])

The output table can be printed to STDOUT or to a text file in TSV format.
"""
import os
from pathlib import Path
import argparse
import hashlib
import csv


def dir2filetable(
    rootpath: str,
    hash: str = 'md5',
    nonrecursive: bool = False,
    output: str = 'stdout',
):
    """
    Print a table with information about the files contained in
    a directory on a filesystem.

    Args:
        rootpath (str): The root directory for which the table 
            shoult be printed.
        
        hash (str, optional): Name of the algorithm to be used for
            calculating file hashes, e.g. 'md5' or 'sha256'. The
            algorithm must be supported by the Python 'hashlib' module.
            Defaults to 'md5'.
        
        recursive (bool, optional): Set this flag to recurse into
            subdirectories. Defaults to False.

        output (str, optional): A directory of filename to save the
            output to. Defaults to 'stdout.
    """
    # Get file list
    out_info = []
    _dir2filelist(Path(rootpath), Path(rootpath), out_info, hash, not nonrecursive)
    # Output the data
    # header compliant with tby-ds1 convention
    header = {
        'path': 'path[POSIX]',
        'size': 'size[bytes]',
        'hash': f'checksum[{hash}]',
        'url': 'url'
    }
    fieldnames = out_info[0].keys()
    headernames = [header[fn] for fn in fieldnames]
    if output != 'stdout':
        outpath = _get_output_path(output)
        with open(outpath, 'w', encoding='utf8', newline='') as output_file:
            fc = csv.DictWriter(
                output_file,
                fieldnames=fieldnames,
                delimiter='\t'
            )
            fc.writerow(dict((fn,hn) for (fn,hn) in zip(fieldnames, headernames)))
            fc.writerows(out_info)
        print(f'Output saved to: {outpath.absolute()}')
    else:
        print(f'{header["hash"]}\t{header["size"]}\t{header["path"]}\t{header["url"]}')
        for el in out_info:
            print(f'{el["hash"]}\t{el["size"]}\t{el["path"]}\t')


def _dir2filelist(
    rootpath: Path,
    relpath: Path,
    result: list,
    hash: str = 'md5',
    recursive: bool = True,
):
    """"""
    if relpath is None:
        relpath=rootpath
    for f in relpath.glob('*'):
        if f.is_file():
            f_info = get_file_info(rp=rootpath,
                                   fp=f,
                                   hash_algo=hash)
            result.append(f_info)                
        elif f.is_dir():
            if recursive:
                _dir2filelist(rootpath, f, result, hash, recursive)
        else:
            # what to do here?
            pass
    return


def get_file_info(rp: Path, fp: Path, hash_algo: str = 'md5'):
    """
    Returns a dict with path, checksum, and size in bytes
    of a Path object (path is relative to a root Path)
    """
    with open(fp, "rb") as f:
        hashclass = getattr(hashlib, hash_algo)
        h = hashlib.file_digest(f, hashclass)
    stats = os.stat(str(fp))
    return dict(path=fp.relative_to(rp),
                size=stats.st_size,
                hash=h.hexdigest(),
                url='',
    )


def _get_output_path(out_str):
    """
    Creates Path object from the provided output string with a filename
    compliant with the tabby convention for a collection-of-files dataset (see: 
    https://docs.datalad.org/projects/tabby/en/latest/conventions/tby-ds1.html)

    If an existing directory is provided, the output filename will be
    'files@tby-ds1.tsv', saved to the provided directory. If not, the provided
    path will be interpreted as a filename, from which the prefix will be
    derived, which is then prepended to '_files@tby-ds1.tsv' to form the output
    filename.
    """
    outpath = Path(out_str)
    if outpath.is_dir():
        output_path = outpath / 'files@tby-ds1.tsv'
    else:
        # isolate prefix, without extension/suffix and without
        # TODO: remove any redundancies in prefix e.g. if user
        # provided an output filename already containing tby-ds1
        # convention specification
        prefix = outpath.stem
        output_path = outpath.parent / f'{prefix}_files@tby-ds1.tsv'
    # return tby-ds1 compliant file sheet name
    return output_path


if __name__ == '__main__':
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "directory", metavar='PATH',
        help="Directory for which a tabby file listing should be generated."
    )
    p.add_argument(
        '--hash', metavar='HASH', default='md5',
        help="Name of the algorithm to be used for calculating file hashes, "
        "e.g. 'md5' or 'sha256'. The algorithm must be supported by the Python "
        "'hashlib' module. Default = 'md5'"
    )
    p.add_argument(
        '--non-recursive', action='store_true',
        help="Do not recurse into subdirectories when generating a file listing "
        "for a given root path. Default = False, i.e. recursion always happens "
        "unless this flag is passed."
    )
    p.add_argument(
        '--output', default='stdout',
        help="Directory or filename to which the output should be saved. "
        "If an existing directory is supplied, the file 'files@tby-ds1.tsv' "
        "will be saved to that directory. "
        "If a filename supplied, it will be used to derive the prefix which is "
        "then prepended to '_files@tby-ds1.tsv' to form the filename at which the "
        "output will be saved. "
        "If this argument is not supplied, the output is printed to STDOUT"
    )
    args = p.parse_args()
    dir2filetable(
        rootpath=args.directory,
        hash=args.hash,
        nonrecursive=args.non_recursive,
        output=args.output,
    )
