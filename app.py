notes = {
    "python": "Python is a programming language used to build AI applications.",
    "llm": "An LLM is a large language model that processes and generates text.",
    "vector database": "A vector database stores vectors and searches for similar ones."
}

question = input("What do you want to learn? ").strip().lower()

found = False

for topic, explanation in notes.items():
    if topic in question:
        print("\nTopic:", topic)
        print("Answer:", explanation)
        found = True

if not found:
    print("I couldn't find a matching topic in my notes.")