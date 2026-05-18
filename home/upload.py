"""
upload.py

AI Chat & Code Audit Service using LangChain + Groq.

Modes:
  - Normal chat  → friendly AI assistant
  - Code input   → structured code quality audit with suggestions
"""

import os
import re
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


# ================= ENV SETUP =================

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# ================= CODE DETECTION =================

_CODE_KEYWORDS = [
    "def ", "class ", "import ", "from ", "#include", "function ", "const ",
    "let ", "var ", "=>", "return ", "if (", "for (", "while (", "async ",
    "public ", "private ", "protected ", "void ", "int ", "string ", "bool ",
    "elif ", "except ", "lambda ", "SELECT ", "INSERT ", "UPDATE ", "DELETE ",
    "CREATE TABLE", "ALTER TABLE",
]

_CODE_EXTS = {
    "py", "js", "ts", "jsx", "tsx", "java", "c", "cpp", "cs", "go",
    "rb", "php", "swift", "kt", "rs", "html", "css", "sql", "sh",
    "yaml", "yml", "json", "xml",
}


def is_code(text: str, ext: str = "") -> bool:
    """Detect whether input is code rather than natural language."""
    if ext and ext.lower() in _CODE_EXTS:
        return True

    # Explicit fenced code block
    if "```" in text:
        return True

    lines = text.strip().split("\n")
    keyword_hits = sum(1 for k in _CODE_KEYWORDS if k in text)
    symbol_count = len(re.findall(r"[{};]", text))
    indented_lines = sum(1 for l in lines if l.startswith(("    ", "\t")))

    if keyword_hits >= 2:
        return True
    if symbol_count >= 3 and len(lines) >= 3:
        return True
    if indented_lines >= 3 and len(lines) >= 5:
        return True

    return False


# ================= SYSTEM PROMPTS =================

_CHAT_SYSTEM = """You are CodeSageAI, a friendly and knowledgeable AI assistant.

Guidelines:
- Answer conversationally and naturally.
- Use markdown (bold, lists, code snippets) when it adds clarity.
- For coding questions without a code snippet, give guidance and short examples.
- Keep replies focused — don't pad with filler.
- Be supportive and encouraging."""

_AUDIT_SYSTEM = """You are CodeSageAI, an expert code reviewer and software quality engineer.

When given code, produce a structured audit using EXACTLY this format:

---
## Code Overview
One-paragraph summary of what the code does and its purpose.

## Code Quality  ⭐⭐⭐⭐⭐ (rate 1–5)
- Readability & naming conventions
- Structure and organisation
- Adherence to language best practices

## Issues Found
List each issue with a severity tag:
🔴 **Critical** — bugs, crashes, data loss risk
🟡 **Warning**  — logic errors, bad patterns
🔵 **Info**     — style, minor improvements

If no issues: "✅ No significant issues found."

## Security Concerns
Any vulnerabilities (injection, hardcoded secrets, unsafe inputs, etc.).
If none: "✅ No security concerns identified."

## Performance
Inefficiencies, unnecessary loops, memory issues, or O(n) surprises.
If none: "✅ Performance looks good."

## Suggestions for Improvement
Numbered, actionable list. Include brief code snippets for clarity.

## Refactored Snippet (if applicable)
Show a cleaner version of the most problematic section.
---

Be specific, educational, and actionable. Mention the language/framework when relevant."""


# ================= MAIN FUNCTION =================

def analyze_with_langchain(content: str, ext: str = "txt", chat_history: list = None) -> str:
    """
    Process user input and return an AI response.

    Args:
        content:      The user's message or code.
        ext:          File extension hint (e.g. 'py', 'js', 'txt').
        chat_history: Per-chat message history as a list of
                      {"role": "user"/"ai", "content": str} dicts.
                      Used to maintain conversation context per chat session.
    Returns:
        AI response string.
    """
    if not GROQ_API_KEY:
        return "❌ API key not configured. Set GROQ_API_KEY in your .env file."

    if not content.strip():
        return "❌ No input provided."

    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            api_key=GROQ_API_KEY,
        )

        code_mode = is_code(content, ext)
        system_prompt = _AUDIT_SYSTEM if code_mode else _CHAT_SYSTEM

        lc_messages = [SystemMessage(content=system_prompt)]

        # Inject per-chat conversation history for context
        for msg in (chat_history or []):
            role = msg.get("role", "")
            text = msg.get("content", "")
            if role == "user":
                lc_messages.append(HumanMessage(content=text))
            elif role in ("ai", "assistant"):
                lc_messages.append(AIMessage(content=text))

        # Build the current user message
        if code_mode:
            lang = ext if ext and ext not in ("txt", "md", "") else ""
            fence = f"```{lang}" if lang else "```"
            user_message = f"Please audit this code:\n\n{fence}\n{content}\n```"
        else:
            user_message = content

        lc_messages.append(HumanMessage(content=user_message))

        response = llm.invoke(lc_messages)
        return response.content or "⚠️ No response generated."

    except Exception as e:
        return f"❌ Error: {str(e)}"
