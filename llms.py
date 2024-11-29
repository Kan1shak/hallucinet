import json
import google.generativeai as genai
from anthropic import Anthropic
from openai import OpenAI

def schema_to_json(model):
    dummy_dict = {}
    for field_name, field_type in model.__annotations__.items():
        if hasattr(field_type, '__fields__'):
            dummy_dict[field_name] = schema_to_json(field_type)
        elif hasattr(field_type, "__origin__") and field_type.__origin__ == list:
            inner_type = field_type.__args__[0]
            if hasattr(inner_type, '__fields__'):
                dummy_dict[field_name] = [schema_to_json(inner_type)]
            else:
                dummy_dict[field_name] = []
        elif field_type == str:
            dummy_dict[field_name] = ""
        elif field_type == int:
            dummy_dict[field_name] = 0
        elif field_type == float:
            dummy_dict[field_name] = 0.0
        elif field_type == bool:
            dummy_dict[field_name] = False
        elif field_type == dict:
            dummy_dict[field_name] = {}
        else:
            dummy_dict[field_name] = None
    return dummy_dict

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
            return json.loads(self.gemini.generate_content(prompt,generation_config=genai.GenerationConfig(
                response_mime_type="application/json", response_schema=schema
                )
            ).text)
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
            prompt = prompt + f"""\n\nFollow the following JSON schema to format your response:\n{schema_to_json(schema)}\n"""
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
            prompt = prompt + f"""\n\nFollow the following JSON schema to format your response:\n{schema_to_json(schema)}\n"""
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
        
class CreativeWriter:
    def __init__(self, meta_prompt, llm_provider_type, **llm_provider_kwargs):
        self.meta_prompt = meta_prompt
        self.llm = LLMWrapper(llm_provider_type, **llm_provider_kwargs, system_instruction=meta_prompt)

    def creative_loop(self, context):
        # for now lets just use the original prompt
        current_idea = self.llm.generate_plain_text(context)
        return current_idea

class JSONWriter:
    def __init__(self, json_instructions, schema,llm_provider_type, **llm_provider_kwargs):
        self.json_instructions = json_instructions
        self.llm = LLMWrapper(llm_provider_type, **llm_provider_kwargs, system_instruction=json_instructions)
        self.schema = schema

    def convertToJSON(self, text_to_extract_from):
        # for now lets just use the original prompt
        prompt = f"""{self.json_instructions}\n\n{text_to_extract_from}"""
        current_idea = self.llm.generate_structured(prompt,self.schema)
        return current_idea
        

