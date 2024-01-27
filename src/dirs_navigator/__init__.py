from attrs import define, field
import cattrs

@define
class Project:
    name: str = field()
    rootPath: str = field()
