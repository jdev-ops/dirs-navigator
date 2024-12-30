import subprocess
import os
import sys
import glob
from pathlib import Path
from shutil import *

# import pprint

import traceback
import logging
from rich import print

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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f"{os.environ['HOME']}/.navigator/debug.log"),
        # logging.StreamHandler(sys.stdout),
    ],
    force=True,
)


def normalize_path(path: str) -> str:
    if path.startswith("~"):
        return path.replace("~", os.environ["HOME"])
    return path


def create_ast(rg: RootGroup) -> list[AstNode]:
    ast_nodes: list[AstNode] = []
    nodes: list[Node] = []
    match rg:
        case RootGroup(git_working_trees=[_, *_] as git_working_trees):
            for wt in git_working_trees:
                ast_nodes.append(
                    AstWorkTree(cwd=Path(normalize_path(wt.path)), tag=wt.tag)
                )

    match rg:
        case RootGroup(base_paths=[_, *_] as base_paths):
            rg.base_paths = map(lambda e: normalize_path(e), base_paths)
            for bp in rg.base_paths:
                nav_path = Path(bp)
                nav_file = nav_path / ".navigator.yml"
                node = deserialize(nav_file, Node)
                if node:
                    node.cwd = nav_path
                    nodes.append(node)

    np, nodes = split_nodes(nodes)
    while np and np.base_paths:
        for bp in np.base_paths:
            nav_path = np.cwd / Path(bp)
            nav_file = nav_path / ".navigator.yml"
            node = deserialize(nav_file, Node)
            if node:
                node.cwd = nav_path
                nodes.append(node)
        nodes.append(np)
        np.base_paths = None
        np, nodes = split_nodes(nodes)

    for n in nodes:
        match n:
            case Node(expansions=[_, *_] as expansions):
                for ex in expansions:
                    ast_nodes.append(
                        AstExpansion(
                            cwd=n.cwd / ex.path, level=ex.level, tag=f"{n.tag}:{ex.tag}"
                        )
                    )

    for n in nodes:
        # files = [f for f in glob.glob(os.path.join(n.cwd, "*")) if Path(f).is_dir()]
        files = [
            f.as_posix()
            for f in n.cwd.glob("*")
            if f.is_dir() and not f.parts[-1].startswith(".")
        ]
        parts = []

        match n:
            case Node(expansions=[_, *_] as expansions):
                for e in expansions:
                    parts.append(Path(e.path).parts[0])
        match n:
            case Node(excludes=[_, *_] as excludes):
                excludes = [f"{n.cwd}/{ex}" for ex in excludes]
                for f in files:
                    checked_parts = map(lambda p: f.endswith(p), parts)
                    if any(checked_parts):
                        excludes.append(f)
                files = set(files) - set(excludes)
                ast_nodes.append(AstBasic(n.tag, [Path(f) for f in files]))
            case Node(includes=[_, *_] as includes):
                excludes = []
                files = [f"{n.cwd}/{f}" for f in includes]
                for f in files:
                    checked_parts = map(lambda p: f.endswith(p), parts)
                    if any(checked_parts):
                        excludes.append(f)
                files = set(files) - set(excludes)
                # remove the expansions
                ast_nodes.append(AstBasic(n.tag, [Path(f) for f in files]))

    return ast_nodes


def get_options(ast_nodes: list[AstNode]) -> dict[str, str]:
    repeated = False
    result = dict()
    for ast in ast_nodes:
        match ast:
            case AstExpansion(tag=tag, cwd=cwd, level=level):
                res = subprocess.run(
                    f"fd --max-depth {level} --type d",
                    stdout=subprocess.PIPE,
                    text=True,
                    shell=True,
                    cwd=cwd,
                )

                l = res.stdout.strip()
                lines = [f for f in l.splitlines() if len(Path(f).parts) == level]
                for l in lines:
                    key = f"{tag}:{Path(l).parts[-1]}"
                    value = f"{cwd}/{l}"
                    if key in result:
                        logging.error(
                            f"{key} is already present, ctx:type=AstExpansion,tag={tag},cwd={cwd}"
                        )
                        repeated = True
                    else:
                        result[key] = value
            case AstWorkTree(tag=tag, cwd=cwd):
                res = subprocess.run(
                    "git worktree list | hck -f1",
                    stdout=subprocess.PIPE,
                    text=True,
                    shell=True,
                    cwd=cwd,
                )
                l = res.stdout.strip()
                for l in l.splitlines():
                    key = f"{tag}:{Path(l).parts[-1]}"
                    value = l
                    if key in result:
                        logging.error(
                            f"{key} is already present, ctx:type=AstWorkTree,tag={tag},cwd={cwd}"
                        )
                        repeated = True
                    else:
                        result[key] = value
                    # result.append(key)
                    # result.append(value)
            case AstBasic(tag=tag, dirs=dirs):
                for l in dirs:
                    key = f"{tag}:{Path(l).parts[-1]}"
                    value = l.as_posix()
                    if key in result:
                        logging.error(
                            f"{key} is already present, ctx:type=AstBasic,tag={tag},dir={l}"
                        )
                        repeated = True
                    else:
                        result[key] = value
                    # result.append(key)
                    # result.append(value)

    if repeated:
        result["repeated-key (this is only an information, check the logs)"] = True
    return result


def find_and_remove_first(lst, condition):
    """
    Finds and removes the first element in the list that satisfies the condition.

    Parameters:
    lst (list): The list to search through.
    condition (function): A function that takes an element and returns True if the condition is met.

    Returns:
    The removed element if found, otherwise None.
    """
    for i, element in enumerate(lst):
        if condition(element):
            return lst.pop(i)
    return None


def split_nodes(nodes):
    res = find_and_remove_first(nodes, lambda n: n.base_paths)
    return res, nodes


def get_home_path() -> Path:
    return Path(f"{os.environ['HOME']}")


def read_all_content(path: Path) -> str | None:
    try:
        environment = open(path)
        return environment.read()
    except:
        logging.error(traceback.format_exc())
        return None


def deserialize[T](path: Path, clazz: T) -> T | None:
    try:
        content = load(open(path), Loader=Loader)
        return converter.structure(content, clazz)
    except:
        logging.error(traceback.format_exc())
        return None


def load_projects() -> dict[str, str]:
    env_file = read_all_content(get_home_path() / ".navigator/.environment")
    if env_file:
        nav_file = get_home_path() / f".navigator/entries/{env_file}.yml"
        root = deserialize(nav_file, RootGroup)
        if root:
            ast_list = create_ast(root)
            # print(ast_list)
            return get_options(ast_list)
    return {}


def projects_names():
    projects = load_projects()
    print("\n".join(projects.keys()))
    return 0


def project_path_(result: str) -> int:
    return project_path(result)


def project_path(result: str, projects_values: dict[str, str] | None = None) -> int:
    projects = projects_values if projects_values else load_projects()
    sel = result.strip()
    if sel:
        selected_path = projects[sel]
        if selected_path.startswith("~"):
            selected_path = selected_path.replace("~", get_home_path().as_posix())
        print(selected_path, end="")
        return 0
    else:
        return 1


def choose_project():
    posible_values = load_projects()
    result = subprocess.run(
        ["fzf"],
        input="\n".join(posible_values.keys()),
        stdout=subprocess.PIPE,
        text=True,
    )
    return project_path(result.stdout, posible_values)


def sel_env():
    options = glob.glob(f"{os.environ['HOME']}/.navigator/entries/*.yml")
    options = [Path(o).parts[-1][:-4] for o in options]
    my_env = os.environ.copy()
    # my_env["GUM_FILTER_PLACEHOLDER"] = f"Choose an environment:"
    result = subprocess.run(
        # ["gum", "filter"],
        ["fzf"],
        input="\n".join(options),
        stdout=subprocess.PIPE,
        text=True,
        env=my_env,
    )
    if result.stdout:
        open(f"{os.environ['HOME']}/.navigator/.environment", "w").write(
            result.stdout.strip()
        )
    return 0
