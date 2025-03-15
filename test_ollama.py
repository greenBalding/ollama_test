import ollama

response = ollama.chat(model='gemma3:1b', messages=[
    {'role': 'user', 'content': 'Generate a multiple choice question for me about AI.'}
])

print(response['message']['content'])