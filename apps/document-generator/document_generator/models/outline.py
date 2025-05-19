"""
Data models for the Document Generator app.
Defines Resource, Section, and Outline dataclasses with serialization utilities.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any


@dataclass
class Resource:
    key: str
    path: str
    description: str
    merge_mode: str


@dataclass
class Section:
    title: str
    prompt: Optional[str] = None
    refs: List[str] = field(default_factory=list)
    resource_key: Optional[str] = None
    sections: List["Section"] = field(default_factory=list)


def section_from_dict(data: Dict[str, Any]) -> Section:
    return Section(
        title=data.get("title", ""),
        prompt=data.get("prompt"),
        refs=list(data.get("refs", [])),
        resource_key=data.get("resource_key"),
        sections=[section_from_dict(s) for s in data.get("sections", [])],
    )


@dataclass
class Outline:
    title: str
    general_instruction: str
    resources: List[Resource] = field(default_factory=list)
    sections: List[Section] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Outline":
        res_list: List[Resource] = []
        for r in data.get("resources", []):
            res_list.append(
                Resource(
                    key=r.get("key", ""),
                    path=r.get("path", ""),
                    description=r.get("description", ""),
                    merge_mode=r.get("merge_mode", "concat"),
                )
            )
        sec_list: List[Section] = [section_from_dict(s) for s in data.get("sections", [])]
        return cls(
            title=data.get("title", ""),
            general_instruction=data.get("general_instruction", ""),
            resources=res_list,
            sections=sec_list,
        )
