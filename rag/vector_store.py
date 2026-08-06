import os
from langchain_qdrant import QdrantVectorStore
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from rag.chunking import get_policy_chunks
from qdrant_client import QdrantClient
from qdrant_client.http import models

def setup_vector_store():
    # 1. الحصول على الـ chunks
    chunks = get_policy_chunks()
    
    # 2. إعداد الـ Embeddings
    print("Initializing FastEmbed...")
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    
    # 3. إعداد مسار التخزين
    path = os.path.join(os.path.dirname(__file__), "local_qdrant")
    
    # 4. بناء الـ Vector Store بالطريقة المباشرة (عشان نهرب من الـ AssertionError)
    print(f"Indexing {len(chunks)} chunks into Qdrant...")
    
    vector_store = QdrantVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        path=path,  # التخزين المحلي
        collection_name="ironbridge_policies",
        force_recreate=True # عشان لو فيه داتا قديمة ممسوحة يمسحها ويبدأ نظيف
    )
    
   # 5. بناء metadata index صريح على الحقل "metadata.source" عشان الفلترة
    # تستخدم index حقيقي وقت البحث، مش full scan (rubric requirement)
    print("Creating payload index on metadata.source...")
    vector_store.client.create_payload_index(
        collection_name="ironbridge_policies",
        field_name="metadata.source",
        field_schema="keyword",
    )

    print("✅ Qdrant Vector Store is ready, indexed, and payload-indexed!")
    return vector_store

if __name__ == "__main__":
    setup_vector_store()