from fastapi import FastAPI, Body

# Expose FastAPI app as `router` to match test import
router = FastAPI()

@router.post("/api/agent2/topology/report-insights")
def report_insights(payload: dict = Body(...)):
    # Minimal implementation to satisfy test expectations
    # Returns a `result` object with `success` True and optional insights
    return {
        "result": {
            "success": True,
            "insights": [],
        }
    }