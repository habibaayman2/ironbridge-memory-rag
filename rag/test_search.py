import os
from langchain_qdrant import QdrantVectorStore
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models # استيراد الموديلات الرسمية لـ Qdrant

def test_search():
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    path = os.path.join(os.path.dirname(__file__), "local_qdrant")
    
    client = QdrantClient(path=path)
    vector_store = QdrantVectorStore(
        client=client,
        collection_name="ironbridge_policies",
        embedding=embeddings
    )
    
    query = "What are the rules for lifting steel?"
    print(f"\n🔍 Searching for: '{query}'")
    
    # بناء الـ Filter بشكل رسمي (هذا هو المطلوب في الـ Rubric)
    # بنقول له: لازم (must) يكون الحقل اللي اسمه metadata.source بيساوي القيمة دي
    qdrant_filter = models.Filter(
        must=[
            models.FieldCondition(
                key="metadata.source", 
                match=models.MatchValue(value="material_handling_procedures.md"),
            )
        ]
    )
    
    results = vector_store.similarity_search(
        query, 
        k=2,
        filter=qdrant_filter # تمرير الـ Filter الرسمي
    )
    
    print(f"\n✅ Found {len(results)} results (Filtered by Source):")
    for i, res in enumerate(results):
        print(f"\nResult {i+1} from {res.metadata['source']}:")
        print(f"Content: {res.page_content[:150]}...")

if __name__ == "__main__":
    test_search()