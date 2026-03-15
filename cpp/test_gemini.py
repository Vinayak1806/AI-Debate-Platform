import google.generativeai as genai
genai.configure(api_key='AIzaSyAx0GhciWpuUyQFwO4aVKel8Tenavn-Adk')
with open('models.txt', 'w') as f:
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                f.write(m.name + '\n')
    except Exception as e:
        f.write(f"Error: {e}\n")
