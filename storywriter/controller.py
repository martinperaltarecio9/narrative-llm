import json
from llm import LLMClient

# Importamos tus agentes (asegúrate de que las rutas sean correctas)
from agents.event_seed import EventSeed
from agents.event_validator import EventValidator
from agents.subtasker import SubTasker
from agents.chapter_weaver import ChapterWeaver
from agents.coordinator import Coordinator
from agents.final_writer import FinalWriter

# --- UTILIDADES DE UI (Colores) ---
class Colors:
    HEADER = '\033[95m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_interaction(agent_name, content, color):
    """Imprime el nombre del agente y su contenido de forma bonita"""
    print(f"\n{color}{Colors.BOLD}┌─ {agent_name} dice:{Colors.END}")
    
    # Si el contenido es un dict/json, lo mostramos bonito
    if isinstance(content, (dict, list)):
        formatted_content = json.dumps(content, indent=2, ensure_ascii=False)
        print(f"{formatted_content}")
    else:
        print(f"{content}")
    
    print(f"{color}{Colors.BOLD}└───────────────────────────────{Colors.END}")

# ----------------------------------

DEFAULT_STORY_CONCEPT = "A young archaeologist discovers an ancient artifact that manipulates memory."

class Controller:

    def __init__(
        self,
        story_concept,  # Ahora lo pasamos obligatorio o desde el input
        max_seed_iterations=3, # Bajé un poco para probar más rápido
        max_writer_iterations=3,
        model_path="./modelo_local/GGUF/modelo.gguf"
    ):
        self.max_seed_iterations = max_seed_iterations
        self.max_writer_iterations = max_writer_iterations
        self.story_concept = story_concept

        print(f"{Colors.YELLOW}Cargando modelo LLM en {model_path}...{Colors.END}")
        self.llm = LLMClient(model_path=model_path, n_ctx=4096) # Aumenté contexto por seguridad

        # Instancia de agentes
        self.event_seed = EventSeed(self.llm)
        self.event_validator = EventValidator(self.llm)
        self.subtasker = SubTasker(self.llm)
        self.chapter_weaver = ChapterWeaver(self.llm)
        self.coordinator = Coordinator(self.llm)
        self.final_writer = FinalWriter(self.llm)

    # 1. EVENTO PRINCIPAL
    def generate_events(self, n_events):
        print(f"\n{Colors.HEADER}=== FASE 1: GENERACIÓN DE EVENTOS ==={Colors.END}")
        approved = []
        for i in range(n_events):
            print(f"\n--- Generando Evento {i+1}/{n_events} ---")
            
            # 1. EventSeed genera
            event = self.event_seed.generate_initial_event(
                story_concept=self.story_concept,
                index=i,
                previous_events=approved
            )
            print_interaction("EventSeed", event, Colors.CYAN)

            # Bucle de validación
            for attempts in range(self.max_seed_iterations):
                # 2. EventValidator revisa
                feedback = self.event_validator.validate(event=event, other_events=approved)
                print_interaction("EventValidator", feedback, Colors.MAGENTA)

                if feedback.get("valid", False) is True:
                    print(f"{Colors.GREEN}>> Evento Aprobado{Colors.END}")
                    approved.append(event)
                    break
                
                print(f"{Colors.YELLOW}>> Evento Rechazado. Revisando... (Intento {attempts+1}){Colors.END}")

                # 3. EventSeed revisa (si fue rechazado)
                event = self.event_seed.revise_event(event=event, feedback=feedback, other_events=approved)
                print_interaction("EventSeed (Revisión)", event, Colors.CYAN)
            else:
                # Si sale del for sin break, aceptamos el último (o podrías descartarlo)
                print(f"{Colors.RED}>> Máx iteraciones alcanzadas. Se acepta forzosamente.{Colors.END}")
                approved.append(event)

        return approved

    # 2. SUB-EVENTOS Y CAPÍTULOS
    def expand_and_weave(self, events):
        print(f"\n{Colors.HEADER}=== FASE 2: ESTRUCTURA Y CAPÍTULOS ==={Colors.END}")
        all_subs = []
        
        # Subtasker
        for idx, ev in enumerate(events):
            subs = self.subtasker.split_into_sub_events(ev)
            print_interaction(f"SubTasker (Evento {idx})", subs, Colors.BLUE)
            all_subs.extend(subs)
        
        # ChapterWeaver
        chapters = self.chapter_weaver.assign_to_chapters(all_subs)
        print_interaction("ChapterWeaver", [c.__dict__ for c in chapters], Colors.GREEN) # Asumiendo que chapter es objeto
        return chapters

    # 3. ESCRITURA FINAL
    def write_story(self, chapters):
        print(f"\n{Colors.HEADER}=== FASE 3: ESCRITURA FINAL ==={Colors.END}")
        story = ""

        for ch_idx, chapter in enumerate(chapters):
            print(f"\n{Colors.BOLD}--- Escribiendo Capítulo {ch_idx + 1} ---{Colors.END}")
            
            # Nota: Asumo que chapter tiene un atributo sub_events
            # Si chapter es un dict, cambia chapter.sub_events por chapter['sub_events']
            current_sub_events = getattr(chapter, 'sub_events', []) 

            for subev in current_sub_events:
                
                # 1. Coordinator da instrucciones
                instructions = self.coordinator.initial_instructions(
                    sub_event=subev,
                    chapter_context=ch_idx
                )
                print_interaction("Coordinator", instructions, Colors.YELLOW)

                for attempt in range(self.max_writer_iterations):

                    # 2. FinalWriter escribe
                    text = self.final_writer.write_sub_event(
                        sub_event=subev,
                        instructions=instructions
                    )
                    # Mostramos solo un pedacito del texto para no llenar la pantalla
                    preview = text[:200] + "..." if len(text) > 200 else text
                    print_interaction("FinalWriter", f"Escribió: {preview}", Colors.CYAN)

                    # 3. Coordinator revisa
                    validation = self.coordinator.review(
                        text=text,
                        sub_event=subev,
                        chapter_index=ch_idx
                    )
                    print_interaction("Coordinator (Review)", validation, Colors.YELLOW)

                    if validation.get("status") == "approved":
                        story += text + "\n\n"
                        break
                    
                    instructions = validation.get("rewrite_instructions", "")

        return story

    # PIPELINE COMPLETO
    def run(self, n_events=6):
        events = self.generate_events(n_events)
        # Nota: expand_and_weave y write_story dependen de que tengas implementadas 
        # las clases Subtasker, ChapterWeaver, etc. Si no están listas, comenta estas líneas.
        try:
            chapters = self.expand_and_weave(events)
            final_story = self.write_story(chapters)
            return final_story
        except NotImplementedError as e:
            print(f"{Colors.RED}Error: Algún agente aún no está implementado ({e}){Colors.END}")
            return events

def print_ascii_art(file_path: str, color: str = Colors.CYAN):
    """
    Lee un archivo de texto línea por línea y lo imprime en la terminal
    con el color especificado.
    """
    try:
        # Abre y lee el archivo, manejando el cierre automáticamente
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Quitamos saltos de línea y espacios al inicio/fin, luego imprimimos con color.
                print(f"{color}{Colors.BOLD}{line.rstrip()}{Colors.END}")
    except FileNotFoundError:
        print(f"\n{Colors.RED}ERROR: El archivo ASCII art no fue encontrado en la ruta: {file_path}{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}ERROR al leer el archivo ASCII art: {e}{Colors.END}")

if __name__ == "__main__":
    # --- UI RUDIMENTARIA DE ENTRADA ---
    # Define la ruta de tu archivo ASCII (ajusta si el archivo no está en la raíz)
    ASCII_FILE_PATH = "logo.txt"

    # 1. Imprime el arte desde el archivo
    print_ascii_art(ASCII_FILE_PATH, color=Colors.BLUE)
    
    # 2. Imprime el subtítulo
    print(f"{Colors.MAGENTA}{Colors.BOLD}                                            Generá tu propia aventura{Colors.END}")
    
    print("")
    user_idea = input(f"{Colors.BOLD}Insertá la idea de tu historia (en inglés): {Colors.END}")
    
    if not user_idea.strip():
        user_idea = DEFAULT_STORY_CONCEPT
        print(f"Usando concepto por defecto: {user_idea}")

    # Inicializamos controller con la idea del usuario
    # IMPORTANTE: Asegurate de tener el modelo .gguf en la ruta indicada o cambiarla aquí
    controller = Controller(
        story_concept=user_idea, 
        model_path="./modelo_local/GGUF/modelo_mistral.gguf" 
    )
    
    final_result = controller.run(n_events=3) # Pongo 3 para probar, luego sube a 6
    
    print("\n" + "="*50)
    print("RESULTADO FINAL:")
    print("="*50)
    print(final_result)