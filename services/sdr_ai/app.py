from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.ai.rf_ml import RFSignatureClassifier

app = FastAPI(title="Shadow Scout SDR AI")
classifier = RFSignatureClassifier()


class RFIn(BaseModel):
    iq_samples: list[float] = Field(default_factory=list)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/classify")
def classify(payload: RFIn):
    return classifier.predict(payload.iq_samples)
