from typing import Any, Callable, Optional


class Depends():
    """
    Dependency registration class
    """
    def __init__(self, obj: Optional[Callable[..., Any]] = None) -> None:
        self.obj = obj
    
    def __repr__(self) -> str:
        return f"{self.obj.__module__}.{self.obj.__name__} dependency"