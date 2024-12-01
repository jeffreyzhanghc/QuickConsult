import httpx
from typing import Dict
from app.core.config import Settings

class BackgroundCheckService:
    def __init__(self, settings: Settings):
        self.api_key = settings.BACKGROUND_CHECK_API_KEY
        self.base_url = settings.BACKGROUND_CHECK_API_URL
    
    async def initiate_check(self, expert_data: Dict) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/checks",
                json=expert_data,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code != 200:
                raise Exception("Background check initiation failed")
            
            return response.json()
    
    async def get_check_status(self, check_id: str) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/checks/{check_id}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code != 200:
                raise Exception("Failed to get background check status")
            
            return response.json()