# event_validator.py
import json
from agents.base_agent import BaseAgent
from agents.base_agent import extract_json

VALIDATOR_PROMPT = """
You are an Event Validator.

Evaluate whether this event is coherent, original, and non-redundant.

Event:
{event}

Other approved events:
{other_events}

Return ONLY JSON:
{{
  "valid": true/false,
  "reason": "...",
  "required_fixes": "..."
}}
"""

class EventValidator(BaseAgent):

    def validate(self, event, other_events):
        prompt = VALIDATOR_PROMPT.format(
            event=json.dumps(event, indent=2),
            other_events=json.dumps(other_events, indent=2)
        )

        raw = self.call_llm(prompt)

        # Usamos el extractor robusto
        parsed = extract_json(raw)

        if parsed:
            # Nos aseguramos de que el campo 'valid' exista y sea booleano
            if "valid" in parsed and isinstance(parsed["valid"], bool):
                return parsed
            # Si el JSON es válido pero le faltan campos, asumimos que no es válido para forzar la revisión
            return {"valid": False, "reason": "JSON structure incomplete or 'valid' field missing.", "required_fixes": "Ensure the JSON is fully completed."}
        else:
            # Fallback seguro: forzar revisión si el JSON falla, no aceptarlo.
            return {"valid": False, "reason": "Failed to parse JSON output from LLM.", "required_fixes": "Rewrite the event completely to avoid parser failure."}

    # run() queda igual
    def run(self, *args, **kwargs):
        raise NotImplementedError