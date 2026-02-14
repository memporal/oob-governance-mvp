from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.ingestion.syslog import parse_syslog_line
from app.models import DriftEvent, Link, Site
from app.state_engine.engine import process_ingested_message

router = APIRouter()


class SyslogIn(BaseModel):
    line: str


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
    return {"id": msg.id, "site": msg.site, "link": msg.link, "asn": msg.asn}


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
