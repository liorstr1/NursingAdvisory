import json
import os

import OpenAI
from google import genai
from anthropic import Anthropic
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from entities import PROJECT_NAME, AgentType
from services.secret_manager_service import SecretManagerService
from dotenv import load_dotenv
load_dotenv()


class UserRequest(BaseModel):
    request: str


class LLMBaseAgent:
    def __init__(self):
        self.format_instructions = None
        self.output_parser = None
        self.agent_name = ""
        self.agent_charcter = ""
        self.agent_description = ""
        self.system_prompt = ""
        self.user_prompt = ""
        self.output_classes = UserRequest
        self.available_actions = []
        self.available_handlers = []
        self.system_message = ""
        self.secret_manager = SecretManagerService("Botit1")

        self.anthropic_client = Anthropic(
            api_key=self._get_anthropic_api_key(),
        )
        self.gemini_client = genai.client.Client(
            api_key=self._get_gemini_api_key(),
        )
        self.openai_client = OpenAI(
            api_key=self._get_openai_api_key(),
        )

    def update_parser(self):
        self.output_parser = PydanticOutputParser(pydantic_object=self.output_classes)
        self.format_instructions = self.output_parser.get_format_instructions()

    def get_system_prompt(self):
        return self.system_prompt.format(
            agent_name=self.agent_name,
            agent_character=self.agent_charcter,
            agent_description=self.agent_description,
            available_actions=self.available_actions,
            available_handlers=self.available_handlers,
            system_message=self.system_message,
            output_format=self.format_instructions
        )

    def get_user_prompt(self, chat_history):
        return self.user_prompt.format(
            chat_history=chat_history
        )

    async def generate_response_from_anthropic(
            self,
            chat_history=None,
            max_tokens=1000,
            anthropic_model="claude-3-5-sonnet-latest"
    ):
        if chat_history is None:
            chat_history = []
        system_prompt = self.get_system_prompt()
        user_prompt = self.get_user_prompt(chat_history)
        message = self.anthropic_client.messages.create(
            model=anthropic_model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt
                },
            ]
        )
        try:
            parsed_response = self.output_parser.parse(message.content[0].text)
            return parsed_response.response
        except Exception as e:
            print(f"Error parsing response: {e}")
            return None

    def _get_anthropic_api_key(self):
        anthropic_api_key = None
        try:
            secrets = json.loads(self.secret_manager.access_secret(PROJECT_NAME))
            anthropic_api_key = secrets["claude_key"]
        except Exception as e:
            print(f"Error accessing Anthropic API key from secret manager: {e}")
            anthropic_api_key = os.getenv("LOCAL_CLAUDE_KEY")
        finally:
            return anthropic_api_key

    def _get_openai_api_key(self):
        openai_api_key = None
        try:
            secrets = json.loads(self.secret_manager.access_secret(PROJECT_NAME))
            openai_api_key = secrets["openai_key"]
        except Exception as e:
            print(f"Error accessing Anthropic API key from secret manager: {e}")
            openai_api_key = os.getenv("LOCAL_OPENAI_KEY")
        finally:
            return openai_api_key

    def _get_gemini_api_key(self):
        gemini_api_key = None
        try:
            secrets = json.loads(self.secret_manager.access_secret(PROJECT_NAME))
            gemini_api_key = secrets["gemini_key"]
        except Exception as e:
            print(f"Error accessing Anthropic API key from secret manager: {e}")
            gemini_api_key = os.getenv("LOCAL_GEMINI_KEY")
        finally:
            return gemini_api_key







