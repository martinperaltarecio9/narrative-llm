#!/bin/bash
# Activar entorno virtual
source .venv/bin/activate

# Rutas relativas
MODEL_DIR="./modelo_local/HF_original"
GGUF_OUT="./modelo_local/GGUF/modelo_mistral.gguf"
CONVERT_SCRIPT="./llama.cpp/convert_hf_to_gguf.py"

# Hay que crear la carpeta porque si no tira error
#mkdir -p modelo_local/GGUF

# Ejecutar conversión
python "$CONVERT_SCRIPT" "$MODEL_DIR" \
    --outfile "$GGUF_OUT"
