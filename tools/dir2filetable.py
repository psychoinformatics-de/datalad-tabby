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
    recursive: bool = False,
    output: str = 'stdout',
):
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

    Args:
        rootpath (str): The root directory for which the table 
            shoult be printed.
        
        hash (str, optional): Name of the algorithm to be used for
            calculating file hashes, e.g. 'md5' or 'sha256'. The
            algorithm must be supported by the Python 'hashlib' module.
            Defaults to 'md5'.
        
        recursive (bool, optional): Set this flag to recurse into
            subdirectories. Defaults to False.

        output (str, optional): A filepath to print the output to.
            Defaults to 'stdout.
    """
    # Get file list
    out_info = []
    _dir2filelist(Path(rootpath), Path(rootpath), out_info, hash, recursive)
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
        outpath = Path(output)
        with open(outpath, 'w', encoding='utf8', newline='') as output_file:
            fc = csv.DictWriter(
                output_file,
                fieldnames=fieldnames,
                delimiter='\t'
            )
            fc.writerow(dict((fn,hn) for (fn,hn) in zip(fieldnames, headernames)))
            fc.writerows(out_info)
    else:
        print(f'{header["hash"]}\t{header["size"]}\t{header["path"]}\t{header["url"]}')
        for el in out_info:
            print(f'{el["hash"]}\t{el["size"]}\t{el["path"]}\t')


def _dir2filelist(
    rootpath: Path,
    relpath: Path,
    result: list,
    hash: str = 'md5',
    recursive: bool = False,
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
        '--recursive', action='store_true',
        help="Generate a file listing recursively for all directories "
        "starting from the root"
    )
    p.add_argument(
        '--output', default='stdout',
        help="Filename to which the output should be printed. If not supplied, "
        "the output is printed to STDOUT"
    )
    args = p.parse_args()
    dir2filetable(
        rootpath=args.directory,
        hash=args.hash,
        recursive=args.recursive,
        output=args.output,
    )
