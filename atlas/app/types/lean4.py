from typing import TypedDict, List, Optional


class SystemInfo(TypedDict):
    os: str
    architecture: str
    python_version: str
    home_dir: str
    current_dir: str


class BinaryDetail(TypedDict):
    available: bool
    path: Optional[str]
    executable: bool
    error: Optional[str]


class BinaryChecks(TypedDict):
    lean: BinaryDetail
    lake: BinaryDetail
    elan: BinaryDetail


class Diagnosis(TypedDict):
    error_message: str
    context: Optional[str]
    error_type: str
    suggestions: List[str]
    severity: str