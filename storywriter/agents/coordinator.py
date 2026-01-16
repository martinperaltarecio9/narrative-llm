# coordinator.py
import json
from agents.base_agent import BaseAgent
from agents.base_agent import extract_json


INITIAL_INSTRUCTIONS_PROMPT = """
You are the Writing Coordinator.
Provide focused narrative instructions for the writer based on the SUB-EVENT and CHAPTER CONTEXT.

SUB-EVENT: {sub_event}
CHAPTER CONTEXT: {chapter_context}

Return ONLY ONE JSON OBJECT:
{{
  "instructions": "A brief, actionable directive for the writer (e.g., focus on mood, dialogue, character motivation)."
}}
"""

REVIEW_WRITING_PROMPT = """
You are the Writing Reviewer.
Evaluate the TEXT provided against the SUB-EVENT goals.
If the text is sufficient, set status to "approved". Otherwise, provide fixes.

TEXT: {text}
SUB-EVENT: {sub_event}
CHAPTER INDEX: {chapter_index}

Return ONLY ONE JSON OBJECT:
{{
  "status": "approved" or "needs_revision",
  "issues": "A clear list of problems (e.g., plot hole, wrong character, inconsistent tone).",
  "rewrite_instructions": "Specific, actionable steps for the FinalWriter to fix the issues."
}}
"""

class Coordinator(BaseAgent):

    def initial_instructions(self, sub_event, chapter_context):
        prompt = INITIAL_INSTRUCTIONS_PROMPT.format(
            sub_event=json.dumps(sub_event, indent=2),
            chapter_context=chapter_context
        )
        raw = self.call_llm(prompt)
        
        # 1. Parsing seguro
        parsed = extract_json(raw)

        if parsed:
            # 2. Extracción segura de la instrucción
            return parsed.get("instructions", "Write a coherent narrative following the sub-event.")
        else:
            # Fallback simple
            return "Write a coherent narrative following the sub-event."

    def review(self, text, sub_event, chapter_index):
        prompt = REVIEW_WRITING_PROMPT.format(
            text=text,
            sub_event=json.dumps(sub_event, indent=2),
            chapter_index=chapter_index
        )
        raw = self.call_llm(prompt)

        # 1. Parsing seguro
        parsed = extract_json(raw)

        if parsed:
            # 2. Aseguramos que los campos clave existan para evitar KeyError en el Controller
            return {
                "status": parsed.get("status", "needs_revision"),
                "issues": parsed.get("issues", "Parsing successful, but required fields missing."),
                "rewrite_instructions": parsed.get("rewrite_instructions", "Provide more detail in the next revision.")
            }
        else:
            # Fallback robusto forzando la revisión
            return {
                "status": "needs_revision",
                "issues": "Invalid JSON output from the Reviewer LLM.",
                "rewrite_instructions": "Rewrite the section, focusing strictly on fulfilling the sub-event goal."
            }

    def run(self, *args, **kwargs):
        raise NotImplementedError