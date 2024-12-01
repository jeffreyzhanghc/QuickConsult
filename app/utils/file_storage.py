import boto3
from botocore.exceptions import ClientError
from typing import Optional, BinaryIO
from app.core.config import Settings

class S3Storage:
    def __init__(self, settings: Settings):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket = settings.S3_BUCKET
    
    async def upload_file(
        self,
        file_obj: BinaryIO,
        file_name: str,
        content_type: Optional[str] = None
    ) -> str:
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            await self.s3_client.upload_fileobj(
                file_obj,
                self.bucket,
                file_name,
                ExtraArgs=extra_args
            )
            
            return f"https://{self.bucket}.s3.amazonaws.com/{file_name}"
        
        except ClientError as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    async def get_download_url(self, file_name: str, expires_in: int = 3600) -> str:
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': file_name},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            raise Exception(f"Failed to generate download URL: {str(e)}")