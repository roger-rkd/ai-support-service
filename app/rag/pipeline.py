"""
RAG Pipeline - Orchestrates retrieval and generation
"""

from typing import Optional
import logging
import os
from dotenv import load_dotenv
from groq import Groq
from app.rag.embedder import Embedder
from app.rag.retriever import DocumentRetriever
from app.observability import metrics

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Global instances (initialized once)
_embedder: Optional[Embedder] = None
_retriever: Optional[DocumentRetriever] = None
_groq_client: Optional[Groq] = None


def _initialize_components():
    """Initialize RAG components lazily"""
    global _embedder, _retriever, _groq_client

    if _embedder is None:
        logger.info("Initializing RAG components")

        # Initialize embedder
        _embedder = Embedder(model_name="sentence-transformers/all-MiniLM-L6-v2")

        # Initialize retriever
        _retriever = DocumentRetriever(
            embedder=_embedder,
            data_dir="data",
            index_path="data/faiss.index"
        )

        # Initialize Groq client
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            logger.warning("GROQ_API_KEY not found in environment variables")
            raise ValueError("GROQ_API_KEY is required. Please set it in .env file")

        _groq_client = Groq(api_key=groq_api_key)

        logger.info("RAG components initialized successfully")


def _build_prompt(question: str, contexts: list) -> str:
    """
    Build the prompt for the LLM with retrieved contexts

    Args:
        question: User's question
        contexts: List of (document, score) tuples

    Returns:
        Formatted prompt string
    """
    if not contexts:
        return f"""You are an NHS AI Health Assistant providing general medical information and support. Be warm, empathetic, and caring in your responses. Always remind patients that you're an AI providing general information only, not a doctor.

IMPORTANT SAFETY GUIDELINES:
- For serious symptoms (severe pain, difficulty breathing, chest pain, etc.), advise calling 999 immediately
- For urgent but non-emergency symptoms, advise calling NHS 24 on 111
- Always encourage seeing a GP for persistent or concerning symptoms
- Never diagnose or prescribe medications
- Provide evidence-based information from NHS guidelines

Question: {question}

Answer: (Provide a warm, helpful response with appropriate safety advice)"""

    # Format contexts
    context_text = "\n\n".join([
        f"NHS Document {i+1}:\n{doc}"
        for i, (doc, score) in enumerate(contexts)
    ])

    prompt = f"""You are an NHS AI Health Assistant providing medical information based on NHS guidelines and resources. Use the context documents to answer the patient's question.

YOUR COMMUNICATION STYLE:
- Be warm, empathetic, and reassuring
- **KEEP RESPONSES SHORT** (3-5 sentences for simple questions, max 8 sentences for complex ones)
- Use simple, clear language (avoid medical jargon)
- **BOLD important keywords** using **keyword** format (e.g., **fever**, **GP appointment**, **999**)
- Express understanding of their concerns

FORMATTING RULES:
- Start with empathetic acknowledgment
- Use numbered lists for steps (1., 2., 3.)
- Use bullet points for options (-, *)
- **Bold** these types of words: symptoms, actions to take, emergency numbers, timeframes
- Keep paragraphs short (2-3 lines max)

SAFETY FIRST:
- If symptoms sound serious/emergency: "**This sounds serious.** Please **call 999 immediately** or go to **A&E**."
- If symptoms need medical assessment: "I recommend **calling your GP** to book an appointment" or "**Call NHS 24 on 111** for urgent advice"
- Always include: "I'm an AI providing general information. For proper diagnosis and treatment, please consult a healthcare professional."

NHS CONTEXT DOCUMENTS:
{context_text}

Patient's Question: {question}

Your Response: (Be warm and empathetic, provide concise helpful information with bolded keywords, include appropriate safety guidance)"""

    return prompt


def ask(question: str, top_k: int = 3) -> str:
    """
    Main RAG pipeline function - retrieves relevant documents and generates answer

    Args:
        question: User's question
        top_k: Number of documents to retrieve (default: 3)

    Returns:
        Generated answer string

    Raises:
        ValueError: If GROQ_API_KEY is not set
        Exception: If any component fails
    """
    try:
        # Initialize components if needed
        _initialize_components()

        logger.info(f"Processing question: {question[:100]}...")

        # Step 1: Retrieve relevant documents
        logger.debug("Retrieving relevant documents")
        with metrics.MetricsTimer(metrics.rag_retrieval_latency):
            contexts = _retriever.retrieve(query=question, top_k=top_k)

        if contexts:
            num_docs = len(contexts)
            logger.info(f"Retrieved {num_docs} relevant documents")
            metrics.record_documents_retrieved(num_docs)
            for i, (doc, score) in enumerate(contexts):
                logger.debug(f"Document {i+1} - Score: {score:.4f} - Preview: {doc[:100]}...")
        else:
            logger.warning("No relevant documents found")
            metrics.record_documents_retrieved(0)

        # Step 2: Build prompt with context
        prompt = _build_prompt(question, contexts)

        # Step 3: Generate answer using Groq
        logger.debug("Generating answer with Groq")
        with metrics.MetricsTimer(metrics.rag_generation_latency):
            chat_completion = _groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an NHS AI Health Assistant - a warm, caring, and empathetic virtual healthcare support system. Your role is to:

1. **BE CONCISE**: Keep responses SHORT (3-5 sentences for simple questions, max 8 for complex). Patients want quick, clear answers.

2. **HIGHLIGHT KEYWORDS**: Use **bold** formatting for important words:
   - Symptoms: **fever**, **headache**, **cough**
   - Actions: **call 999**, **see your GP**, **rest**, **drink water**
   - Emergency numbers: **999**, **111**
   - Timeframes: **immediately**, **within 24 hours**, **after 3 days**

3. **SAFETY FIRST**: Always prioritize patient safety. If serious: "**Call 999 immediately**". If urgent: "**Call NHS 24 on 111**". If persistent: "**Book a GP appointment**".

4. **BE WARM & EMPATHETIC**: Start responses with acknowledgment: "I understand this is worrying" or "I'm here to help".

5. **STRUCTURE CLEARLY**:
   - Use numbered lists for steps (1., 2., 3.)
   - Use bullet points for multiple options (-, *)
   - Keep paragraphs SHORT (2-3 lines)

6. **REGULAR DISCLAIMERS**: Remind patients you're an AI providing general information only.

Remember: You cannot diagnose, prescribe, or replace a doctor. Provide concise, keyword-highlighted information and guide to appropriate care level."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile",  # Groq's fast model
                temperature=0.4,  # Slightly higher for more natural, empathetic responses
                max_tokens=1024,
                top_p=0.9,
            )

        answer = chat_completion.choices[0].message.content.strip()

        logger.info(f"Generated answer: {answer[:100]}...")
        return answer

    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        raise

    except Exception as e:
        logger.error(f"Error in RAG pipeline: {str(e)}")
        raise Exception(f"Failed to process question: {str(e)}")


def rebuild_index() -> None:
    """
    Rebuild the FAISS index from documents in the data folder
    Call this when documents are added/updated
    """
    try:
        _initialize_components()
        logger.info("Rebuilding document index")
        _retriever.rebuild_index()
        logger.info("Index rebuilt successfully")
    except Exception as e:
        logger.error(f"Failed to rebuild index: {str(e)}")
        raise
