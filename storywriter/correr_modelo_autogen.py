import re
import asyncio
from autogen_ext.models.llama_cpp import LlamaCppChatCompletionClient
from autogen_core.models import UserMessage


PROMPT = "What's the capital of France?"


def limpiar_output_simple(model_output: str) -> str:
    """
    Extrae y limpia solo la primera respuesta significativa del output de AutoGen/LlamaClient.
    """
    # Extraer contenido entre content='...' si existe
    match = re.search(r"content='(.*?)' usage=", model_output, re.DOTALL)
    if match:
        model_output = match.group(1)

    # Buscar los bloques [OUT]...[/OUT]
    bloques = re.findall(r'\[OUT\](.*?)\[/OUT\]', model_output, re.DOTALL)

    # Tomar la primera respuesta no vacía y limpia
    for bloque in bloques:
        texto = bloque.strip()
        if texto:
            texto = re.sub(r'\s+', ' ', texto).strip()
            return texto

    # Si no se encontró ningún bloque [OUT], devolver texto limpio general
    return re.sub(r'\s+', ' ', model_output).strip()


async def main():
    # Crear cliente del modelo local
    llama_client = LlamaCppChatCompletionClient(
        model_path="./modelo_local/GGUF/modelo.gguf",
        n_ctx=4096,
        n_threads=8
    )

    # Enviar mensaje al modelo
    result = await llama_client.create([
        UserMessage(content=PROMPT, source="user")
    ])

    # Convertir a string (por compatibilidad con la función de limpieza)
    raw_output = str(result)

    # Limpiar el texto
    limpio = limpiar_output_simple(raw_output)

    # Mostrar salida final
    print("🧹 Output limpio:", limpio)


if __name__ == "__main__":
    asyncio.run(main())
