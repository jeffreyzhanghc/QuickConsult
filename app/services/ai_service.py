# services/question_service.py
import openai, asyncio, backoff, os
from anthropic import Anthropic
from openai import OpenAI, AsyncOpenAI
from app.core.config import settings
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import List, Optional

class AIResponse(BaseModel):
    analysis_type: str
    reason: str
    suggested_questions: List[str]

class AIService():
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.message_history = []
        
        self.system_prompt = """
        We are building a platform that help user quickly find matching consult to their questions, you are an expert on determine the following:
        1. Look the question as a whole, do you think these questions need to be answered by expert from different companies?
        2. Do you think the question need to be more elaborate? Or needs rephrasing for clarity and completeness?
        
        If answer to 1 is yes, you need to break down question to MINIMAL NUMBER OF subquestions. You should ONLY breakdown question if you think it is better to have expert from different companies to answer this question. ONLY separate if you think it is very necessary.
        If answer to 2 is yes, you should rephrase and make the question more clear

        Return in this JSON format:
        {
            "analysis_type": "keep same|separate|rephrase",
            "reason": "Brief explanation of your decision",
            "suggested_questions": ["list of questions"] // only if breakdown or rephrase needed
        }
        
        When combining questions:
        - Maintain all original format if you does not change the problem
        """

    async def analyze_question(self, question):
        try:
            result, message_history = await self._get_response_from_llm(
                msg=question,
                imgs=None,  # Pass list of processed images
                client=self.client,
                model="gpt-4o-mini-2024-07-18"
            )
            
            # Validate response format
            if not isinstance(result, str):
                raise ValueError("Invalid response format from LLM")
                
            return result
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"LLM analysis failed: {str(e)}"
            )

    async def _get_response_from_llm(
        self,
        msg,
        imgs=None,  
        client=None,
        model=None,
        system_message=None,
        print_debug=False,
        msg_history=None,
        temperature=1,
    ):
        if not system_message:
            system_message = self.system_prompt

        if msg_history is None:
            msg_history = self.message_history
        
        if "claude" in model:
            message_content = []
            
            # Add text if present
            if msg:
                message_content.append({
                    "type": "text",
                    "text": msg
                })
            
            # Add images if present, properly encoded in base64
            if imgs:
                import base64
                for img_data in imgs:
                    base64_image = base64.b64encode(img_data).decode('utf-8')
                    message_content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image
                        }
                    })

            new_msg_history = msg_history + [
                {
                    "role": "user",
                    "content": message_content
                }
            ]
            
            response = await client.messages.create(
                model=model,
                max_tokens=3000,
                temperature=temperature,
                system=system_message,
                messages=new_msg_history,
                response_format=AIResponse
            )
            content = response.content[0].text
            new_msg_history = new_msg_history + [
                {
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": content,
                        }
                    ],
                }
            ]
        elif model in [
            "gpt-4o-2024-05-13",
            "gpt-4o-mini-2024-07-18",
            "gpt-4o-2024-08-06",
        ]:
            # For OpenAI models, combine images into base64 and create a single message
            import base64
            message_text = []
            if msg:
                message_text.append({"type":"text","text":msg})
            if imgs:
                for i, img_data in enumerate(imgs, 1):
                    #print(img_data)
                    base64_image = base64.b64encode(img_data).decode('utf-8')
                    #print(type(base64_image))
                    message_text.append({"type": "image_url",
                                            "image_url": {
                                                "url":  f"data:image/jpeg;base64,{base64_image}"
                                            },
                                         })
            #need to implemen history !!!
            new_msg_history = []
            response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {
                "role": "user",
                "content": message_text,
                },
            ],
            )
            content = response.choices[0].message.content
            new_msg_history = new_msg_history + [{"role": "assistant", "content": content}]
            self.message_history = new_msg_history
        else:
            raise ValueError(f"Model {model} not supported.")

        if print_debug:
            print()
            print("*" * 20 + " LLM START " + "*" * 20)
            for j, msg in enumerate(new_msg_history):
                print(f'{j}, {msg["role"]}: {msg["content"]}')
            print(content)
            print("*" * 21 + " LLM END " + "*" * 21)
            print()
        return content, new_msg_history
    


    @backoff.on_exception(backoff.expo, (openai.RateLimitError, openai.APITimeoutError))
    def _get_batch_responses_from_llm(
        self,
        msg,
        client,
        model,
        system_message = "",
        print_debug=False,
        msg_history=None,
        temperature=0.75,
        n_responses=1,
    ):
        if msg_history is None:
            msg_history = []

        if model in [
            "gpt-4o-2024-05-13",
            "gpt-4o-mini-2024-07-18",
            "gpt-4o-2024-08-06",
        ]:
            new_msg_history = msg_history + [{"role": "user", "content": msg}]
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    *new_msg_history,
                ],
                max_tokens=3000,
                n=n_responses,
                stop=None,
                seed=0,
            )
            content = [r.message.content for r in response.choices]
            new_msg_history = [
                new_msg_history + [{"role": "assistant", "content": c}] for c in content
            ]
        elif "claude" in model:
            content, new_msg_history = [], []
            for _ in range(n_responses):
                c, hist = self._get_response_from_llm(
                    msg,
                    client,
                    model,
                    system_message,
                    print_debug=False,
                    msg_history=None,
                    temperature=temperature,
                )
                content.append(c)
                new_msg_history.append(hist)
        else:
            raise ValueError(f"Model {model} not supported.")

        if print_debug:
            # Just print the first one.
            print()
            print("*" * 20 + " LLM START " + "*" * 20)
            for j, msg in enumerate(new_msg_history[0]):
                print(f'{j}, {msg["role"]}: {msg["content"]}')
            print(content)
            print("*" * 21 + " LLM END " + "*" * 21)
            print()

        return content, new_msg_history