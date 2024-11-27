import json
import google.generativeai as genai
from anthropic import Anthropic
from openai import OpenAI
from pydantic import BaseModel
from typing_extensions import TypedDict

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
            model_name = "gemini-1.5-flash" if 'model_name' not in llm_provider_kwargs else llm_provider_kwargs['model_name']
            self.gemini = genai.GenerativeModel(
                model_name=model_name,
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
            self.local_client = OpenAI(
                base_url=llm_provider_kwargs['base_url'],
                api_key="meow"
            )
            self.local_system_instruction = llm_provider_kwargs['system_instruction']
            self.local_model_name = llm_provider_kwargs['model_name']
        else:
            raise ValueError(f"Unknown LLM provider type {llm_provider_type}")

    def generate_plain_text(self, prompt):
        if self.llm_provider_type == 'gemini':
            return self.gemini.generate_content(prompt).text
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
            completion = self.local_client.chat.completions.create(
                model=self.local_model_name,
                messages=[
                    {
                        "role": "system",
                        "content": self.local_system_instruction
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

    def generate_structured(self, prompt,schema):
        if self.llm_provider_type == 'gemini':
            # converting a pydantic model to a typed dict
            Model = TypedDict(
                schema.__name__ + "TypedDict",
                {name: field.annotation for name, field in schema.model_fields.items()}
            )
            # generate the content
            return self.gemini.generate_content(prompt,generation_config=genai.GenerationConfig(
                response_mime_type="application/json", response_schema=list[Model]
                )
            )

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
                ],
                response_format=schema
            )
            return completion.choices[0].message.content
        elif self.llm_provider_type == 'anthropic':
            # we have to do some work here
            prompt = prompt + f"""\n\nFollow the following JSON schema to format your response:\n{schema.model_json_schema()}\n"""
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
                    },
                    # prefill the response with the `{` character so we know it starts with a JSON object
                    {
                        "role": "assistant",
                        "content": "Here is the JSON requested:\n{"
                    }

                ]
            )
            unformatted = message.content[0].text
            output_json = json.loads("{" + unformatted[:unformatted.rfind("}") + 1])
            return output_json
        
        elif self.llm_provider_type == 'local':
            # same approach as anthropic
            prompt = prompt + f"""\n\nFollow the following JSON schema to format your response:\n{schema.model_json_schema()}\n"""
            completion = self.local_client.chat.completions.create(
                model=self.local_model_name,
                messages=[
                    {
                        "role": "system",
                        "content": self.local_system_instruction
                    },
                    {
                        "role": "user",
                        "content": prompt
                    },
                    {
                        "role": "assistant",
                        "content": "Here is the JSON requested:\n{"
                    }
                ],
            )
            unformatted = completion.choices[0].message.content
            output_json = json.loads("{" + unformatted[:unformatted.rfind("}") + 1])
            return output_json
        else:
            # should never reach here
            raise ValueError(f"Unknown LLM provider type {self.llm_provider_type}")