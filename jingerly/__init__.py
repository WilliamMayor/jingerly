import os
import shutil

from jinja2 import Environment, DebugUndefined


def walk(root, ignore):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = filter(lambda dn: dn not in ignore, dirnames)
        filenames = filter(lambda fn: fn not in ignore, filenames)
        yield dirpath, dirnames, filenames


def render(template_dir, output_dir, _ignore=None, **kwargs):
    if _ignore is None:
        _ignore = ['.DS_Store', '.git']
    env = Environment(undefined=DebugUndefined)
    env.filters['copy'] = lambda p: p
    env.filters['download'] = lambda p: p
    shutil.copytree(template_dir, output_dir)
    for root, dirs, files in walk(output_dir, _ignore):
        for f in files:
            file_path = os.path.join(root, f)
            file_name = env.from_string(f).render(
                IN=template_dir, OUT=output_dir,
                **kwargs)
            with open(file_path, 'rb') as fd:
                template = env.from_string(fd.read())
            if file_name != f:
                os.remove(file_path)
                file_path = os.path.join(root, file_name)
            with open(file_path, 'wb') as fd:
                fd.write(
                    template.render(
                        IN=template_dir, OUT=output_dir,
                        **kwargs))
        dir_names = []
        for d in dirs:
            dir_path = os.path.join(root, d)
            dir_name = env.from_string(d).render(
                IN=template_dir, OUT=output_dir,
                **kwargs)
            dir_names.append(dir_name)
            if dir_name != d:
                shutil.move(dir_path, os.path.join(root, dir_name))
        dirs[:] = dir_names
