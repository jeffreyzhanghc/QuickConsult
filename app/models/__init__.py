from app.models.base_models import Base
from app.models.user import User
from app.models.notification import Notification
from app.models.expert import ExpertProfile
from app.models.question import Question

# This ensures all models are registered
__all__ = ['Base', 'User', 'Notification', 'ExpertProfile', 'Question']