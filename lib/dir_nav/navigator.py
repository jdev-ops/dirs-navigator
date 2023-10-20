import subprocess
import os

from slugify import slugify

from pathlib import Path

from decouple import config as decouple_config
from decouple import Config, RepositoryEnv

import cattrs

from dir_nav import *

if os.environ.get("CONFIG_PATH"):
    config = Config(RepositoryEnv(os.environ["CONFIG_PATH"]))
elif Path(".env.local").is_file():
    config = Config(RepositoryEnv(".env.local"))
else:
    config = decouple_config

def sel_env():
    import glob
    import sys

    options = glob.glob(f"{os.environ['HOME']}/.navigator/*.yaml")
    values = {}
    for o in options:
        i=o.rfind("/")
        values[o[i+1:-5]]= o
    my_env = os.environ.copy()
    my_env["GUM_FILTER_PLACEHOLDER"] = f"Choose an environment:"
    result = subprocess.run(
        ["gum", "filter"], input="\n".join(values.keys()), stdout=subprocess.PIPE, text=True, env=my_env
    )
    open(f"{os.environ['HOME']}/.navigator/.environment", "w").write(result.stdout.strip())
    return 0

def choose_destination():
    from yaml import load, dump
    try:
        from yaml import CLoader as Loader, CDumper as Dumper
    except ImportError:
        from yaml import Loader, Dumper

    environment = open(f"{os.environ['HOME']}/.navigator/.environment", "r").read()
    doc=load(open(f"{os.environ['HOME']}/.navigator/{environment}.yaml", "r"), Loader=Loader)
    all_paths = cattrs.structure(doc, list[Project])
    values = dict([ (p.name, p.rootPath) for p in all_paths])
    my_env = os.environ.copy()
    my_env["GUM_FILTER_PLACEHOLDER"] = f"Choose an environment:"
    result = subprocess.run(
        ["gum", "filter"], input="\n".join(values.keys()), stdout=subprocess.PIPE, text=True, env=my_env
    )
    print(values[result.stdout.strip()])
    return 0
