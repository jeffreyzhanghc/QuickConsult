from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.notification import Notification
import uuid
from datetime import datetime

class NotificationService:
    async def create_notification(
        self,
        db: Session,
        user_id: uuid.UUID,
        title: str,
        content: str,
        notification_type: str
    ) -> Notification:
        notification = Notification(
            id=uuid.uuid4(),
            user_id=user_id,
            title=title,
            content=content,
            type=notification_type
        )
        
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        
        # Trigger real-time notification if applicable
        await self._send_realtime_notification(notification)
        return notification
    
    async def get_user_notifications(
        self,
        db: Session,
        user_id: uuid.UUID,
        unread_only: bool = False
    ) -> List[Notification]:
        query = db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.is_read == False)
        return query.order_by(Notification.created_at.desc()).all()
    
    async def mark_as_read(
        self,
        db: Session,
        notification_id: uuid.UUID
    ) -> Optional[Notification]:
        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if notification:
            notification.is_read = True
            await db.commit()
            await db.refresh(notification)
        
        return notification
    
    async def _send_realtime_notification(self, notification: Notification):
        # Implement WebSocket notification here
        pass