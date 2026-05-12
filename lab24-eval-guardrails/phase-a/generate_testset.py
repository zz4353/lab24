"""
Task A.1 — Synthetic Test Set Generation
Generate 50 questions từ Lab18 document corpus với RAGAS TestsetGenerator.
Distribution: 50% simple, 25% reasoning, 25% multi_context

Output: phase-a/testset_v1.csv
"""

import os
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from rag_adapter import LAB18_DATA_DIR

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from ragas.testset import TestsetGenerator
from ragas.testset.synthesizers import (
    SingleHopSpecificQuerySynthesizer,
    MultiHopAbstractQuerySynthesizer,
    MultiHopSpecificQuerySynthesizer,
)
from ragas.llms import llm_factory
from ragas.embeddings import embedding_factory
from ragas.testset.transforms.extractors import EmbeddingExtractor, SummaryExtractor
from ragas.testset.transforms.extractors.llm_based import NERExtractor, ThemesExtractor
from ragas.testset.transforms.filters import CustomNodeFilter
from ragas.testset.transforms.relationship_builders import CosineSimilarityBuilder, OverlapScoreBuilder
from ragas.testset.transforms.engine import Parallel
from ragas.testset.graph import NodeType


def load_documents():
    raw_docs = []
    for fname in os.listdir(LAB18_DATA_DIR):
        if fname.endswith('.pdf'):
            fpath = os.path.join(LAB18_DATA_DIR, fname)
            print(f"Loading: {fname}")
            loader = PyPDFLoader(fpath)
            raw_docs.extend(loader.load())
    print(f"Loaded {len(raw_docs)} pages total")

    # Pre-chunk to ~400 tokens to avoid HeadlineSplitter in RAGAS 0.4.3
    splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
    docs = splitter.split_documents(raw_docs)
    print(f"Split into {len(docs)} chunks (capping at 80 to avoid API overload)")
    # Sample evenly across the corpus to keep domain diversity
    if len(docs) > 80:
        step = len(docs) // 80
        docs = docs[::step][:80]
    print(f"Using {len(docs)} chunks")
    return docs


def main():
    print("=== Task A.1: Synthetic Test Set Generation ===")

    documents = load_documents()

    openai_client = OpenAI()
    llm = llm_factory("gpt-4o-mini", client=openai_client)
    emb = embedding_factory("openai", model="text-embedding-3-small", client=openai_client)

    generator = TestsetGenerator(llm=llm, embedding_model=emb)

    query_distribution = [
        (SingleHopSpecificQuerySynthesizer(llm=llm), 0.5),
        (MultiHopAbstractQuerySynthesizer(llm=llm), 0.25),
        (MultiHopSpecificQuerySynthesizer(llm=llm), 0.25),
    ]

    # Custom transforms: bỏ HeadlinesExtractor + HeadlineSplitter (gây lỗi với PDF không có headlines)
    def filter_docs(node):
        return node.type == NodeType.DOCUMENT

    custom_transforms = [
        SummaryExtractor(llm=llm, filter_nodes=filter_docs),
        CustomNodeFilter(llm=llm, filter_nodes=filter_docs),
        Parallel(
            EmbeddingExtractor(
                embedding_model=emb,
                property_name="summary_embedding",
                embed_property_name="summary",
                filter_nodes=filter_docs,
            ),
            ThemesExtractor(llm=llm, filter_nodes=filter_docs),
            NERExtractor(llm=llm, filter_nodes=filter_docs),
        ),
        Parallel(
            CosineSimilarityBuilder(
                property_name="summary_embedding",
                new_property_name="summary_similarity",
                threshold=0.5,
                filter_nodes=filter_docs,
            ),
            OverlapScoreBuilder(threshold=0.01, filter_nodes=filter_docs),
        ),
    ]

    print("Generating test set (50 questions)...")
    testset = generator.generate_with_langchain_docs(
        documents=documents,
        testset_size=50,
        query_distribution=query_distribution,
        transforms=custom_transforms,
    )

    df = testset.to_pandas()

    # RAGAS 0.4.3 renamed columns — map back to standard names
    col_map = {
        'user_input': 'question',
        'reference': 'ground_truth',
        'reference_contexts': 'contexts',
        'synthesizer_name': 'evolution_type',
    }
    df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

    required_cols = ['question', 'ground_truth', 'contexts', 'evolution_type']
    for col in required_cols:
        if col not in df.columns:
            print(f"WARNING: Missing column '{col}'")

    out_path = os.path.join(os.path.dirname(__file__), 'testset_v1.csv')
    df.to_csv(out_path, index=False)
    print(f"\nSaved {len(df)} questions to {out_path}")

    print("\n--- Distribution ---")
    type_col = next((c for c in df.columns if 'type' in c.lower() or 'synth' in c.lower()), None)
    if type_col:
        print(df[type_col].value_counts())
    else:
        print("Columns:", df.columns.tolist())

    print("\nNext: review testset_v1.csv, fill in testset_review_notes.md")


if __name__ == "__main__":
    main()
