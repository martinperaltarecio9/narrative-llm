from huggingface_hub import InferenceClient

client = InferenceClient(
    provider="groq",
    api_key='',   #poner tu API_KEY de HF. te van a cobrar, hay prueba gratis igual
)

completion = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ],
)

print(completion.choices[0].message)