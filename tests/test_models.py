from datetime import datetime, timedelta, timezone

from app.models import PasswordResetToken, Project, User


class TestUserModel:
    def test_password_is_hashed_not_stored_in_plaintext(self):
        user = User(name="Alice", email="alice@example.com")
        user.set_password("correct-horse-battery")
        assert user.password_hash != "correct-horse-battery"

    def test_check_password_accepts_correct_and_rejects_wrong(self):
        user = User(name="Alice", email="alice@example.com")
        user.set_password("correct-horse-battery")
        assert user.check_password("correct-horse-battery") is True
        assert user.check_password("wrong-password") is False

    def test_to_dict_excludes_password_hash(self, make_user):
        user = make_user()
        data = user.to_dict()
        assert "password_hash" not in data
        assert data["email"] == user.email


class TestProjectModel:
    def test_progress_percent_with_no_tasks_is_zero(self, db, make_user):
        user = make_user()
        project = Project(user_id=user.id, name="Launch")
        db.session.add(project)
        db.session.commit()

        assert project.task_count == 0
        assert project.progress_percent == 0

    def test_progress_percent_reflects_completed_tasks(self, db, make_user, make_task):
        user = make_user()
        project = Project(user_id=user.id, name="Launch")
        db.session.add(project)
        db.session.commit()

        make_task(user, title="Task 1", project_id=project.id, is_completed=True)
        make_task(user, title="Task 2", project_id=project.id, is_completed=False)

        assert project.task_count == 2
        assert project.completed_count == 1
        assert project.progress_percent == 50


class TestPasswordResetToken:
    def test_is_valid_for_unused_unexpired_token(self, make_user):
        user = make_user()
        token = PasswordResetToken(
            user_id=user.id,
            token_hash="hash",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        )
        assert token.is_valid() is True

    def test_is_invalid_once_used(self, make_user):
        user = make_user()
        token = PasswordResetToken(
            user_id=user.id,
            token_hash="hash",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            used=True,
        )
        assert token.is_valid() is False

    def test_is_invalid_once_expired(self, make_user):
        user = make_user()
        token = PasswordResetToken(
            user_id=user.id,
            token_hash="hash",
            expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
        )
        assert token.is_valid() is False
