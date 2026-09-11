import json
from pathlib import Path


def search_notes(question, notes):
    matches = []

    for topic, explanation in notes.items():
        if topic.lower() in question.lower():
            matches.append((topic, explanation))

    return matches


notes_path = Path(__file__).with_name("notes.json")

with notes_path.open("r", encoding="utf-8") as file:
    notes = json.load(file)

print("Welcome to your AI Study Assistant!")
print("Type 'exit' or 'quit' to stop.")

while True:
    question = input("\nYour question: ").strip()

    if question.lower() in ("exit", "quit"):
        print("Goodbye!")
        break

    if not question:
        print("Please enter a question.")
        continue

    results = search_notes(question, notes)

    if results:
        for topic, explanation in results:
            print("\nTopic:", topic)
            print("Answer:", explanation)
    else:
        print("I couldn't find a matching topic in my notes.")