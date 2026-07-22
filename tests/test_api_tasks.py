from app.extensions import db
from app.models import Task, TaskStatus


class TestTaskStatusEndpoint:
    def test_requires_authentication(self, client, make_user, make_task):
        user = make_user()
        task = make_task(user)

        response = client.patch(f"/api/tasks/{task.id}/status", json={"status": "IN_PROGRESS"})

        assert response.status_code == 401

    def test_updates_status_for_owned_task(self, auth_client, make_task):
        client, user = auth_client
        task = make_task(user)

        response = client.patch(f"/api/tasks/{task.id}/status", json={"status": "IN_PROGRESS"})

        assert response.status_code == 200
        body = response.get_json()
        assert body["task"]["status"] == "IN_PROGRESS"
        assert body["task"]["is_completed"] is False

    def test_completed_status_marks_task_completed(self, auth_client, make_task):
        client, user = auth_client
        task = make_task(user)

        response = client.patch(f"/api/tasks/{task.id}/status", json={"status": "COMPLETED"})

        assert response.status_code == 200
        body = response.get_json()
        assert body["task"]["is_completed"] is True

    def test_rejects_invalid_status(self, auth_client, make_task):
        client, user = auth_client
        task = make_task(user)

        response = client.patch(f"/api/tasks/{task.id}/status", json={"status": "BOGUS"})

        assert response.status_code == 400

    def test_returns_404_for_task_owned_by_another_user(self, auth_client, make_user, make_task):
        client, _user = auth_client
        other_user = make_user(email="other@example.com")
        other_task = make_task(other_user)

        response = client.patch(
            f"/api/tasks/{other_task.id}/status", json={"status": "IN_PROGRESS"}
        )

        assert response.status_code == 404


class TestTaskCompleteEndpoint:
    def test_toggle_complete_sets_status_and_flag(self, auth_client, make_task):
        client, user = auth_client
        task = make_task(user)

        response = client.patch(f"/api/tasks/{task.id}/complete", json={"is_completed": True})

        assert response.status_code == 200
        body = response.get_json()
        assert body["task"]["is_completed"] is True
        assert body["task"]["status"] == "COMPLETED"

    def test_toggle_incomplete_clears_completed_at(self, auth_client, make_task):
        client, user = auth_client
        task = make_task(user, is_completed=True, status=TaskStatus.COMPLETED)

        response = client.patch(f"/api/tasks/{task.id}/complete", json={"is_completed": False})

        assert response.status_code == 200
        body = response.get_json()
        assert body["task"]["is_completed"] is False
        assert body["task"]["status"] == "TODO"


class TestTaskReorderEndpoint:
    def test_reorder_updates_position_and_status(self, auth_client, make_task):
        client, user = auth_client
        task_a = make_task(user, title="A")
        task_b = make_task(user, title="B")

        response = client.post(
            "/api/tasks/reorder",
            json={"status": "IN_PROGRESS", "ordered_ids": [task_b.id, task_a.id]},
        )

        assert response.status_code == 200
        assert response.get_json() == {"ok": True}

        refreshed_a = db.session.get(Task, task_a.id)
        refreshed_b = db.session.get(Task, task_b.id)
        assert refreshed_b.position == 0
        assert refreshed_a.position == 1
        assert refreshed_a.status == TaskStatus.IN_PROGRESS
        assert refreshed_b.status == TaskStatus.IN_PROGRESS

    def test_reorder_rejects_invalid_status(self, auth_client, make_task):
        client, user = auth_client
        task = make_task(user)

        response = client.post(
            "/api/tasks/reorder", json={"status": "BOGUS", "ordered_ids": [task.id]}
        )

        assert response.status_code == 400
