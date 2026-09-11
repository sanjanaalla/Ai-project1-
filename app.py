import json
from pathlib import Path

notes_path = Path(__file__).with_name("notes.json")

with notes_path.open("r", encoding="utf-8") as file:
    notes = json.load(file)

print("Welcome to your AI Study Assistant!")
print("Type 'exit' to stop.")

while True:
    question = input("\nYour question: ").strip().lower()

    if question == "exit":
        print("Goodbye!")
        break

    if not question:
        print("Please enter a question.")
        continue

    found = False

    for topic, explanation in notes.items():
        if topic in question:
            print("\nTopic:", topic)
            print("Answer:", explanation)
            found = True

    if not found:
        print("I couldn't find a matching topic in my notes.")