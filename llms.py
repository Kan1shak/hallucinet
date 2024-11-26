import google.generativeai as genai
from anthropic import Anthropic
from openai import OpenAI

from PIL import ImageFont

class LLMWrapper:
    def __init__(self, llm_provider_type, **llm_provider_kwargs):
        # create a client based on the provider type
        # gemini from google aistudio, (not sure about vertex for now)
        self.llm_provider_type = llm_provider_type
        if self.llm_provider_type == 'gemini':
            genai.configure(api_key=llm_provider_kwargs['api_key'])
            generation_config = {
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 40,
            }
            safety_settings = [
                {
                    "category": "HARM_CATEGORY_DANGEROUS",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ]

            self.gemini = genai.GenerativeModel(
                model_name=llm_provider_kwargs['model_name'],
                generation_config=generation_config,
                safety_settings=safety_settings,
                system_instruction=llm_provider_kwargs['system_instruction']
            )
        # openai
        elif llm_provider_type == 'openai':
            self.openai_client = OpenAI(llm_provider_kwargs['api_key'])
            self.openai_system_instruction = llm_provider_kwargs['system_instruction']
            self.openai_model_name = llm_provider_kwargs['model_name']
        # anthropic
        elif llm_provider_type == 'anthrpic':
            self.anthropic_client = Anthropic(llm_provider_kwargs['api_key'])
            self.anthropic_system_instruction = llm_provider_kwargs['system_instruction']
            self.anthropic_model_name = llm_provider_kwargs['model_name']
        # local openAI compatible api
        elif llm_provider_type == 'local':
            self.ollama_client = OpenAI(
                base_url=llm_provider_kwargs['base_url'],
                api_key="meow"
            )
            self.ollama_system_instruction = llm_provider_kwargs['system_instruction']
            self.ollama_model_name = llm_provider_kwargs['model_name']
        else:
            raise ValueError(f"Unknown LLM provider type {llm_provider_type}")

        def generate_plain_text(prompt):
            if self.llm_provider_type == 'gemini':
                return self.gemini.generate_content(prompt)
            elif self.llm_provider_type == 'openai':
                completion = self.openai_client.chat.completions.create(
                    model=self.openai_model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": self.openai_system_instruction
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                return completion.choices[0].message.content
            elif self.llm_provider_type == 'anthropic':
                message = self.anthropic_client.messages.create(
                    model=self.anthropic_model_name,
                    system=self.anthropic_system_instruction,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "content": prompt
                                }
                            ]
                        }
                    ]
                )
                return message.content[0].text
            elif self.llm_provider_type == 'local':
                completion = self.ollama_client.chat.completions.create(
                    model=self.ollama_model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": self.ollama_system_instruction
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                return completion.choices[0].message.content
            else:
                # should never reach here
                raise ValueError(f"Unknown LLM provider type {self.llm_provider_type}")    
        