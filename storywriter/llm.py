# llm.py
#from llama_cpp import Llama
#from typing import Dict, Any

#class LLMClient:
 #   def __init__(self, model_path: str, **kwargs):
  #      # kwargs pueden incluir n_ctx, n_threads, etc.
   #     self.model = Llama(model_path=model_path, verbose=False, **kwargs)

    #def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.7, stop: list = None) -> str:
     #   out = self.model(prompt, max_tokens=max_tokens, temperature=temperature)
      #  text = out['choices'][0].get('text', '')
       # return text.strip()

# Ejemplo de uso:
# client = LLMClient(model_path="./modelo_local/GGUF/modelo.gguf", n_ctx=512)
# respuesta = client.generate("Escribe un evento principal: ...")

# llm.py
from llama_cpp import Llama
import json
import re

class LLMClient:
    def __init__(self, model_path: str, n_ctx: int = 4096, **kwargs):
        # verbose=False para que no moleste en la consola
        self.model = Llama(
            model_path=model_path, 
            n_gpu_layers=999,
            n_ctx=n_ctx, 
            verbose=False, 
            **kwargs
        )

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.7, stop: list = None) -> str:
        """
        Genera respuesta usando el formato de Chat nativo del modelo.
        """
        # Estructuramos el mensaje como una conversación
        messages = [
            {"role": "user", "content": prompt}
        ]

        # create_chat_completion se encarga de poner los [INST] y tokens especiales automáticamente
        output = self.model.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop
        )

        # Extraemos el contenido limpio
        return output['choices'][0]['message']['content'].strip()

# Helper opcional para limpiar JSONs, ya que los modelos a veces ponen ```json ... ```
def clean_json_text(text: str) -> str:
    # Si el modelo devuelve bloques de código markdown, los quitamos
    match = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()
