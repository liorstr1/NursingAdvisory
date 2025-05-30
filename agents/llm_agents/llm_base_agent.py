import json
import os
from openai import OpenAI
from google import genai
from anthropic import Anthropic
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from entities import PROJECT_NAME, DEFAULT_CLAUDE_MODEL, SECRET_SERVICE_NAME
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
        self.event_description = ""
        self.system_prompt = ""
        self.user_prompt = ""
        self.output_classes = UserRequest
        self.available_actions = []
        self.available_handlers = []
        self.system_message = ""
        self.secret_manager = SecretManagerService(SECRET_SERVICE_NAME)

        self.anthropic_client = Anthropic(
            api_key=self._get_anthropic_api_key(),
        )
        self.gemini_client = genai.client.Client(
            api_key=self._get_gemini_api_key(),
        )
        self.openai_client = OpenAI(
            api_key=self._get_openai_api_key(),
        )

    def update_agent_info(self, agent_info):
        self.agent_name = agent_info.get("agent_name", "")
        self.agent_charcter = agent_info.get("agent_charcter", "")
        self.event_description = agent_info.get("event_description", "")
        self.system_prompt = agent_info.get("system_prompt", "")
        self.user_prompt = agent_info.get("user_prompt", "")
        self.output_classes = agent_info.get("output_classes", UserRequest)
        self.available_actions = agent_info.get("available_actions", [])
        self.available_handlers = agent_info.get("available_handlers", [])
        self.system_message = agent_info.get("system_message", "")

    def update_parser(self, user_output: BaseModel):
        self.output_parser = PydanticOutputParser(pydantic_object=user_output)
        self.format_instructions = self.output_parser.get_format_instructions()

    def update_prompts(self, chat_history):
        self.system_prompt = self.get_system_prompt()
        self.user_prompt = self.get_user_prompt(chat_history)

    def get_system_prompt(self):
        return self.system_prompt.format(
            agent_name=self.agent_name,
            agent_character=self.agent_charcter,
            event_description=self.event_description,
            # available_actions=self.available_actions,
            # available_handlers=self.available_handlers,
            # system_message=self.system_message,
            output_format=self.format_instructions
        )

    def get_user_prompt(self, chat_history):
        return self.user_prompt.format(
            chat_history=chat_history
        )

    def generate_response_from_anthropic(
            self,
            max_tokens=1000,
            model=DEFAULT_CLAUDE_MODEL
    ):
        message = self.anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=self.system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": self.user_prompt
                },
            ]
        )
        try:
            parsed_response = self.output_parser.parse(message.content[0].text)
            return parsed_response.next_message
        except Exception as e:
            print(f"Error parsing response: {e}")
            return None

    def generate_response_from_openai(
            self,
            max_tokens=1000,
            model="gpt-4o"
    ):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt}
        ]
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )

            response_text = response.choices[0].message.content
            parsed_response = self.output_parser.parse(response_text)
            return parsed_response.next_message
        except Exception as e:
            print(f"Error generating OpenAI response: {e}")
            return None

    def generate_response_from_gemini(
            self,
            model="gemini-2.5-pro"
    ):
        full_prompt = f"{self.system_prompt}\n\nUser: {self.user_prompt}"
        try:
            response = self.gemini_client.models.generate_content(
                model=f"models/{model}",
                contents=[{
                    "parts": [{"text": full_prompt}]
                }],
            )

            response_text = response.candidates[0].content.parts[0].text
            parsed_response = self.output_parser.parse(response_text)
            return parsed_response.next_message
        except Exception as e:
            print(f"Error generating Gemini response: {e}")
            return None

    def _get_anthropic_api_key(self):
        try:
            secrets = json.loads(self.secret_manager.access_secret(PROJECT_NAME))
            anthropic_api_key = secrets["claude_key"]
        except Exception as e:
            print(f"Error accessing Anthropic API key from secret manager: {e}")
            anthropic_api_key = os.getenv("LOCAL_CLAUDE_KEY")
        return anthropic_api_key

    def _get_openai_api_key(self):
        try:
            secrets = json.loads(self.secret_manager.access_secret(PROJECT_NAME))
            openai_api_key = secrets["openai_key"]
        except Exception as e:
            print(f"Error accessing OpenAI API key from secret manager: {e}")
            openai_api_key = os.getenv("LOCAL_OPENAI_KEY")
        return openai_api_key

    def _get_gemini_api_key(self):
        try:
            secrets = json.loads(self.secret_manager.access_secret(PROJECT_NAME))
            gemini_api_key = secrets["gemini_key"]
        except Exception as e:
            print(f"Error accessing Gemini API key from secret manager: {e}")
            gemini_api_key = os.getenv("LOCAL_GEMINI_KEY")
        return gemini_api_key
