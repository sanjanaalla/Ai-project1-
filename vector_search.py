import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

# Load study notes.
notes_path = Path(__file__).with_name("notes.json")

with notes_path.open("r", encoding="utf-8") as file:
    notes = json.load(file)

topics = list(notes.keys())
texts = list(notes.values())

if not texts:
    raise SystemExit("Add at least one note to notes.json.")

# Create embeddings using the same model as before.
model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2",
    device="cpu"
)

embeddings = model.encode(texts)

# Create an in-memory vector database.
client = QdrantClient(":memory:")

client.create_collection(
    collection_name="study_notes",
    vectors_config=models.VectorParams(
        size=embeddings.shape[1],
        distance=models.Distance.COSINE
    )
)

# Store each embedding with its topic and original text.
points = []

for index, text in enumerate(texts):
    point = models.PointStruct(
        id=index,
        vector=embeddings[index].tolist(),
        payload={
            "topic": topics[index],
            "text": text
        }
    )
    points.append(point)

client.upsert(
    collection_name="study_notes",
    points=points,
    wait=True
)

print(f"Stored {len(points)} notes in Qdrant.")

while True:
    question = input("\nYour question (or exit): ").strip()

    if question.lower() in ("exit", "quit"):
        break

    if not question:
        continue

    question_vector = model.encode(question).tolist()

    results = client.query_points(
        collection_name="study_notes",
        query=question_vector,
        limit=1,
        score_threshold=0.40,
        with_payload=True
    ).points

    if results:
        match = results[0]
        print("Topic:", match.payload["topic"])
        print("Note:", match.payload["text"])
        print("Similarity:", round(match.score, 3))
    else:
        print("I couldn't find a sufficiently similar note.")

client.close()