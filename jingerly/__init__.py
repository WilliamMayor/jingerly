import subprocess
import os
import shutil

import requests
from jinja2 import Environment, DebugUndefined


def __walk(root, ignore):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = filter(lambda dn: dn not in ignore, dirnames)
        filenames = filter(lambda fn: fn not in ignore, filenames)
        yield dirpath, dirnames, filenames


def __filter_copy(path):
    with open(path, 'rb') as fd:
        return fd.read()


def __filter_download(url):
    return requests.get(url).content


def __make_env():
    env = Environment(undefined=DebugUndefined)
    env.filters['copy'] = __filter_copy
    env.filters['download'] = __filter_download
    return env


def __make_renderer(env, template_dir, output_dir, kwargs):
    def renderer(text):
        template = env.from_string(text)
        return template.render(IN=template_dir, OUT=output_dir, **kwargs)
    return renderer


def __process_files(root, files, renderer):
    for f in files:
        file_path = os.path.join(root, f)
        file_name = renderer(f)
        with open(file_path, 'rb') as fd:
            file_contents = renderer(fd.read())
        if file_name != f:
            os.remove(file_path)
            file_path = os.path.join(root, file_name)
        with open(file_path, 'wb') as fd:
            fd.write(file_contents)


def __process_dirs(root, dirs, renderer):
    dir_names = []
    for d in dirs:
        dir_path = os.path.join(root, d)
        dir_name = renderer(d)
        dir_names.append(dir_name)
        if dir_name != d:
            shutil.move(dir_path, os.path.join(root, dir_name))
    return dir_names


def __run_script_and_delete(script_path, renderer):
    if os.path.isfile(script_path):
        with open(script_path, 'rb') as fd:
            file_contents = renderer(fd.read())
        with open(script_path, 'wb') as fd:
            fd.write(file_contents)
        subprocess.call(script_path)
        os.remove(script_path)


def __run_pre(output_dir, renderer):
    script_path = os.path.join(output_dir, 'jingerly.pre')
    __run_script_and_delete(script_path, renderer)


def __run_post(output_dir, renderer):
    script_path = os.path.join(output_dir, 'jingerly.post')
    __run_script_and_delete(script_path, renderer)


def render(template_dir, output_dir, _ignore=None, **kwargs):
    if _ignore is None:
        _ignore = ['.DS_Store', '.git']
    env = __make_env()
    renderer = __make_renderer(env, template_dir, output_dir, kwargs)
    shutil.copytree(template_dir, output_dir)
    __run_pre(output_dir, renderer)
    for root, dirs, files in __walk(output_dir, _ignore):
        __process_files(
            root, files, renderer)
        dirs[:] = __process_dirs(
            root, dirs, renderer)
    __run_post(output_dir, renderer)
