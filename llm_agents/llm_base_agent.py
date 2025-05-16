from langchain_core.output_parsers import PydanticOutputParser


class LLMBaseAgent:
    def __init__(self):
        self.output_parser = None
        self.agent_name = ""
        self.agent_charcter = ""
        self.agent_description = ""
        self.main_prompt = ""
        self.output_classes = ""
        self.available_actions = []
        self.available_handlers = []
        self.system_message = ""

    def update_parser(self):
        self.output_parser = PydanticOutputParser(pydantic_object=Entities)
        format_instructions = output_parser.get_format_instructions()
        h = 0

    async def generate_response_from_anthropic(self, max_tokens=1000, anthropic_model="claude-3-5-sonnet-latest"):
        system_prompt = self.get_system_prompt()
        user_prompt = self.get_user_prompt()
        print("Creating response using Anthropic for:", self.name)
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





