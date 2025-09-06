from datetime import datetime
from ..extensions import db


class FocusSession(db.Model):
    __tablename__ = 'focus_sessions'

    id = db.Column(db.Integer, primary_key=True)

    # Session details
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    session_type = db.Column(db.String(20), default='pomodoro')  # pomodoro, deep_work, break

    # Session tracking
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    was_completed = db.Column(db.Boolean, default=True)

    # Optional notes
    notes = db.Column(db.Text)
    productivity_score = db.Column(db.Integer)  # 1-10 self-rating

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))

    def to_dict(self):
        """Convert focus session to dictionary"""
        return {
            'id': self.id,
            'duration': self.duration,
            'session_type': self.session_type,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'was_completed': self.was_completed,
            'notes': self.notes,
            'productivity_score': self.productivity_score,
            'user_id': self.user_id,
            'task_id': self.task_id
        }

    def __repr__(self):
        return f'<FocusSession {self.duration}min>'
