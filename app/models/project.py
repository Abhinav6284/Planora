from datetime import datetime
from ..extensions import db

# Association Table for the many-to-many relationship between Project and Task
project_task_association = db.Table(
    'project_task_association',
    db.Column('project_id', db.Integer, db.ForeignKey(
        'projects.id'), primary_key=True),
    db.Column('task_id', db.Integer, db.ForeignKey(
        'tasks.id'), primary_key=True)
)


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)

    # active, completed, archived
    status = db.Column(db.String(50), default='active')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # --- PORTFOLIO FIELDS ---
    github_url = db.Column(db.String(512))
    # This is where the AI-generated README will be stored
    portfolio_readme = db.Column(db.Text)
    is_in_portfolio = db.Column(db.Boolean, default=False)

    # --- RELATIONSHIPS ---
    # A project is a collection of many tasks
    tasks = db.relationship(
        'Task', secondary=project_task_association, backref='projects', lazy='dynamic')

    def __repr__(self):
        return f'<Project {self.name}>'
