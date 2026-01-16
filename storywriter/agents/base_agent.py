from abc import ABC, abstractmethod
import json

def extract_json(text):
    """Busca y parsea JSON dentro de un texto, manejando código blocks."""
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != -1:
            # Quitamos envoltorios de markdown ```json ... ``` si existen
            possible_json = text[start:end]
            return json.loads(possible_json)
        return json.loads(text)
    except json.JSONDecodeError:
        return None
    
def extract_json_list(text):
    """Busca y parsea una lista JSON dentro de un texto."""
    try:
        start = text.find('[')
        end = text.rfind(']') + 1
        if start != -1 and end != -1:
            possible_json = text[start:end]
            return json.loads(possible_json)
        return json.loads(text)
    except json.JSONDecodeError:
        return None

class BaseAgent(ABC):
    """
    Clase base que se encarga de almacenar el cliente LLM.
    Todos los agentes heredan de esta clase y usan self.llm.
    """

    def __init__(self, llm_client, name: str = "", prompt_template: str = ""):
        self.llm = llm_client
        self.name = name
        self.prompt_template = prompt_template

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    def call_llm(self, prompt: str, **gen_kwargs):
        return self.llm.generate(prompt, **gen_kwargs)
