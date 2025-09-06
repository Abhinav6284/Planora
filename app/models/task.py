from datetime import datetime
from ..extensions import db
from sqlalchemy import event


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    # Task properties
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='todo')  # todo, in_progress, completed, cancelled

    # Dates and times
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # Estimated and actual time
    estimated_duration = db.Column(db.Integer)  # in minutes
    actual_duration = db.Column(db.Integer)  # in minutes

    # Task organization
    position = db.Column(db.Integer, default=0)  # for drag-and-drop ordering
    tags = db.Column(db.Text)  # JSON string of tags

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    parent_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))  # for subtasks

    # Self-referential relationship for subtasks
    subtasks = db.relationship('Task', backref=db.backref('parent_task', remote_side=[id]))
    focus_sessions = db.relationship('FocusSession', backref='task', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return datetime.utcnow() > self.due_date
        return False

    @property
    def time_remaining(self):
        """Get time remaining until due date"""
        if self.due_date and not self.is_completed:
            delta = self.due_date - datetime.utcnow()
            return delta.total_seconds() / 3600  # hours
        return None

    @property
    def is_completed(self):
        """Check if task is completed"""
        return self.status == 'completed'

    def mark_completed(self):
        """Mark task as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()

    def mark_in_progress(self):
        """Mark task as in progress"""
        self.status = 'in_progress'

    def get_progress_percentage(self):
        """Get task progress based on subtasks"""
        if not self.subtasks:
            return 100 if self.is_completed else 0

        completed_subtasks = sum(1 for subtask in self.subtasks if subtask.is_completed)
        return (completed_subtasks / len(self.subtasks)) * 100

    def get_total_focus_time(self):
        """Get total focus time spent on this task"""
        return self.focus_sessions.with_entities(
            db.func.sum(FocusSession.duration)
        ).scalar() or 0

    def to_dict(self, include_subtasks=False):
        """Convert task to dictionary"""
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'estimated_duration': self.estimated_duration,
            'actual_duration': self.actual_duration,
            'position': self.position,
            'tags': self.tags,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'parent_task_id': self.parent_task_id,
            'is_overdue': self.is_overdue,
            'time_remaining': self.time_remaining,
            'progress_percentage': self.get_progress_percentage(),
            'total_focus_time': self.get_total_focus_time()
        }

        if include_subtasks:
            data['subtasks'] = [subtask.to_dict() for subtask in self.subtasks]

        return data

    def __repr__(self):
        return f'<Task {self.title}>'


# Auto-update updated_at timestamp
@event.listens_for(Task, 'before_update')
def task_updated_at(mapper, connection, target):
    target.updated_at = datetime.utcnow()
