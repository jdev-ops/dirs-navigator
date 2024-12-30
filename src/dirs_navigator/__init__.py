from attrs import define, field
import cattrs
from pathlib import Path
from collections.abc import Iterable


@define
class AstNode:
    pass


@define
class AstBasic(AstNode):
    tag: str = field()
    dirs: list[Path] = field()


@define
class AstWorkTree(AstNode):
    tag: str = field()
    cwd: Path = field()


@define
class AstExpansion(AstNode):
    tag: str = field()
    cwd: Path = field()
    level: int = field()


@define
class WorkTree:
    path: str = field()
    tag: str = field()


@define
class RootGroup:
    # git_working_trees: list[str] = field(metadata={"alias": "git-working-trees"})
    # base_paths: list[str] = field(metadata={"alias": "base-paths"})
    git_working_trees: list[WorkTree] | None = field()
    base_paths: Iterable[str] | None = field()


@define
class Expansion:
    path: str = field()
    level: int = field()
    cwd: str | None = field()
    tag: str = field()


# type TPath = list[str] | list[Node] | None
# type TPath = list[str] | None


@define
class Node:
    base_paths: list[str] | None = field()
    expansions: list[Expansion] | None = field()
    excludes: list[str] | None = field()
    includes: list[str] | None = field()
    cwd: Path | None = field()
    tag: str = field()


converter = cattrs.Converter()

# Register structure hooks to handle hyphens in field names
converter.register_structure_hook(
    RootGroup,
    lambda d, _: RootGroup(
        git_working_trees=(
            converter.structure(d["git-working-trees"], list[WorkTree])
            if "git-working-trees" in d.keys()  # TODO: clean this
            else None
        ),
        base_paths=d.get("base-paths"),
    ),
)

converter.register_structure_hook(
    Expansion,
    lambda d, _: Expansion(
        path=d["path"],
        level=d["level"],
        cwd=d.get("cwd"),
        tag=d["tag"],
    ),
)

converter.register_structure_hook(
    WorkTree,
    lambda d, _: WorkTree(
        path=d["path"],
        tag=d["tag"],
    ),
)

converter.register_structure_hook(
    Node,
    lambda d, _: Node(
        base_paths=d.get("base-paths"),
        expansions=(
            converter.structure(d["expansions"], list[Expansion])
            if "expansions" in d.keys()
            else None
        ),
        excludes=d.get("excludes"),
        includes=d.get("includes"),
        cwd=d.get("cwd"),
        tag=d["tag"],
    ),
)
