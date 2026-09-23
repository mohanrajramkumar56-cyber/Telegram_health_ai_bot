from fastapi import APIRouter, Depends

from app.schemas import KBQuery, OutbreakQuery, VaccineQuery
from app.services.kb import get_prevention, get_symptoms, get_vaccine_schedule
from app.services.outbreaks import format_outbreak_response

router = APIRouter(tags=["knowledge-base"])


@router.get("/symptoms")
async def symptoms(query: KBQuery = Depends()):
    return {"answer": get_symptoms(query.disease)}


@router.get("/prevention")
async def prevention(query: KBQuery = Depends()):
    return {"answer": get_prevention(query.disease)}


@router.get("/vaccine/schedule")
async def vaccine_schedule(query: VaccineQuery = Depends()):
    return {"answer": get_vaccine_schedule(query.age_months)}


@router.get("/outbreak/status")
async def outbreak_status(query: OutbreakQuery = Depends()):
    return {"status": format_outbreak_response(query.district, query.state)}
