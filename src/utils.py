from contextlib import contextmanager
import os
import logging
import random
import re
import itertools

logger = logging.getLogger(
    "{0}".format(__name__)
)
method_pattern = re.compile(
    r"\.method.+?(?P<method_name>\S+?)"
    r"\((?P<method_param>\S*?)\)"
    r"(?P<method_return>\S+)",
    re.UNICODE,
)
class_pattern = re.compile(r"\.class.+?(?P<class_name>\S+?;)", re.UNICODE)
def get_random_list_permutations(input_list: list) -> list:
    permuted_list = list(itertools.permutations(input_list))
    random.shuffle(permuted_list)
    return permuted_list

# Referenced from https://www.zopatista.com/python/2013/11/26/inplace-file-rewriting/
@contextmanager
def edit_file(file_name: str):
    """
    Allow for a file to be replaced with new content. Yield a tuple of (readable, writable) file objects,
    where writable replaces readable.

    If an exception occurs, the old file is restored, removing the written data.
    """

    backup_file_name = "{0}{1}{2}".format(file_name, os.extsep, "bak")

    try:
        os.unlink(backup_file_name)
    except OSError:
        pass
    os.rename(file_name, backup_file_name)

    readable = open(backup_file_name, "r", encoding="utf-8")
    try:
        perm = os.fstat(readable.fileno()).st_mode
    except OSError:
        writable = open(file_name, "w", encoding="utf-8", newline="")
    else:
        os_mode = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
        if hasattr(os, "O_BINARY"):
            os_mode |= os.O_BINARY
        fd = os.open(file_name, os_mode, perm)
        writable = open(fd, "w", encoding="utf-8", newline="")
        try:
            if hasattr(os, "chmod"):
                os.chmod(file_name, perm)
        except OSError:
            pass
    try:
        yield readable, writable
    except Exception as e:
        try:
            os.unlink(file_name)
        except OSError:
            pass
        os.rename(backup_file_name, file_name)

        logger.error(
            'Error during editing file "{0}": {1}'.format(file_name, e)
        )
        raise
    finally:
        readable.close()
        writable.close()
        try:
            os.unlink(backup_file_name)
        except OSError:
            pass

# For any methods that require random
def get_ran_int(min: int, max: int):
	return random.randint(min,max)

# For any methods that read from file resources
def get_file_contents(file):
	with open(file, "r", encoding="utf-8") as f:
		return list(line.strip() for line in f)

# For methods that require op codes
def get_op_codes():
	return get_file_contents(os.path.join(os.path.dirname(__file__),"resources","op_codes.txt"))