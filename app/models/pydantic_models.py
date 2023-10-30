from pydantic import BaseModel
from typing import List, Optional

class Repository(BaseModel):
    name: str
    html_url: str
    description: Optional[str] = None
    language: Optional[str] = None

class UserRepos(BaseModel):
    username: str
    repos: List[Repository]