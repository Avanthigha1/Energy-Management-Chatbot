import json
import re
import os
import logging
from openai import OpenAI
from dotenv import load_dotenv
from app.models.intent import IntentResult, QueryType

load_dotenv()
logger = logging.getLogger("llm_service")


class LLMService:

    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY", "")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = os.getenv("OPENROUTER_MODEL", "gpt-4o-mini")
        logger.info(f"LLM connected: {self.model}")

    def detect_intent(self, query: str) -> IntentResult:
        prompt = """You are an intent extractor for an Energy Management chatbot.
Read the query and return ONLY valid JSON. No explanation. No markdown.

Intent types: single_day, floor_breakdown, comparison, pue_analysis, cooling_ratio, unknown

Date rules: "10th" or "Feb 10" → "2026-02-10", "11th" → "2026-02-11", "12th" → "2026-02-12"

Return format:
{
  "intent": "single_day",
  "date_1": "2026-02-11",
  "date_2": null,
  "metric": "total_energy"
}"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user",   "content": f'Query: "{query}"'}
            ],
            temperature=0.0,
            max_tokens=100,
        )

        raw = response.choices[0].message.content.strip()

        # Remove markdown fences if model added them
        if "```" in raw:
            raw = re.sub(r"```(?:json)?", "", raw).replace("```", "").strip()

        return IntentResult(**json.loads(raw))