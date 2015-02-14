import imp
import subprocess
import os
import shutil

import requests
from jinja2 import Environment, DebugUndefined, meta

ALLOWED_TYPES = [
    type(True), type(0), type(0.0), type(0l), type(0+0j), type(''), type(u''),
    type([]), type((1,)), type(set()), type({})]


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


def __make_variables(template_dir, output_dir, kwargs):
    variables = kwargs.copy()
    variables['IN'] = template_dir
    variables['OUT'] = output_dir
    env_path = os.path.join(template_dir, 'jingerly.env')
    if os.path.isfile(env_path):
        env = imp.load_source('module.name', env_path)
        for name in dir(env):
            if name.startswith('__'):
                continue
            attr = getattr(env, name)
            if type(attr) in ALLOWED_TYPES:
                variables[name] = attr
    return variables


def __make_renderer(env, variables):
    def renderer(text):
        template = env.from_string(text)
        return template.render(**variables)
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


def __run_script(script_path, renderer):
    if os.path.isfile(script_path):
        with open(script_path, 'rb') as fd:
            file_contents = renderer(fd.read())
        with open(script_path, 'wb') as fd:
            fd.write(file_contents)
        subprocess.call(script_path)


def __run_pre(output_dir, renderer):
    script_path = os.path.join(output_dir, 'jingerly.pre')
    __run_script(script_path, renderer)


def __run_post(output_dir, renderer):
    script_path = os.path.join(output_dir, 'jingerly.post')
    __run_script(script_path, renderer)


def __clean(path):
    for name in ['jingerly.pre', 'jingerly.post', 'jingerly.env']:
        try:
            os.remove(os.path.join(path, name))
        except OSError:
            pass


def render(template_dir, output_dir, _ignore=None, **kwargs):
    shutil.copytree(template_dir, output_dir)
    if _ignore is None:
        _ignore = ['.DS_Store', '.git']
    env = __make_env()
    variables = __make_variables(template_dir, output_dir, kwargs)
    renderer = __make_renderer(env, variables)
    __run_pre(output_dir, renderer)
    for root, dirs, files in __walk(output_dir, _ignore):
        __process_files(
            root, files, renderer)
        dirs[:] = __process_dirs(
            root, dirs, renderer)
    __run_post(output_dir, renderer)
    __clean(output_dir)


def find_variables(template_dir, _ignore=None):
    if _ignore is None:
        _ignore = ['.DS_Store', '.git', 'jingerly.env']
    env = __make_env()
    known = __make_variables(template_dir, template_dir, {})
    unknown = set()
    for root, dirs, files in __walk(template_dir, _ignore):
        for f in files:
            ast = env.parse(f)
            unknown |= meta.find_undeclared_variables(ast)
            with open(os.path.join(root, f), 'rb') as fd:
                ast = env.parse(fd.read())
                unknown |= meta.find_undeclared_variables(ast)
        for d in dirs:
            ast = env.parse(d)
            unknown |= meta.find_undeclared_variables(ast)
    return filter(lambda n: n not in known, unknown)
