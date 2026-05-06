from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin_pairing,
    admin_sake,
    admin_sakana,
    articles,
    auth,
    pairing_guide,
    sake,
    quiz_results,
    journal,
)

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(articles.router, prefix="", tags=["articles"])
router.include_router(pairing_guide.router, prefix="", tags=["pairing-guide"])
router.include_router(sake.router, prefix="", tags=["sake"])
router.include_router(quiz_results.router, prefix="", tags=["quiz-results"])
router.include_router(journal.router, prefix="", tags=["journal"])
router.include_router(admin_sakana.router)
router.include_router(admin_sake.router)
router.include_router(admin_pairing.router)
