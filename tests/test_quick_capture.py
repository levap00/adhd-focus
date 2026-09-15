import os
import tempfile
from pathlib import Path

TMP = Path(tempfile.mkdtemp(prefix="focus-capture-"))
os.environ["FOCUS_APP_DB_PATH"] = str(TMP / "app.db")
os.environ["FOCUS_USERNAME"] = "admin"
os.environ["FOCUS_PASSWORD"] = "adminpass1"
os.environ["FOCUS_INVITE_CODES"] = "invite-one"
os.environ["FOCUS_SESSION_SECRET"] = "test-session-secret"

from fastapi.testclient import TestClient

from backend.app import app


def fresh_client() -> TestClient:
    return TestClient(app)


def login(client: TestClient):
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "adminpass1", "remember": "1"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    return response


def test_task_without_module_lands_in_inbox():
    client = fresh_client()
    login(client)

    created = client.post("/tasks", json={"name": "kupic filtr"})
    assert created.status_code == 200, created.text
    task_id = created.json()["id"]

    modules = client.get("/modules").json()
    inbox = next(item for item in modules if item["name"].strip().lower() == "do przypisania")

    tasks = client.get("/tasks").json()
    task = next(item for item in tasks if item["id"] == task_id)
    assert task["name"] == "kupic filtr"
    assert task["module_id"] == inbox["id"]
    assert task["status"] == "oczekujace"
    assert not task.get("due_date")


def test_subtask_defaults_time_and_points():
    client = fresh_client()
    login(client)

    created = client.post(
        "/tasks",
        json={
            "name": "zwroty",
            "subtasks": [{"title": "klawiatura"}, {"title": "filtr do wody"}],
        },
    )
    assert created.status_code == 200, created.text
    task_id = created.json()["id"]

    tasks = client.get("/tasks").json()
    task = next(item for item in tasks if item["id"] == task_id)
    assert len(task["subtasks"]) == 2
    assert task["subtasks"][0]["estimated_time"] == 15
    assert task["subtasks"][0]["points_weight"] == 1
    assert task["estimated_time"] == 30
    assert task["points_weight"] == 2


def test_subtask_reordering_preserves_completion_and_durations():
    client = fresh_client()
    login(client)
    created = client.post("/tasks", json={
        "name": "kolejnosc krokow",
        "subtasks": [
            {"title": "Powtorzona nazwa", "estimated_time": 135, "points_weight": 2},
            {"title": "Zrobione", "done": True, "done_at": "2026-01-01T12:00:00Z"},
            {"title": "Powtorzona nazwa", "estimated_time": 37, "points_weight": 3},
        ],
    })
    assert created.status_code == 200, created.text
    task_id = created.json()["id"]
    task = next(item for item in client.get("/tasks").json() if item["id"] == task_id)
    steps = task["subtasks"]
    reordered = [steps[2], steps[1], steps[0]]
    saved = client.put(f"/tasks/{task_id}", json={"subtasks": reordered})
    assert saved.status_code == 200, saved.text
    loaded = next(item for item in client.get("/tasks").json() if item["id"] == task_id)
    assert [item["estimated_time"] for item in loaded["subtasks"]] == [37, 15, 135]
    assert loaded["subtasks"][1]["done"]
    assert loaded["subtasks"][1]["done_at"] == steps[1]["done_at"]
    assert loaded["estimated_time"] == 187
