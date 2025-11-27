from typing import List, Dict
import google.generativeai as genai
from agents.prompts import (
    GLOBAL_ANSWER_PROMPT,
    SELECTED_TEXT_ANSWER_PROMPT,
    MODE_INSTRUCTIONS,
)


class BookAgent:
    """Agent for answering questions about the book."""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        """
        Initialize the agent.

        Args:
            api_key: Google API key
            model: Gemini model to use
        """
        # Configure genai only if not already configured
        if not hasattr(genai, '_configured') or not genai._configured:
            genai.configure(api_key=api_key)
            genai._configured = True
        self.model = genai.GenerativeModel(model)

    async def answer_with_context(
        self, question: str, chunks: List[Dict], mode: str = "answer"
    ) -> str:
        """
        Answer a question using retrieved context chunks.

        Args:
            question: User's question
            chunks: Retrieved chunks with text and metadata
            mode: Query mode (answer, explain, summarize)

        Returns:
            Generated answer
        """
        # Format context from chunks
        context = self._format_context(chunks)

        # Build prompt
        prompt = GLOBAL_ANSWER_PROMPT.format(question=question, context=context)

        # Add mode-specific instruction
        if mode in MODE_INSTRUCTIONS:
            prompt += f"\n\n{MODE_INSTRUCTIONS[mode]}"

        # Generate answer with safety settings
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=500,
            ),
            safety_settings={
                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            }
        )

        # Handle response safely
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                return candidate.content.parts[0].text
            else:
                return f"Response blocked. Reason: {candidate.finish_reason}"
        return "No response generated"

    async def answer_from_selection(self, question: str, selected_text: str) -> str:
        """
        Answer a question based only on selected text.

        Args:
            question: User's question
            selected_text: User-selected text from the book

        Returns:
            Generated answer
        """
        # Build prompt
        prompt = SELECTED_TEXT_ANSWER_PROMPT.format(
            question=question, selected_text=selected_text
        )

        # Generate answer with safety settings
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=500,
            ),
            safety_settings={
                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE",
            }
        )

        # Handle response safely
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                return candidate.content.parts[0].text
            else:
                return f"Response blocked. Reason: {candidate.finish_reason}"
        return "No response generated"

    def _format_context(self, chunks: List[Dict]) -> str:
        """
        Format retrieved chunks into context string.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Formatted context string
        """
        if not chunks:
            return "No relevant context found."

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            text = chunk.get("text", "")
            metadata = chunk.get("metadata", {})
            section = metadata.get("section", "Unknown section")

            context_parts.append(f"[{i}] From {section}:\n{text}")

        return "\n\n".join(context_parts)
