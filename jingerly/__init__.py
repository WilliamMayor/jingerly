import shutil


def render(template_dir, output_dir, **kwargs):
    shutil.copytree(template_dir, output_dir)
