from __future__ import annotations

from typing import Dict

from pydantic import BaseModel


class FreezeParameter(BaseModel):
    parameter: str
