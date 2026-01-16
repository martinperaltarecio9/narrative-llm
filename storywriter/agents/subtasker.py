# subtasker.py
import json
from agents.base_agent import BaseAgent
from agents.base_agent import extract_json_list

SUBTASKER_PROMPT = """
You are a Sub-Event Decomposer.

Your goal is to break one high-level story event into 3–7 smaller sub-events.
The sub-events must be sequential and necessary steps to resolve the main event.

Each sub-event MUST follow this strict format:
{{
  "id": "...",
  "parent_event": "...",
  "description": "...",
  "purpose": "...",
  "characters": [...],
  "location": "..."
}}

Return ONLY a JSON list (e.g., [{{...}}, {{...}}]).
"""

class SubTasker(BaseAgent):

    def split_into_sub_events(self, event):
        prompt = SUBTASKER_PROMPT + "\n\nMain event:\n" + json.dumps(event, indent=2)

        raw = self.call_llm(prompt)

        # Usamos el nuevo extractor para listas
        parsed = extract_json_list(raw)

        if parsed and isinstance(parsed, list):
            # Asumiendo que el parsing fue exitoso y es una lista
            return parsed
        else:
            # Fallback con error claro
            return [{"error": "Invalid JSON List or parsing failed", "raw": raw, "parent_event": event.get("title", "?")}]

    def run(self, *args, **kwargs):
        raise NotImplementedError