from typing import Optional

from pydantic import BaseModel


class ModuleCreate(BaseModel):
    name: str
    category: str = "praca"


class ModuleUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None


class TaskCreate(BaseModel):
    name: str
    module_id: int
    status: str = "oczekujace"
    estimated_time: int = 0
    description: str = ""
    due_date: str = ""
    priority: str = ""


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    name: Optional[str] = None
    module_id: Optional[int] = None
    priority: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    estimated_time: Optional[int] = None


class NotePayload(BaseModel):
    content: str = ""


class MonthlyTaskCreate(BaseModel):
    name: str
    due_day: int = 0


class MonthlyTaskUpdate(BaseModel):
    name: str
    due_day: int = 0


class MonthlyTaskStatePayload(BaseModel):
    month_key: Optional[str] = None
    done: Optional[bool] = None
    note: Optional[str] = None


class DebtCreate(BaseModel):
    name: str
    place: str = ""
    kind: str = "debt"
    total_amount: float = 0.0
    monthly_amount: float = 0.0
    due_day: int = 0
    note: str = ""


class DebtUpdate(BaseModel):
    name: Optional[str] = None
    place: Optional[str] = None
    kind: Optional[str] = None
    total_amount: Optional[float] = None
    monthly_amount: Optional[float] = None
    due_day: Optional[int] = None
    note: Optional[str] = None


class DebtStatePayload(BaseModel):
    month_key: Optional[str] = None
    done: Optional[bool] = None
