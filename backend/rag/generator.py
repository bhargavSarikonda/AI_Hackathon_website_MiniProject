import os
import re
from typing import Any
from rag.schemas import ChatMessage, ChatSource


class ResponseGenerator:
    """Generates grounded responses with citations and follow-up prompts."""

    def generate(
        self,
        query: str,
        retrieved: list[tuple[dict[str, Any], float]],
        history: list[ChatMessage] = []
    ) -> tuple[str, list[ChatSource], list[str]]:
        top_chunk, _ = retrieved[0]

        # Build clean source excerpts
        sources: list[ChatSource] = []
        for chunk, score in retrieved:
            clean_text = re.sub(r"[*#_`|]", "", chunk["content"]).strip()
            excerpt = clean_text[:220] + ("..." if len(clean_text) > 220 else "")
            sources.append(
                ChatSource(
                    section_id=chunk["section_id"],
                    title=chunk["title"],
                    excerpt=excerpt,
                    score=round(score, 3),
                )
            )

        # Check for external LLMs
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")

        if gemini_api_key:
            print("[RAG Mode] ONLINE via Google Gemini (gemini-1.5-flash)")
            reply = self._call_gemini(query, retrieved, gemini_api_key)
        elif openai_api_key:
            print("[RAG Mode] ONLINE via OpenAI (gpt-4o-mini)")
            reply = self._call_openai(query, retrieved, openai_api_key)
        else:
            print("[RAG Mode] OFFLINE (Local Rulebook Engine)")
            reply = self._synthesize_local(query, retrieved)

        # Generate follow-up suggestions
        suggested: list[str] = []
        for chunk, _ in retrieved:
            for sq in chunk.get("suggested_questions", []):
                if sq not in suggested and sq.lower() != query.lower().strip("?"):
                    suggested.append(sq)
                if len(suggested) >= 3:
                    break
            if len(suggested) >= 3:
                break

        if not suggested:
            suggested = [
                "What is the allowed team size?",
                "Am I allowed to use ChatGPT or Claude?",
                "What is the judging rubric breakdown?"
            ]

        return reply, sources, suggested[:3]

    def _synthesize_local(self, query: str, retrieved: list[tuple[dict[str, Any], float]]) -> str:
        import re
        top_chunk, _ = retrieved[0]
        q_lower = query.lower().strip()
        words = set(re.findall(r"\b\w+\b", q_lower))

        if words.intersection({"hello", "hi", "hey", "greetings", "howdy"}) and len(words) <= 3:
            return (
                "👋 **Hello! Welcome to the Innovate AI Hackathon 2026 Assistant!**\n\n"
                "I am your official AI guide powered by the **Hackathon Rulebook & Knowledge Base**. "
                "I can answer any questions about:\n"
                "- 👥 **Team Formation & Eligibility** (Team sizes, student IDs, solo policy)\n"
                "- 🤖 **Permitted AI Tools** (ChatGPT, Claude, open-source models, cloud APIs)\n"
                "- 🍕 **Logistics & Food** (36-hour schedule, meals, 24/7 coffee, rest zones)\n"
                "- 🏆 **Judging & Prizes** (Scoring rubric, deadlines, disbursement, certificates)\n\n"
                "How can I help you today? Feel free to ask a question or click one of the suggested prompts below!"
            )

        if words.intersection({"thanks", "thank", "thx", "appreciate"}):
            return (
                "You're very welcome! 😊 Best of luck with your hackathon journey! "
                "Let me know if you need any further clarification on rules, logistics, or deadlines."
            )

        # Offline Grounded Synthesis
        lines = [
            f"📖 **Official Rulebook Answer ({top_chunk['title']}):**\n",
            top_chunk["content"].strip()
        ]

        if len(retrieved) > 1 and retrieved[1][1] > 0.35:
            second_chunk = retrieved[1][0]
            if second_chunk["section_id"] != top_chunk["section_id"]:
                lines.append(f"\n\n💡 **Related Details ({second_chunk['title']}):**\n")
                lines.append(second_chunk["content"].strip())

        citations = ", ".join([f"`[{c['section_id']} - {c['title'].split(':')[-1].strip()}]`" for c, _ in retrieved[:2]])
        lines.append(f"\n\n📌 **Verified Source Citations:** {citations}")

        return "\n".join(lines)

    def _call_gemini(self, query: str, retrieved: list[tuple[dict[str, Any], float]], api_key: str) -> str:
        try:
            import requests
            context_text = "\n\n---\n\n".join(
                [f"[{c['section_id']}] {c['title']}:\n{c['content']}" for c, _ in retrieved]
            )
            prompt = (
                f"You are the official AI Assistant for Innovate AI Hackathon 2026.\n"
                f"Answer using ONLY the following verified rulebook context with section citations.\n\n"
                f"CONTEXT:\n{context_text}\n\nUSER QUESTION: {query}"
            )
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            resp = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=12
            )
            if resp.status_code == 200:
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            pass
        return self._synthesize_local(query, retrieved)

    def _call_openai(self, query: str, retrieved: list[tuple[dict[str, Any], float]], api_key: str) -> str:
        try:
            import requests
            context_text = "\n\n---\n\n".join(
                [f"[{c['section_id']}] {c['title']}:\n{c['content']}" for c, _ in retrieved]
            )
            system_msg = (
                "You are the official AI Assistant for Innovate AI Hackathon 2026.\n"
                "Answer the participant's question accurately, helpfully, and conversationally using ONLY the verified rulebook context below.\n"
                "Always cite relevant section IDs (e.g. [Section 2.2], [Section 3.4]) in your answer.\n\n"
                f"OFFICIAL RULEBOOK CONTEXT:\n{context_text}"
            )
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key.strip()}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": query}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 700
                },
                timeout=15
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            else:
                print(f"OpenAI API Error ({resp.status_code}): {resp.text}")
        except Exception as exc:
            print(f"OpenAI Request Exception: {exc}")
        return self._synthesize_local(query, retrieved)

