import json
from pathlib import Path

from sentence_transformers import SentenceTransformer

# Read our study notes.
notes_path = Path(__file__).with_name("notes.json")

with notes_path.open("r", encoding="utf-8") as file:
    notes = json.load(file)

topics = list(notes.keys())
texts = list(notes.values())

if not texts:
    raise SystemExit("Add at least one note to notes.json.")

# Load a pretrained embedding model.
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    device="cpu"
)

# Convert all notes into vectors once.
note_embeddings = model.encode(texts, convert_to_tensor=True)

print("Embedding shape:", note_embeddings.shape)

while True:
    question = input("\nYour question (or exit): ").strip()

    if question.lower() in ("exit", "quit"):
        break

    if not question:
        continue

    # Convert the question into a vector using the same model.
    question_embedding = model.encode(
        question,
        convert_to_tensor=True
    )

    # Compare the question with every note.
    scores = model.similarity(
        question_embedding,
        note_embeddings
    )[0]

    best_index = scores.argmax().item()
    best_score = scores[best_index].item()

    # An experimental starting value, not a universal cutoff.
    threshold = 0.40

    print("Similarity:", round(best_score, 3))

    if best_score >= threshold:
        print("Closest topic:", topics[best_index])
        print("Note:", texts[best_index])
    else:
        print("I couldn't find a sufficiently similar note.")