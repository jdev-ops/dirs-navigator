from attrs import define, field
import cattrs


@define
class Project:
    name: str = field()
    rootPath: str = field()


@define
class ProjectGroup:
    name: str = field()
    entries: list[Project] = field()
