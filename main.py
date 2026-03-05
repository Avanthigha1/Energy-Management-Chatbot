"""
main.py — FastAPI entry point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.services.data_service import DataService
from app.services.llm_service import LLMService
from app.services.calculation_service import CalculationService
from app.models.intent import QueryType
from app.models.response import ChatResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

data_service        = None
llm_service         = None
calculation_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global data_service, llm_service, calculation_service
    data_service        = DataService()
    llm_service         = LLMService()
    calculation_service = CalculationService()
    logger.info(f"Ready. Available dates: {data_service.available_dates}")
    yield

app = FastAPI(
    title="Energy Management AI Chatbot",
    version="1.0.0",
    lifespan=lifespan
)

class ChatRequest(BaseModel):
    query: str = "Total energy on 2026-02-11"

#  Health check
@app.get("/health")
def health():
    return {
        "status": "ok",
        "available_dates": data_service.available_dates
    }

#  Main chat endpoint
@app.post("/chat", response_model=ChatResponse, response_model_exclude_none=True)
def chat(request: ChatRequest):
    """
    Send a natural language energy query.
    Returns text + kpis + insights as per assignment format.
    """
    try:
        
        intent = llm_service.detect_intent(request.query)
        logger.info(f"Intent: {intent.intent} | date_1={intent.date_1} | date_2={intent.date_2}")

       
        if intent.intent == QueryType.SINGLE_DAY:
            result = calculation_service.single_day(intent.date_1)

        elif intent.intent == QueryType.FLOOR_BREAKDOWN:
            result = calculation_service.floor_breakdown(intent.date_1)

        elif intent.intent == QueryType.COMPARISON:
            date_2 = intent.date_2 or data_service.available_dates[0]
            result = calculation_service.comparison(intent.date_1, date_2)

        elif intent.intent == QueryType.PUE_ANALYSIS:
            result = calculation_service.pue_analysis(intent.date_1)

        elif intent.intent == QueryType.COOLING_RATIO:
            result = calculation_service.cooling_ratio(intent.date_1)

        else:
            return ChatResponse(
                text="I can answer: total energy, floor-wise energy, date comparisons, PUE, and cooling ratio.",
                kpis={"total_energy_kwh": 0, "it_load_kwh": 0, "non_it_kwh": 0, "pue": 0},
                insights={"efficiency_status": "N/A", "spike_flag": False}
            )

        return ChatResponse(**result)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
