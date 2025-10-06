import os
import random
import time
import json
import sys
import requests
from typing import List

import PyPDF2
from sentence_transformers import SentenceTransformer
import faiss
from flotorch.sdk.llm import FlotorchLLM


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file."""
    text_content = ""
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            print(f"Successfully loaded PDF: {pdf_path}")
            print(f"Total pages: {len(pdf_reader.pages)}")
            
            # Extract text from all pages
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text.strip():  # Only add non-empty pages
                    text_content += page_text + "\n\n"
                    
            print(f"Extracted text length: {len(text_content)} characters")
            
    except FileNotFoundError:
        print(f"Error: PDF file '{pdf_path}' not found.")
        return ""
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""
        
    return text_content


def split_text_into_sentences(text: str) -> List[str]:
    """Split text content into sentences for embedding."""
    sentences = []
    
    # Split by paragraphs first, then by sentences
    for paragraph in text.split("\n\n"):
        # Clean paragraph
        paragraph = paragraph.strip().replace("\n", " ")
        if not paragraph:
            continue
            
        # Simple sentence splitting (can be improved with nltk or spacy)
        current_sentences = paragraph.split(". ")
        for i, sentence in enumerate(current_sentences):
            sentence = sentence.strip()
            if sentence:
                # Add period back except for last sentence
                if i < len(current_sentences) - 1 and not sentence.endswith("."):
                    sentence += "."
                sentences.append(sentence)
    
    # Filter out very short sentences
    sentences = [s for s in sentences if len(s) > 30]
    
    print(f"Extracted {len(sentences)} sentences from PDF")
    return sentences


def create_faiss_index(sentences: List[str], embedder: SentenceTransformer):
    """Create and train FAISS index with sentence embeddings."""
    
    # Generate embeddings for all sentences
    print("Generating embeddings for sentences...")
    sentence_embeddings = embedder.encode(sentences, convert_to_numpy=True)
    print(f"Embeddings shape: {sentence_embeddings.shape}")
    
    # FAISS index configuration
    dimension = sentence_embeddings.shape[1]  # Embedding dimension
    num_vectors = sentence_embeddings.shape[0]  # Number of sentences
    
    # Create the index
    if num_vectors < 100:
        # Use simpler index for small datasets
        index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
        print("Using IndexFlatIP for small dataset")
    else:
        # Use more complex index for larger datasets
        nlist = min(8, max(1, num_vectors // 50))  # Adaptive number of clusters
        M = 2  # Number of sub-quantizers for PQ
        nbits = 8  # Bits per sub-quantizer
        index_factory_string = f"IVF{nlist},PQ{M}x{nbits}"
        index = faiss.index_factory(dimension, index_factory_string)
        index.nprobe = min(nlist, 4)
        print(f"Using {index_factory_string} for larger dataset")
    
    print("Training index...")
    if hasattr(index, 'train'):
        index.train(sentence_embeddings)
        
    print("Adding vectors to index...")
    index.add(sentence_embeddings)
    
    print(f"Index is trained: {getattr(index, 'is_trained', True)}")
    print(f"Number of vectors in index: {index.ntotal}")
    
    return index, sentence_embeddings

def call_flotorch_api(base_url: str, model_name: str, api_key: str, prompt: str) -> tuple:
    """Call Flotorch-monitored LLM API and return response with metadata."""
    messages = [{"role": "user", "content": prompt}]
    model = FlotorchLLM(model_id=model_name, api_key=api_key, base_url=base_url)
    
    try:
        print(f"🔄 Calling Flotorch API...")
        response = model.invoke(messages)
        generated_text = response.content
        
        # Extract metadata for monitoring
        tokens_used = response.metadata.get('totalTokens', 'N/A')
        
        print(f"📊 Tokens used: {tokens_used}")
        print(f"✅ Response received successfully")
        
        return generated_text, tokens_used
        
    except Exception as e:
        print(f"❌ API Error: {e}")
        return "", 0
def generate_questions_from_pdf(sentences: List[str], base_url: str, model_name: str, api_key: str, num_questions: int = 4) -> tuple:
    """Generate questions from random sentences in the PDF using Flotorch."""
    
    # Select random sentences with sufficient length
    selected_sentences = {}
    attempts = 0
    while len(selected_sentences) < num_questions and attempts < len(sentences) * 2:
        idx = random.randint(0, len(sentences) - 1)
        sentence = sentences[idx]
        if len(sentence) > 50 and idx not in selected_sentences:
            selected_sentences[idx] = sentence
        attempts += 1
    
    # Generate questions using Flotorch
    question_prompt = """For the following sentence, create one specific question that can be answered using only the information in the sentence. 
Make the question clear and focused.

Sentence: {sentence}

Generate only the question, without any additional text or explanation."""
    
    query_texts = []
    total_tokens = 0
    
    print("🤖 Generating questions using Flotorch-monitored API calls...")
    print("Selected sentences and generated questions:\n")
    
    for i, sentence in selected_sentences.items():
        prompt = question_prompt.format(sentence=sentence)
        question, tokens = call_flotorch_api(base_url, model_name, api_key, prompt)
        
        if question.strip():
            query_texts.append(question.strip())
            total_tokens += int(tokens) if tokens != 'N/A' else 0
            
            print(f"📝 Sentence {i}: {sentence}")
            print(f"❓ Question {i}: {question.strip()}")
            print(f"🔢 Tokens for this call: {tokens}")
            print("-" * 70)
        
        time.sleep(2)  # Rate limiting
    
    print(f"\n📊 Total tokens used for question generation: {total_tokens}")
    return query_texts, total_tokens

def generate_questions_from_pdf_rag(sentences: List[str], base_url: str, model_name: str, api_key: str, num_questions: int = 4) -> tuple:
    """Generate questions from random sentences in the PDF using Flotorch."""
    
    # Select random sentences with sufficient length
    selected_sentences = {}
    attempts = 0
    while len(selected_sentences) < num_questions and attempts < len(sentences) * 2:
        idx = random.randint(0, len(sentences) - 1)
        sentence = sentences[idx]
        if len(sentence) > 50 and idx not in selected_sentences:
            selected_sentences[idx] = sentence
        attempts += 1
    
    # Generate questions using Flotorch
    question_prompt = """For the following sentence, create one specific question that can be answered using only the information in the sentence. 
Make the question clear and focused.

Sentence: {sentence}

Generate only the question, without any additional text or explanation."""
    
    query_texts = []
    total_tokens = 0
    
    print("🤖 Generating questions using Flotorch-monitored API calls...")
    print("Selected sentences and generated questions:\n")
    
    for i, sentence in selected_sentences.items():
        prompt = question_prompt.format(sentence=sentence)
        question, tokens = call_flotorch_api(base_url, model_name, api_key, prompt)
        
        if question.strip():
            query_texts.append(question.strip())
            total_tokens += int(tokens) if tokens != 'N/A' else 0
            
            print(f"📝 Sentence {i}: {sentence}")
            print(f"❓ Question {i}: {question.strip()}")
            print(f"🔢 Tokens for this call: {tokens}")
            print("-" * 70)
        
        time.sleep(2)  # Rate limiting
    
    print(f"\n📊 Total tokens used for question generation: {total_tokens}")
    return query_texts, total_tokens

def perform_monitored_rag_search(query_texts: List[str], sentences: List[str], index, embedder: SentenceTransformer, 
                                base_url: str, model_name: str, api_key: str, k: int = 3):
    """Perform RAG search and answer generation with Flotorch monitoring."""
    
    answer_prompt = """Consider the following context from the document: {context}

Now answer the following question using only the context provided: {query}

Provide a clear and concise answer based on the information given."""
    
    total_answer_tokens = 0
    
    for query_idx, query_text in enumerate(query_texts, 1):
        print(f"\n🔍 QUERY {query_idx}: {query_text}")
        print("=" * 80)
        
        # Embed the query text
        query_embedding = embedder.encode(query_text, convert_to_numpy=True).reshape(1, -1)
        
        print(f"\n🔎 Searching FAISS index for similar content...")
        distances, indices = index.search(query_embedding, k)
        
        context = ""
        print("\n📚 Retrieved Context:")
        print("-" * 50)
        
        for i, idx in enumerate(indices[0]):
            if idx < len(sentences):  # Safety check
                retrieved_sentence = sentences[idx]
                print(f"\n[{i+1}] {retrieved_sentence}")
                print(f"    Similarity Score: {distances[0][i]:.4f}")
                context += retrieved_sentence + "\n"
        
        # Generate answer using Flotorch-monitored API
        print("\n🤖 Generating answer with Flotorch monitoring...")
        prompt = answer_prompt.format(context=context, query=query_text)
        answer, tokens = call_flotorch_api(base_url, model_name, api_key, prompt)
        
        total_answer_tokens += int(tokens) if tokens != 'N/A' else 0
        
        print("\n💡 ANSWER:")
        print("-" * 20)
        print(answer)
        print(f"\n🔢 Tokens used for this answer: {tokens}")
        print("\n" + "="*80 + "\n")
        
        time.sleep(2)  # Rate limiting
    
    return total_answer_tokens


def perform_rag_search(query_texts: List[str], sentences: List[str], index, embedder: SentenceTransformer, api_key: str, k: int = 3):
    """Perform RAG search and answer generation."""
    
    answer_prompt = """Consider the following context from the document: {context}

Now answer the following question using only the context provided: {query}

Provide a clear and concise answer based on the information given."""
    
    for query_idx, query_text in enumerate(query_texts, 1):
        print(f"\n QUERY {query_idx}: {query_text}")
        print("=" * 80)
        
        # Embed the query text
        query_embedding = embedder.encode(query_text, convert_to_numpy=True).reshape(1, -1)
        
        print(f"\n Searching index for similar content...")
        distances, indices = index.search(query_embedding, k)
        
        context = ""
        print("\n Retrieved Context:")
        print("-" * 50)
        
        for i, idx in enumerate(indices[0]):
            if idx < len(sentences):  # Safety check
                retrieved_sentence = sentences[idx]
                print(f"\n[{i+1}] {retrieved_sentence}")
                print(f"    Similarity Score: {distances[0][i]:.4f}")
                context += retrieved_sentence + "\n"
        
        # Generate answer using Gemini
        print("\n Generating answer...")
        prompt = answer_prompt.format(context=context, query=query_text)
        answer = call_gemini_api(api_key, prompt)
        
        print("\n ANSWER:")
        print("-" * 20)
        print(answer)
        print("\n" + "="*80 + "\n")
        
        time.sleep(2)  # Rate limiting
