"""Prompt templates for the RAG chatbot."""

GLOBAL_ANSWER_PROMPT = """You are a helpful assistant answering questions about the book "AI-Driven & Spec-Driven Development Handbook".

Use ONLY the context passages below from the book.

Question:
{question}

Context:
{context}

Answer clearly in 3-6 sentences."""

SELECTED_TEXT_ANSWER_PROMPT = """You are answering based ONLY on the selected text from the book "AI-Driven & Spec-Driven Development Handbook".

Selected Text:
{selected_text}

Question:
{question}

If the selected text does not contain the answer, say so honestly."""

# Mode-specific instructions
MODE_INSTRUCTIONS = {
    "answer": "Provide a direct, concise answer to the question.",
    "explain": "Provide a detailed explanation with context and examples.",
    "summarize": "Provide a brief summary of the relevant information.",
}
