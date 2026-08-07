"""
retrieval_eval/test_questions.py

Fixed test question set for the Memory & RAG Lab.

Each question is deliberately shaped to favor one architecture so the
comparison table shows *why* the fancier approaches exist.

All questions reference the real IronBridge policy corpus
(material_handling_procedures.md, warehouse_safety_regulations.md,
equipment_operation_safety_rules.md).
"""

from typing import List, Dict, Any

TEST_QUESTIONS: List[Dict[str, Any]] = [
    # ------------------------------------------------------------------
    # Questions that favor NAIVE RAG (general semantic match)
    # ------------------------------------------------------------------
    {
        "id": "naive_001",
        "question": "What PPE is required when handling cement on site?",
        "expected_keywords": ["gloves", "goggles", "dust mask", "PPE"],
        "favored_architecture": "naive_rag",
        "rationale": (
            "General safety topic; the answer is likely contained in a single "
            "semantic chunk about cement handling. No exact identifier or multi-hop "
            "reasoning needed."
        ),
    },
    {
        "id": "naive_002",
        "question": "What are the general warehouse safety rules for forklifts?",
        "expected_keywords": ["forklift", "speed", "pedestrian", "inspection"],
        "favored_architecture": "naive_rag",
        "rationale": (
            "Broad procedural question; vector similarity should surface the "
            "forklift section without needing keyword precision."
        ),
    },

    # ------------------------------------------------------------------
    # Questions that favor HYBRID RAG (exact identifiers / citations)
    # ------------------------------------------------------------------
    {
        "id": "hybrid_001",
        "question": "What does Policy #2 say about fire lane clearance distances?",
        "expected_keywords": ["fire lane", "clearance", "fire exit"],
        # Exact identifier from the real doc: "1 meter" (not "15 meters")
        "required_exact": ["1 meter", "1 m"],
        "favored_architecture": "hybrid_rag",
        "rationale": (
            "Contains exact identifier 'Policy #2' and a numeric distance '1 meter'. "
            "BM25 catches the exact token overlap that dense embeddings often miss."
        ),
    },
    {
        "id": "hybrid_002",
        "question": "According to the Material Handling Procedures, what is the maximum manual lift limit for steel reinforcement bars?",
        "expected_keywords": ["manual lift", "steel"],
        "required_exact": ["50kg", "50 kg", "50 kilograms"],
        "favored_architecture": "hybrid_rag",
        "rationale": (
            "Exact numeric threshold (50kg) and material name. Keyword search "
            "is more reliable than pure vector similarity for these constraints."
        ),
    },

    # ------------------------------------------------------------------
    # Questions that favor AGENTIC RAG (multi-part, multi-hop)
    # ------------------------------------------------------------------
    {
        "id": "agentic_001",
        "question": (
            "For a reservation that would breach minimum stock on Reinforcement Steel, "
            "what handling requirements apply and what does the approval workflow require?"
        ),
        "expected_keywords": ["handling", "approval"],
        # Must cover BOTH sub-topics: handling rules AND workflow rules
        "required_sub_concepts": [
            ["mechanical", "lifting", "50kg", "PPE"],           # from Material Handling
            ["supervisor", "confirm", "elow minimum", "workflow", "elicitation"],  # from Warehouse Safety
        ],
        "favored_architecture": "agentic_rag",
        "rationale": (
            "Two independent sub-questions: (1) handling rules for steel, "
            "(2) low-stock approval workflow. A single retrieval call either "
            "buries one part or misses it at narrow top_k. Agentic RAG can issue "
            "a second targeted query after observing the first retrieval."
        ),
    },
    {
        "id": "agentic_002",
        "question": (
            "If a crane operator needs to lift Reinforcement Steel above 50kg near a fire exit, "
            "what safety rules apply and what is the required PPE?"
        ),
        "expected_keywords": ["crane", "fire exit", "PPE"],
        # Must cover BOTH: equipment rules AND material handling rules
        "required_sub_concepts": [
            ["crane", "operator", "mechanical", "lifting"],      # from Equipment Operation
            ["hard hat", "gloves", "goggles", "PPE"],            # from Material Handling
        ],
        "favored_architecture": "agentic_rag",
        "rationale": (
            "Spans two policy documents (Equipment Operation + Material Handling + "
            "Warehouse Safety). Requires reasoning over handling rules, equipment rules, "
            "and spatial safety rules together."
        ),
    },
]

QUESTIONS_BY_ID = {q["id"]: q for q in TEST_QUESTIONS}