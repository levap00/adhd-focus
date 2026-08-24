import json
import os
import tempfile
from pathlib import Path

TMP = Path(tempfile.mkdtemp(prefix="focus-canvas-"))
os.environ["FOCUS_APP_DB_PATH"] = str(TMP / "app.db")
os.environ["FOCUS_USERNAME"] = "admin"
os.environ["FOCUS_PASSWORD"] = "adminpass1"
os.environ["FOCUS_INVITE_CODES"] = "invite-one"
os.environ["FOCUS_SESSION_SECRET"] = "test-session-secret"

from fastapi.testclient import TestClient

from backend.app import app


def login(client: TestClient):
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "adminpass1", "remember": "1"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    return response


def test_process_map_stores_boards_and_task_nodes():
    client = TestClient(app)
    login(client)

    created = client.post("/tasks", json={"name": "przeniesc GPS klientow"})
    assert created.status_code == 200, created.text
    task_id = created.json()["id"]

    payload = {
        "version": 3,
        "activeBoardId": "board-migracja",
        "boards": [
            {
                "id": "board-migracja",
                "name": "Migracja",
                "columns": [{"id": "col-a", "title": "Jest", "x": 40, "width": 300, "color": "sky"}],
                "nodes": [
                    {
                        "id": "node-task",
                        "shape": "task",
                        "taskId": task_id,
                        "columnId": "col-a",
                        "text": "przeniesc GPS klientow",
                        "x": 56,
                        "y": 120,
                        "width": 260,
                        "height": 130,
                        "color": "slate",
                    }
                ],
                "links": [],
            }
        ],
    }
    saved = client.put("/notes/process-map", json={"content": json.dumps(payload)})
    assert saved.status_code == 200, saved.text

    loaded = client.get("/notes/process-map")
    assert loaded.status_code == 200
    stored = json.loads(loaded.json()["content"])
    assert stored["activeBoardId"] == "board-migracja"
    assert stored["boards"][0]["name"] == "Migracja"
    assert stored["boards"][0]["nodes"][0]["taskId"] == task_id
    assert stored["boards"][0]["columns"][0]["title"] == "Jest"
