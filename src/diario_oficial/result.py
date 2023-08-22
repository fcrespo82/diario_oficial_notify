from dataclasses import dataclass

@dataclass
class Result:
    text: str
    url: str
    url_text: str
    title: str|None = None
