from typing import Optional

from pydantic import BaseModel, Field


class RegisterPayload(BaseModel):
    username: str = Field(..., min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(..., min_length=8, max_length=72)
    invite_code: str = Field(..., min_length=1, max_length=128)


class RegisterResponse(BaseModel):
    id: int
    username: str


class ModuleCreate(BaseModel):
    name: str
    category: str = "praca"


class ModuleUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None


class TaskSubtaskPayload(BaseModel):
    id: Optional[int] = None
    title: str = ""
    done: bool = False
    estimated_time: int = 0
    points_weight: float = 0.0
    done_at: str = ""
    source_task_id: Optional[int] = None
    source_module_id: Optional[int] = None
    source_due_date: str = ""
    source_due_time: str = ""


class TaskCreate(BaseModel):
    name: str
    module_id: int
    status: str = "oczekujace"
    estimated_time: int = 0
    points_weight: float = 1.0
    description: str = ""
    due_date: str = ""
    due_time: str = ""
    priority: str = ""
    allow_time_overflow: bool = False
    subtasks: list[TaskSubtaskPayload] = []


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    name: Optional[str] = None
    module_id: Optional[int] = None
    priority: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    due_time: Optional[str] = None
    estimated_time: Optional[int] = None
    points_weight: Optional[float] = None
    allow_time_overflow: Optional[bool] = None
    subtasks: Optional[list[TaskSubtaskPayload]] = None


class TaskSharePayload(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)


class TaskMergePayload(BaseModel):
    source_task_id: int
    target_task_id: int
    name: str = ""
    allow_time_overflow: bool = False


class NotePayload(BaseModel):
    content: str = ""


class MonthlyTaskCreate(BaseModel):
    name: str
    due_day: int = 0
    repeat_type: str = "monthly"
    repeat_weekday: int = 1


class MonthlyTaskUpdate(BaseModel):
    name: str
    due_day: int = 0
    repeat_type: str = "monthly"
    repeat_weekday: int = 1


class MonthlyTaskStatePayload(BaseModel):
    month_key: Optional[str] = None
    done: Optional[bool] = None
    note: Optional[str] = None


class MedicationCreate(BaseModel):
    name: str
    schedule_type: str = "daily"
    reminder_time: str = "08:00"


class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    schedule_type: Optional[str] = None
    reminder_time: Optional[str] = None
    active: Optional[bool] = None


class MedicationStatePayload(BaseModel):
    date_key: Optional[str] = None
    done: Optional[bool] = None


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
