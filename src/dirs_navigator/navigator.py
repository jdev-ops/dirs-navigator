import subprocess
import os
import glob
from pathlib import Path

from decouple import config as decouple_config
from decouple import Config, RepositoryEnv

from yaml import load

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from dirs_navigator import *

if os.environ.get("CONFIG_PATH"):
    config = Config(RepositoryEnv(os.environ["CONFIG_PATH"]))
elif Path(".env.local").is_file():
    config = Config(RepositoryEnv(".env.local"))
else:
    config = decouple_config

def load_projects() -> dict[str, str]:
    options = glob.glob(f"{os.environ['HOME']}/.navigator/*.yaml")
    values = {}
    for o in options:
        i = o.rfind("/")
        values[o[i + 1 : -5]] = o
    posible_values = {}
    for k, v in values.items():
        doc = load(open(v), Loader=Loader)
        all_paths = cattrs.structure(doc, list[Project])
        for p in all_paths:
            posible_values[f"{k}:{p.name}"] = p.rootPath
    return posible_values

def projects_names():
    projects = load_projects()
    print("\n".join(projects.keys()))
    return 0

def project_path_(result: str) -> int:
    return project_path(result)

def project_path(result: str, projects_values:  dict[str, str] | None  = None) -> int:
    projects = projects_values if projects_values else load_projects()
    sel = result.strip()
    if sel:
        selected_path = projects[sel]
        if selected_path.startswith("~"):
            selected_path = selected_path.replace("~", os.environ["HOME"])
        print(selected_path, end="")
        return 0
    else:
        return 1

def sel_env2():
    # options = glob.glob(f"{os.environ['HOME']}/.navigator/*.yaml")
    # values = {}
    # for o in options:
    #     i = o.rfind("/")
    #     values[o[i + 1 : -5]] = o
    # posible_values = {}
    # for k, v in values.items():
    #     doc = load(open(v), Loader=Loader)
    #     all_paths = cattrs.structure(doc, list[Project])
    #     for p in all_paths:
    #         posible_values[f"{k}:{p.name}"] = p.rootPath
    posible_values = load_projects()
    result = subprocess.run(
        ["fzf"],
        input="\n".join(posible_values.keys()),
        stdout=subprocess.PIPE,
        text=True,
    )
    return project_path(result.stdout, posible_values)
    # sel = result.stdout.strip()
    # if sel:
    #     selected_path = posible_values[sel]
    #     if selected_path.startswith("~"):
    #         selected_path = selected_path.replace("~", os.environ["HOME"])
    #     print(selected_path)
    #     return 0
    # else:
    #     return 1


def sel_env():
    options = glob.glob(f"{os.environ['HOME']}/.navigator/*.yaml")
    values = {}
    for o in options:
        i = o.rfind("/")
        values[o[i + 1 : -5]] = o
    my_env = os.environ.copy()
    my_env["GUM_FILTER_PLACEHOLDER"] = f"Choose an environment:"
    result = subprocess.run(
        ["gum", "filter"],
        input="\n".join(values.keys()),
        stdout=subprocess.PIPE,
        text=True,
        env=my_env,
    )
    open(f"{os.environ['HOME']}/.navigator/.environment", "w").write(
        result.stdout.strip()
    )
    return 0


def choose_destination():
    environment = open(f"{os.environ['HOME']}/.navigator/.environment").read()
    doc = load(
        open(f"{os.environ['HOME']}/.navigator/{environment}.yaml"), Loader=Loader
    )
    all_paths = cattrs.structure(doc, list[Project])
    values = {p.name: p.rootPath for p in all_paths}
    my_env = os.environ.copy()
    my_env["GUM_FILTER_PLACEHOLDER"] = f"Choose an environment:"
    result = subprocess.run(
        ["gum", "filter"],
        input="\n".join(values.keys()),
        stdout=subprocess.PIPE,
        text=True,
        env=my_env,
    )
    sel = result.stdout.strip()
    if sel:
        selected_path = values[sel]
        if selected_path.startswith("~"):
            selected_path = selected_path.replace("~", os.environ["HOME"])
        print(selected_path)
        return 0
    else:
        return 1
