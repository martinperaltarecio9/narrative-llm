# chapter_weaver.py
import json
from agents.base_agent import BaseAgent
from agents.base_agent import extract_json

CHAPTER_WEAVER_PROMPT = """
You are a Chapter Planner.

Group the following sub-events into chronological narrative chapters. 
Each chapter should contain a logical sequence of sub-events.

Output strictly ONE JSON OBJECT with the root key "chapters":
{
  "chapters": [
    {
      "chapter_id": 1,
      "summary": "...",
      "sub_events": [...] # LISTA DE SUB-EVENTOS ORIGINALES
    },
    // ... más capítulos
  ]
}
"""

class Chapter:
    def __init__(self, chapter_id, summary, sub_events):
        # Aseguramos que sub_events es una lista para evitar errores posteriores
        self.chapter_id = chapter_id
        self.summary = summary
        self.sub_events = sub_events if isinstance(sub_events, list) else []

    # Agregamos __repr__ para que se vea bien en logs del Controller
    def __repr__(self):
        return f"<Chapter {self.chapter_id}: '{self.summary[:40]}...' ({len(self.sub_events)} sub-events)>"

class ChapterWeaver(BaseAgent):

    def assign_to_chapters(self, sub_events):
        prompt = CHAPTER_WEAVER_PROMPT + "\n\nSub-events:\n" + json.dumps(sub_events, indent=2)
        raw = self.call_llm(prompt)

        # 1. Parsing seguro
        parsed = extract_json(raw)

        if not parsed:
            # Fallback por falla de parsing
            print(f"[{self.name}] ERROR: Fallo de parsing JSON para ChapterWeaver.")
            return [Chapter(1, "Parsing fallido, todos los sub-eventos agrupados.", sub_events)]

        # 2. Extracción de datos
        chapters_data = parsed.get("chapters", [])

        if not isinstance(chapters_data, list) or not chapters_data:
            # Fallback si no existe la clave 'chapters' o si no es una lista
            print(f"[{self.name}] WARNING: Clave 'chapters' inválida o vacía.")
            return [Chapter(1, "Estructura de capítulos inválida, todos los sub-eventos agrupados.", sub_events)]


        chapters = []
        for ch in chapters_data:
            chapters.append(Chapter(
                chapter_id=ch.get("chapter_id", len(chapters)+1),
                summary=ch.get("summary", "Sin resumen."),
                sub_events=ch.get("sub_events", [])
            ))

        return chapters

    def run(self, *args, **kwargs):
        raise NotImplementedError