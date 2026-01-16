from llama_cpp import Llama

llm = Llama(model_path="./modelo_local/GGUF/modelo.gguf")

#output = llm("which is the capital of France? answer in a few words")

#print(output['choices'][0]['text'])

# Esta forma de "promptearlo" mejora mucho el resultado.

prompt = """You are a factual assistant.
Q: What is the capital of France?
A:"""

output = llm(prompt, max_tokens=50)
print(output["choices"][0]["text"])