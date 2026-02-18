from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.adapters.local_llm import summarize_risk
from app.adapters.sdr_ai import classify_iq_samples
from app.database import get_db
from app.ingestion.syslog import parse_syslog_line
from app.models import DriftEvent, Link, Site, SyslogMessage
from app.state_engine.engine import process_ingested_message

router = APIRouter()


class SyslogIn(BaseModel):
    line: str
    iq_samples: list[float] = Field(default_factory=list)


class TriageIn(BaseModel):
    question: str


@router.get("/health")
def healthcheck():
    return {"ok": True}


@router.post("/ingest/syslog")
def ingest_syslog(payload: SyslogIn, db: Session = Depends(get_db)):
    try:
        parsed = parse_syslog_line(payload.line)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    msg = process_ingested_message(db, parsed)

    rf_result = classify_iq_samples(payload.iq_samples)
    if rf_result and rf_result.get("label") == "clone_suspected":
        db.add(
            DriftEvent(
                event_type="hardware_spoofing",
                site=msg.site,
                link=msg.link,
                details=f"RF-ML suspected spoofed transmitter (score={rf_result.get('score')})",
            )
        )
        db.commit()

    return {"id": msg.id, "site": msg.site, "link": msg.link, "asn": msg.asn, "rf": rf_result}


@router.get("/fleet")
def fleet(db: Session = Depends(get_db)):
    site_count = db.query(Site).count()
    link_count = db.query(Link).count()
    return {"sites": site_count, "links": link_count}


@router.get("/alerts")
def alerts(db: Session = Depends(get_db)):
    events = db.query(DriftEvent).order_by(DriftEvent.id.desc()).limit(100).all()
    return [
        {
            "id": ev.id,
            "event_type": ev.event_type,
            "site": ev.site,
            "link": ev.link,
            "details": ev.details,
            "created_at": ev.created_at.isoformat(),
        }
        for ev in events
    ]


@router.post("/triage")
def triage(payload: TriageIn, db: Session = Depends(get_db)):
    recent_events = db.query(DriftEvent).order_by(DriftEvent.id.desc()).limit(20).all()
    recent_syslog = db.query(SyslogMessage).order_by(SyslogMessage.id.desc()).limit(20).all()

    context_lines = ["Recent drift events:"]
    context_lines.extend([f"- {e.event_type} {e.site}/{e.link}: {e.details}" for e in recent_events])
    context_lines.append("Recent syslog messages:")
    context_lines.extend([f"- {m.site}/{m.link} asn={m.asn} raw={m.raw}" for m in recent_syslog])
    answer = summarize_risk(payload.question, "\n".join(context_lines))
    return {"answer": answer}
