import os
from langchain_qdrant import QdrantVectorStore
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from rag.chunking import get_policy_chunks
from qdrant_client import QdrantClient
from qdrant_client.http import models

COLLECTION_NAME = "ironbridge_policies"


def setup_vector_store():
    # 1. إعداد الـ Embeddings
    print("Initializing FastEmbed...")
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    # 2. إعداد مسار التخزين
    path = os.path.join(os.path.dirname(__file__), "qdrant_data")

    client = QdrantClient(path=path)

    # 3. نتأكد الأول: هل الـ collection موجودة ومليانة بالفعل؟
    # لو أيوه، نستخدمها زي ما هي (سريع) بدل إعادة الـ embedding من الصفر
    # كل مرة -- ده اللي كان بيسبب الـ delay في Issue #6.
    collection_exists = client.collection_exists(COLLECTION_NAME)
    point_count = client.count(COLLECTION_NAME).count if collection_exists else 0

    if collection_exists and point_count > 0:
        print(f"Collection already exists with {point_count} points -- reusing it, skipping re-embedding.")
        vector_store = QdrantVectorStore(
            client=client,
            collection_name=COLLECTION_NAME,
            embedding=embeddings,
        )
        return vector_store

   
    client.close()

    # 4. أول مرة بس: نجيب الـ chunks ونبنيهم من الصفر

    # 4. أول مرة بس: نجيب الـ chunks ونبنيهم من الصفر
    chunks = get_policy_chunks()
    print(f"Indexing {len(chunks)} chunks into Qdrant (first-time setup)...")

    vector_store = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        path=path,
        collection_name=COLLECTION_NAME,
        force_recreate=True,
    )

    # 5. بناء metadata index صريح على الحقل "metadata.source" عشان الفلترة
    # تستخدم index حقيقي وقت البحث، مش full scan (rubric requirement)
    print("Creating payload index on metadata.source...")
    vector_store.client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="metadata.source",
        field_schema="keyword",
    )

    print("✅ Qdrant Vector Store is ready, indexed, and payload-indexed!")
    return vector_store


if __name__ == "__main__":
    setup_vector_store()