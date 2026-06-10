from dataclasses import dataclass


@dataclass(frozen=True)
class MLflowConnection:
    url: str
    user: str
    password: str

    @property
    def auth(self) -> tuple[str, str]:
        return (self.user, self.password)
