from datetime import datetime
from ..extensions import db


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#3B82F6')  # Hex color code
    icon = db.Column(db.String(50))  # Font Awesome icon class

    # Category properties
    is_default = db.Column(db.Boolean, default=False)
    position = db.Column(db.Integer, default=0)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tasks = db.relationship('Task', backref='category', lazy='dynamic')

    def get_task_count(self):
        """Get number of tasks in this category"""
        return self.tasks.count()

    def get_completed_task_count(self):
        """Get number of completed tasks in this category"""
        return self.tasks.filter_by(status='completed').count()

    def get_completion_rate(self):
        """Get completion rate for this category"""
        total = self.get_task_count()
        completed = self.get_completed_task_count()
        return (completed / total * 100) if total > 0 else 0

    def to_dict(self, include_stats=False):
        """Convert category to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'is_default': self.is_default,
            'position': self.position,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'user_id': self.user_id
        }

        if include_stats:
            data.update({
                'task_count': self.get_task_count(),
                'completed_tasks': self.get_completed_task_count(),
                'completion_rate': self.get_completion_rate()
            })

        return data

    def __repr__(self):
        return f'<Category {self.name}>'
