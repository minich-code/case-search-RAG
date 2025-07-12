# from typing import List
# from backend.src.components.retrieval import Document
#
# class CoTPromptTemplate:
#     """
#     A template for generating a Chain-of-Thought prompt for legal analysis.
#     Ensures strict adherence to structured output with explicit example.
#     """
#
#     TEMPLATE = """
# You are a legal expert answering a query based on court case context. Follow these instructions exactly to produce a professional, accurate response with proper citations. Your response MUST include the headers 'Reasoning:' and 'Final Answer:' as shown below.
#
# **1. Context Analysis:**
# Analyze the context, consisting of text chunks from legal cases with metadata (case title, media neutral citation, chunk sequence).
#
# **2. Reasoning Step-by-Step (Chain of Thought):**
# - **Identify the Legal Issue:** State the specific legal question.
# - **Extract Relevant Legal Principles and Facts:** Quote or summarize relevant facts or principles from the context. Cite each using: 'Case Title [Year] eKLR' (e.g., 'Habiba Mohamed Al Amin & 2 others v Standard Chartered Bank of Kenya Limited & 8 others [2020] eKLR').
# - **Apply the Law:** Develop a logical, step-by-step argument addressing the query, citing context.
# - **Consider Counterarguments (if applicable):** Evaluate opposing views and explain why they do not apply, citing context.
#
# **3. Final Answer Formulation:**
# - Provide a concise, authoritative answer in formal legal language.
# - Support claims with citations formatted as 'Case Title [Year] eKLR'.
# - Exclude speculative statements or reasoning steps in the final answer.
#
# **4. Output Format (MANDATORY):**
# Your response MUST follow this structure. Use the exact headers 'Reasoning:' and 'Final Answer:'. If you deviate, the response will be invalid. If the query cannot be answered conclusively, state so under 'Final Answer:' and explain why, citing context.
#
# **Example Output:**
# ```
# Reasoning:
# The query asks for the standard for a preliminary objection. A preliminary objection is a point of law raised to challenge the validity of a case. In 'Ilmi Investments (K) Ltd v Saini & 4 others [2025] KEHC 4716 (KLR)', the court held that a preliminary objection must be a pure point of law that can dispose of the case without further evidence. This principle ensures efficiency in judicial proceedings.
#
# Final Answer:
# The standard for a preliminary objection is a pure point of law that, if upheld, disposes of the case without a full hearing [Ilmi Investments v Saini & 4 others [2025] KEHC 4716 (KLR)].
# ```
#
# **5. Fallback Instruction:**
# If the context is insufficient, provide a partial answer under 'Final Answer:' and note the limitation, citing relevant cases if possible.
#
# ---
# **CONTEXT:**
# {context}
# ---
# **USER QUERY:**
# {query}
# ---
# """
#
#     def format(self, query: str, documents: List[Document]) -> str:
#         """
#         Formats the prompt with query and document context.
#
#         Args:
#             query (str): The user query.
#             documents (List[Document]): List of reranked documents.
#
#         Returns:
#             str: Formatted CoT prompt.
#         """
#         formatted_context = self._format_context_string(documents)
#         return self.TEMPLATE.format(context=formatted_context, query=query)
#
#     @staticmethod
#     def _format_context_string(documents: List[Document]) -> str:
#         """
#         Formats the context from documents.
#
#         Args:
#             documents (List[Document]): List of documents.
#
#         Returns:
#             str: Formatted context string.
#         """
#         context_str = ""
#         for doc in documents:
#             metadata = doc.metadata or {}
#             case_title = metadata.get('case_title', 'Unknown Case')
#             media_neutral = metadata.get('media_neutral_citation', 'No Citation')
#             chunk_sequence = metadata.get('chunk_sequence', 'N/A')
#             context_str += f"\n\n--- Start of Context from Case: {case_title} {media_neutral} ---\n"
#             context_str += f"\n[Chunk {chunk_sequence}]\n{doc.content}\n"
#             context_str += f"--- End of Context from Case: {case_title} {media_neutral} ---\n"
#         return context_str.strip()

from typing import List
from backend.src.components.retrieval import Document


class CoTPromptTemplate:
    """
    A template for generating a Chain-of-Thought prompt for legal analysis.
    Ensures strict adherence to structured output with explicit example.
    """

    TEMPLATE = """
You are a legal expert answering a query based on court case context. Follow these instructions exactly to produce a professional, accurate response with proper citations. Your response MUST include the headers 'Reasoning:' and 'Final Answer:' as shown below.

**1. Context Analysis:**
Analyze the context, consisting of text chunks from legal cases with metadata (case title, media neutral citation, chunk sequence).

**2. Reasoning Step-by-Step (Chain of Thought):**
- **Identify the Legal Issue:** State the specific legal question.
- **Extract Relevant Legal Principles and Facts:** Quote or summarize relevant facts or principles from the context. Cite each using: 'Case Title [Year] eKLR' (e.g., 'Habiba Mohamed Al Amin & 2 others v Standard Chartered Bank of Kenya Limited & 8 others [2020] eKLR').
- **Apply the Law:** Develop a logical, step-by-step argument addressing the query, citing context.
- **Consider Counterarguments (if applicable):** Evaluate opposing views and explain why they do not apply, citing context.

**3. Final Answer Formulation:**
- Provide a concise, authoritative answer in formal legal language.
- Support claims with citations formatted as 'Case Title [Year] eKLR'.
- Exclude speculative statements or reasoning steps in the final answer.

**4. Output Format (MANDATORY):**
Your response MUST follow this structure. Use the exact headers 'Reasoning:' and 'Final Answer:'. If you deviate, the response will be invalid. If the query cannot be answered conclusively, state so under 'Final Answer:' and explain why, citing context.

# **Example Output:**
#     Reasoning:
#     The query asks for the standard for a preliminary objection. A preliminary objection is a point of law raised to challenge the validity of a case. In 'Ilmi Investments (K) Ltd v Saini & 4 others [2025] KEHC 4716 (KLR)', the court held that a preliminary objection must be a pure point of law that can dispose of the case without further evidence. This principle ensures efficiency in judicial proceedings.
#     Final Answer:
#     The standard for a preliminary objection is a pure point of law that, if upheld, disposes of the case without a full hearing [Ilmi Investments v Saini & 4 others [2025] KEHC 4716 (KLR)].
#     Generated code
#     **5. Fallback Instruction:**
#     If the context is insufficient, provide a partial answer under 'Final Answer:' and note the limitation, citing relevant cases if possible.

    ---
    **CONTEXT:**
    {context}
    ---
    **USER QUERY:**
    {query}
    ---
    """

    def format(self, query: str, documents: List[Document]) -> str:
        """
        Formats the prompt with query and document context.

        Args:
            query (str): The user query.
            documents (List[Document]): List of reranked documents.

        Returns:
            str: Formatted CoT prompt.
        """
        formatted_context = self._format_context_string(documents)
        return self.TEMPLATE.format(context=formatted_context, query=query)

    @staticmethod
    def _format_context_string(documents: List[Document]) -> str:
        """
        Formats the context from documents.

        Args:
            documents (List[Document]): List of documents.

        Returns:
            str: Formatted context string.
        """
        context_str = ""
        for doc in documents:
            metadata = doc.metadata or {}
            case_title = metadata.get('case_title', 'Unknown Case')
            media_neutral = metadata.get('media_neutral_citation', 'No Citation')
            chunk_sequence = metadata.get('chunk_sequence', 'N/A')
            context_str += f"\n\n--- Start of Context from Case: {case_title} {media_neutral} ---\n"
            context_str += f"\n[Chunk {chunk_sequence}]\n{doc.content}\n"
            context_str += f"--- End of Context from Case: {case_title} {media_neutral} ---\n"
        return context_str.strip()
