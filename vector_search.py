import argparse
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

parser = argparse.ArgumentParser()

parser.add_argument(
    "--refresh",
    action="store_true",
    help="Rebuild the saved collection from notes.json"
)

args = parser.parse_args()

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
# Save the database beside this Python file.
database_path = Path(__file__).with_name("qdrant_data")

client = QdrantClient(path=str(database_path))

if args.refresh and client.collection_exists("study_notes"):
    client.delete_collection("study_notes")
    print("Removed the old collection. Rebuilding from notes.json...")
if not client.collection_exists("study_notes"):
    print("Creating embeddings and saving notes...")

    embeddings = model.encode(texts)

    client.create_collection(
        collection_name="study_notes",
        vectors_config=models.VectorParams(
            size=embeddings.shape[1],
            distance=models.Distance.COSINE
        )
    )

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

    print(f"Saved {len(points)} notes.")
else:
    print("Using the saved note embeddings.")


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