import os
from dataclasses import dataclass


@dataclass
class JohnnyDecimal:
    path: str

    @property
    def basename(self) -> str:
        return os.path.splitext(os.path.basename(self.path))[0]

    @property
    def category_index(self) -> str:
        return os.path.basename(os.path.dirname(self.path)).split("-", 1)[0]

    @property
    def index(self) -> str:
        return self.basename.split("-", 1)[0]

    @property
    def full_index(self) -> str:
        return f"{self.category_index}.{self.index}"
