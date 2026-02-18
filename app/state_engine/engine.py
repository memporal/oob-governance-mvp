from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.ai.anomaly import Sample, detect_timeseries_anomaly
from app.drift_engine.rules import apply_new_asn_rule
from app.models import DriftEvent, SyslogMessage


def process_ingested_message(db: Session, payload: dict[str, str | int]):
    message = SyslogMessage(
        site=str(payload["site"]),
        link=str(payload["link"]),
        asn=int(payload["asn"]),
        raw=str(payload["raw"]),
    )
    db.add(message)
    apply_new_asn_rule(db, site=message.site, link=message.link, asn=message.asn)

    prior = (
        db.query(SyslogMessage)
        .filter(SyslogMessage.site == message.site, SyslogMessage.link == message.link)
        .order_by(SyslogMessage.created_at.desc())
        .limit(500)
        .all()
    )
    historical = [Sample(timestamp=m.created_at, value=float(m.asn)) for m in prior]
    anomalous = detect_timeseries_anomaly(
        historical,
        Sample(timestamp=datetime.utcnow(), value=float(message.asn)),
    )
    if anomalous:
        db.add(
            DriftEvent(
                event_type="behavioral_anomaly",
                site=message.site,
                link=message.link,
                details=f"IsolationForest flagged unexpected ASN behavior value={message.asn}",
            )
        )

    db.commit()
    db.refresh(message)
    return message
