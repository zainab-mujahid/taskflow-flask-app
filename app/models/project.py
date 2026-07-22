from datetime import datetime, timezone

from app.extensions import db

DEFAULT_COLORS = [
    "#6366f1", "#22c55e", "#f59e0b", "#ef4444",
    "#06b6d4", "#ec4899", "#8b5cf6", "#14b8a6",
]


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    color = db.Column(db.String(7), nullable=False, default=DEFAULT_COLORS[0])
    icon = db.Column(db.String(32), nullable=False, default="folder")
    is_archived = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # No delete-orphan cascade here: deleting a project should orphan its tasks
    # (project_id -> NULL), not delete them, matching the FK's ondelete="SET NULL".
    tasks = db.relationship("Task", backref="project", lazy="dynamic")

    @property
    def task_count(self):
        return self.tasks.count()

    @property
    def completed_count(self):
        return self.tasks.filter_by(is_completed=True).count()

    @property
    def progress_percent(self):
        total = self.task_count
        if total == 0:
            return 0
        return round((self.completed_count / total) * 100)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "icon": self.icon,
            "is_archived": self.is_archived,
            "task_count": self.task_count,
            "completed_count": self.completed_count,
            "progress_percent": self.progress_percent,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Project {self.name}>"
