# final_writer.py
import json
from agents.base_agent import BaseAgent
import re

WRITER_PROMPT = """
You are the FinalWriter.
Your only job is to write high-quality narrative prose.
Write 1–3 paragraphs of narrative prose based on the Sub-event and Instructions.
Maintain the context of the story established by previous chapters.

Sub-event:
{sub_event}

Instructions:
{instructions}

RESPONSE MUST CONTAIN NO JSON, NO MARKDOWN TAGS (```), NO HEADINGS, AND NO INTRODUCTORY PHRASES. 
Only the story text itself.
"""

class FinalWriter(BaseAgent):

    def clean_prose_output(self, text: str) -> str:
        """Limpia el texto de cualquier meta-información o tags no deseados."""
        # 1. Quitar posibles bloques de código Markdown (```) o comentarios
        cleaned = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        
        # 2. Quitar prefijos comunes (e.g., "Aquí está la historia:", "Story Text:")
        # Esto es más un "best effort"
        prefixes = [
            "story text:", "prose:", "the story:", "a brief narrative:",
            "aquí está la historia:", "narrativa:", "respuesta:"
        ]
        
        for prefix in prefixes:
            if cleaned.lower().strip().startswith(prefix):
                cleaned = cleaned.replace(prefix, "", 1)
        
        return cleaned.strip()


    def write_sub_event(self, sub_event, instructions):
        prompt = WRITER_PROMPT.format(
            sub_event=json.dumps(sub_event, indent=2),
            instructions=instructions
        )
        raw = self.call_llm(prompt)

        # 1. Manejo del JSON accidental (tu lógica original, mejorada para ser más estricta)
        try:
            parsed = json.loads(raw)
            # Si es un JSON válido, buscamos claves comunes para la prosa
            if isinstance(parsed, dict):
                # Intentamos extraer texto de claves comunes si es JSON
                if "text" in parsed:
                    raw = parsed["text"]
                elif "prose" in parsed:
                    raw = parsed["prose"]
                # Si fallamos, usamos el raw original para la limpieza de tags
        except:
            # No es JSON, continuamos con el texto crudo
            pass
        
        # 2. Aplicamos la limpieza de texto final
        return self.clean_prose_output(raw)

    def run(self, *args, **kwargs):
        raise NotImplementedError