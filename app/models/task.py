import enum
from datetime import datetime, timezone

from app.extensions import db
from app.models.tag import task_tags


class TaskStatus(enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class TaskPriority(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    status = db.Column(db.Enum(TaskStatus), nullable=False, default=TaskStatus.TODO, index=True)
    priority = db.Column(db.Enum(TaskPriority), nullable=False, default=TaskPriority.MEDIUM, index=True)

    start_date = db.Column(db.Date, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True, index=True)

    is_completed = db.Column(db.Boolean, nullable=False, default=False, index=True)
    completed_at = db.Column(db.DateTime, nullable=True)

    position = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    tags = db.relationship("Tag", secondary=task_tags, backref=db.backref("tasks", lazy="dynamic"))

    @property
    def is_overdue(self):
        if not self.due_date or self.is_completed:
            return False
        due = self.due_date
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)
        return due < datetime.now(timezone.utc)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "project_id": self.project_id,
            "project_name": self.project.name if self.project else None,
            "project_color": self.project.color if self.project else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "is_completed": self.is_completed,
            "is_overdue": self.is_overdue,
            "position": self.position,
            "tags": [t.to_dict() for t in self.tags],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Task {self.title}>"
