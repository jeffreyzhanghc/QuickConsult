from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from sqlalchemy.orm import Session as SQLAlchemySession
from typing import List
from datetime import datetime
from app.api.v1.deps import get_db, get_current_user, get_ws_current_user
from app.schemas.session import SessionResponse, MessageResponse, CreateSession
from app.schemas.user import User
from uuid import UUID
from app.models.session import SessionModel, MessageModel
from typing import Optional

router = APIRouter(tags=["sessions"])

# Session Creation
@router.post("", response_model=SessionResponse)
async def create_session(
    data: CreateSession,
    current_user: User = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db)
):
    """Create a new session with initial message"""
    try:
        # Create session
        session = SessionModel(
            user_id=current_user.id,
            expert_id=data.expert_id,
            status="active"
        )
        db.add(session)
        db.commit()
        
        # Add initial message
        message = MessageModel(
            session_id=session.id,
            sender_id=current_user.id,
            content=data.initial_message,
            created_at=datetime.utcnow()
        )
        db.add(message)
        db.commit()
        db.refresh(session)
        #breakpoint()
        return SessionResponse(
            id=UUID(str(session.id)),
            user_id=UUID(str(session.user_id)),
            expert_id=UUID(str(session.expert_id)),
            status=session.status,
            created_at=session.created_at,
            ended_at=session.ended_at,
            messages=[MessageResponse(
                id=UUID(str(message.id)),
                content=message.content,
                sender_id=UUID(str(message.sender_id)),
                created_at=message.created_at
            )]
        )
    except Exception as e:
        print(e)
        # Redirect to an error page on the frontend
        return

# Get User's Sessions
@router.get("/my/active", response_model=List[SessionResponse])
async def get_active_sessions(
    limit: Optional[int] = Query(None),  # Add this parameter
    current_user: User = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db)
):
    """Get all active sessions for current user"""
    query = db.query(SessionModel).filter(
        ((SessionModel.user_id == current_user.id) | (SessionModel.expert_id == current_user.id)) &
        (SessionModel.status == "active")
    ).order_by(SessionModel.created_at.desc())  # Order by most recent
    
    if limit:
        query = query.limit(limit)
        
    sessions = query.all()
    
    return [SessionResponse(
        id=UUID(str(session.id)),
        user_id=UUID(str(session.user_id)),
        expert_id=UUID(str(session.expert_id)),
        status=session.status,
        created_at=session.created_at,
        ended_at=session.ended_at,
        messages=[MessageResponse(
            id=UUID(str(msg.id)),
            content=msg.content,
            sender_id=UUID(str(msg.sender_id)),
            created_at=msg.created_at
        ) for msg in session.messages]
    ) for session in sessions]

@router.get("/my/completed", response_model=List[SessionResponse])
async def get_completed_sessions(
    current_user: User = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db)
):
    """Get all completed sessions for current user"""
    sessions = db.query(SessionModel).filter(
        ((SessionModel.user_id == current_user.id) | (SessionModel.expert_id == current_user.id)) &
        (SessionModel.status == "completed")
    ).all()
    
    return [SessionResponse(
        id=UUID(str(session.id)),
        user_id=UUID(str(session.user_id)),
        expert_id=UUID(str(session.expert_id)),
        status=session.status,
        created_at=session.created_at,
        ended_at=session.ended_at,
        messages=[MessageResponse(
            id=UUID(str(msg.id)),
            content=msg.content,
            sender_id=UUID(str(msg.sender_id)),
            created_at=msg.created_at
        ) for msg in session.messages]
    ) for session in sessions]

@router.post("/{session_id}/close")
async def close_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db)
):
    """Close an active session"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if str(session.user_id) != str(current_user.id) and str(session.expert_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    session.status = "completed"
    session.ended_at = datetime.utcnow()
    db.commit()
    
    return {"status": "success"}

# WebSocket Chat
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, session_id: UUID, websocket: WebSocket, client_id: UUID):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = {}
        self.active_connections[session_id][client_id] = websocket

    def disconnect(self, session_id: UUID, client_id: UUID):
        if session_id in self.active_connections:
            self.active_connections[session_id].pop(client_id, None)

    async def broadcast_message(self, session_id: UUID, message: dict):
        if session_id in self.active_connections:
            for ws in self.active_connections[session_id].values():
                await ws.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/{session_id}")
async def chat_websocket(
    websocket: WebSocket,
    session_id: UUID,
    db: SQLAlchemySession = Depends(get_db),
    current_user: User = Depends(get_ws_current_user)
):
    # Verify session access
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session or (str(session.user_id) != str(current_user.id) and 
                      str(session.expert_id) != str(current_user.id)):
        await websocket.close(code=4003)
        return

    await manager.connect(session_id, websocket, current_user.id)
    try:
        while True:
            data = await websocket.receive_json()
            
            # Save message to database
            message = MessageModel(
                session_id=session_id,
                sender_id=current_user.id,
                content=data["content"]
            )
            db.add(message)
            db.commit()
            db.refresh(message)

            # Broadcast to all session participants
            await manager.broadcast_message(
                session_id,
                {
                    "id": str(message.id),
                    "content": message.content,
                    "sender_id": str(message.sender_id),
                    "created_at": message.created_at.isoformat()
                }
            )
            
    except WebSocketDisconnect:
        manager.disconnect(session_id, current_user.id)

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: SQLAlchemySession = Depends(get_db)
):
    """Get a specific session by ID"""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if user has access to this session
    if str(session.user_id) != str(current_user.id) and str(session.expert_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
    
    return SessionResponse(
        id=UUID(str(session.id)),
        user_id=UUID(str(session.user_id)),
        expert_id=UUID(str(session.expert_id)),
        status=session.status,
        created_at=session.created_at,
        ended_at=session.ended_at,
        messages=[MessageResponse(
            id=UUID(str(msg.id)),
            content=msg.content,
            sender_id=UUID(str(msg.sender_id)),
            created_at=msg.created_at
        ) for msg in session.messages]
    )