from fastapi import APIRouter, HTTPException

from app.api.v1.endpoints.quiz_data import QUIZ_RESULTS

router = APIRouter()


@router.get("/quiz-results/{code}")
def get_quiz_result(code: str):
    result = QUIZ_RESULTS.get(code.upper())
    if not result:
        raise HTTPException(status_code=404, detail=f"No results for code '{code}'")
    return result
