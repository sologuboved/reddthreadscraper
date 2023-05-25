from functools import wraps
import json
import os
import re
import sys
import time


def dump_utf_json(entries, json_file):
    print(f"Dumping {len(entries)} entries into {json_file}...")
    with open(get_abs_path(json_file), 'w', encoding='utf-8') as handler:
        json.dump(entries, handler, ensure_ascii=False, sort_keys=True, indent=2)


def which_watch(func):
    @wraps(func)
    def wrapper(*args, **kwargs):

        def report_time():
            print("'{}' took {}".format(
                func.__name__,
                time.strftime("%H:%M:%S", time.gmtime(time.perf_counter() - start)),
            ))

        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except BaseException as e:
            raise e
        else:
            return result
        finally:
            report_time()

    return wrapper


def get_base_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_abs_path(fname):
    return os.path.join(get_base_dir(), fname)


def write_pid():
    prefix = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    previous_pid = find_previous_pid(prefix)
    if previous_pid:
        print(f"\nRemoving {previous_pid}...")
        os.remove(previous_pid)
    pid_fname = get_abs_path(f'{prefix}_{os.getpid()}.pid')
    print(f"Writing {pid_fname}\n")
    with open(pid_fname, 'w') as handler:
        handler.write(str())
    return pid_fname


def delete_pid(pid_fname):
    try:
        os.remove(pid_fname)
    except FileNotFoundError as e:
        print(str(e))


def find_previous_pid(prefix):
    for fname in os.listdir(get_base_dir()):
        if re.fullmatch(rf'{prefix}_\d+\.pid', fname):
            return get_abs_path(fname)
