# test_data.py
import asyncio
import uuid
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import SecurityManager
from app.core.config import Settings
from app.models import User, ExpertProfile, Question, ExpertResponse, Notification

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

async def cleanup_existing_data(db: Session):
    """Clean up existing test data"""
    # Delete in correct order to handle foreign key constraints
    db.query(ExpertResponse).delete()
    db.query(Question).delete()
    db.query(Notification).delete()
    db.query(ExpertProfile).delete()
    db.query(User).filter(User.email.in_([
        'client1@example.com',
        'client2@example.com',
        'expert1@example.com',
        'expert2@example.com',
        'expert3@example.com'
    ])).delete()
    db.commit()

async def create_test_data():
    settings = Settings()
    security = SecurityManager(settings)
    db = get_db()
    
    try:
        # Clean up existing test data first
        await cleanup_existing_data(db)

        # Create test clients
        clients = [
            {
                "email": "client1@example.com",
                "password": "client123",
                "full_name": "Test Client 1",
                "role": "client"
            },
            {
                "email": "client2@example.com",
                "password": "client123",
                "full_name": "Test Client 2",
                "role": "client"
            }
        ]

        # Create test experts with LinkedIn IDs
        experts = [
            {
                "email": "expert1@example.com",
                "password": "expert123",
                "full_name": "AI Expert",
                "role": "expert",
                "linkedin_id": "li_ai_expert_123",
                "expertise": ["Artificial Intelligence", "Machine Learning", "Deep Learning"],
                "bio": "10 years of experience in AI",
                "hourly_rate": 150.0
            },
            {
                "email": "expert2@example.com",
                "password": "expert123",
                "full_name": "Web Expert",
                "role": "expert",
                "linkedin_id": "li_web_expert_456",
                "expertise": ["Web Development", "Python", "JavaScript"],
                "bio": "Full stack developer with 8 years experience",
                "hourly_rate": 120.0
            },
            {
                "email": "expert3@example.com",
                "password": "expert123",
                "full_name": "Cloud Expert",
                "role": "expert",
                "linkedin_id": "li_cloud_expert_789",
                "expertise": ["AWS", "Azure", "Cloud Architecture"],
                "bio": "Cloud solutions architect",
                "hourly_rate": 140.0
            }
        ]

        # Create clients
        client_users = []
        for client_data in clients:
            client = User(
                id=uuid.uuid4(),
                email=client_data["email"],
                hashed_password=security.get_password_hash(client_data["password"]),
                full_name=client_data["full_name"],
                role=client_data["role"],
                is_active=True
            )
            db.add(client)
            client_users.append(client)

        # Create experts
        expert_users = []
        for expert_data in experts:
            expert_user = User(
                id=uuid.uuid4(),
                email=expert_data["email"],
                hashed_password=security.get_password_hash(expert_data["password"]),
                full_name=expert_data["full_name"],
                role=expert_data["role"],
                is_active=True
            )
            db.add(expert_user)
            expert_users.append(expert_user)

            expert_profile = ExpertProfile(
                id=uuid.uuid4(),
                user_id=expert_user.id,
                linkedin_id=expert_data["linkedin_id"],  # Added linkedin_id
                expertise=expert_data["expertise"],
                bio=expert_data["bio"],
                verification_status="verified",
                background_check_status="passed",
                hourly_rate=expert_data["hourly_rate"],
                rating=4.5,
                total_questions=0
            )
            db.add(expert_profile)

        # First commit for users and expert profiles
        db.commit()

        # Create test questions
        test_questions = [
            {
                "title": "Need help with AI implementation",
                "test_content": "How would you approach implementing a recommendation system?",
                "main_content": "We need a detailed plan for implementing a product recommendation system for our e-commerce platform.",
                "required_expertise": ["Artificial Intelligence", "Machine Learning"],
                "budget_range": {"min": 1000, "max": 5000}
            },
            {
                "title": "Cloud migration project",
                "test_content": "What's your experience with AWS migration?",
                "main_content": "Looking for help to migrate our on-premise application to AWS.",
                "required_expertise": ["AWS", "Cloud Architecture"],
                "budget_range": {"min": 5000, "max": 15000}
            }
        ]

        # Create questions
        for idx, question_data in enumerate(test_questions):
            question = Question(
                id=uuid.uuid4(),
                client_id=client_users[idx % len(client_users)].id,
                title=question_data["title"],
                test_content=question_data["test_content"],
                main_content_encrypted=question_data["main_content"],
                encryption_key_encrypted="dummy_key",
                required_expertise=question_data["required_expertise"],
                budget_range=question_data["budget_range"],
                status="pending"
            )
            db.add(question)

        # Final commit
        db.commit()

        print("\n=== Test Data Created Successfully! ===")
        print("\nTest Accounts:")
        print("\nClients:")
        for client in clients:
            print(f"Email: {client['email']}")
            print(f"Password: {client['password']}")
            print("---")
        
        print("\nExperts:")
        for expert in experts:
            print(f"Email: {expert['email']}")
            print(f"Password: {expert['password']}")
            print(f"LinkedIn ID: {expert['linkedin_id']}")
            print(f"Expertise: {', '.join(expert['expertise'])}")
            print("---")

    except Exception as e:
        print(f"Error creating test data: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(create_test_data())