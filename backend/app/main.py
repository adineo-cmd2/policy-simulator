from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.session import Base, engine
import app.models.user  # noqa: F401
import app.models.policy_submission  # noqa: F401
import app.models.impact_model  # noqa: F401
import app.models.effect_node  # noqa: F401
import app.models.demographic_impact  # noqa: F401
import app.models.historical_analogy  # noqa: F401
import app.models.stakeholder_record  # noqa: F401
from app.api.routes import policy

settings = get_settings()
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Policy Impact Simulator")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:4329"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    return {"ok": True}


app.include_router(policy.router, prefix="/api/policy", tags=["policy"])
