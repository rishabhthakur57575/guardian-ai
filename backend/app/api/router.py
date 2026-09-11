from fastapi import APIRouter
from backend.app.api.endpoints import health, events, risk, sessions, intervention, analytics, simulator

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(events.router, tags=["Events"])
api_router.include_router(risk.router, tags=["Risk Scoring"])
api_router.include_router(sessions.router, tags=["Sessions"])
api_router.include_router(intervention.router, tags=["Interventions"])
api_router.include_router(analytics.router, tags=["Analytics"])
api_router.include_router(simulator.router, tags=["Simulator"])
