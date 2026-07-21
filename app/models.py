from app.database import db
from datetime import datetime, timezone

class Item(db.Model):
    """
    - The schema of postgresql with SQLAlchemy ORM.
    - SQLAlchemy's db.Model provides a magic __init__ that automatically assigns any keyword arguments (name=...) to the matching column names you defined.
    """
    __tablename__ = "items"

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id":          self.id,
            "name":        self.name,
            "description": self.description,
            "created_at":  self.created_at.isoformat(),
        }