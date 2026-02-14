from sqlalchemy.orm import Session

from app.drift_engine.rules import apply_new_asn_rule
from app.models import SyslogMessage


def process_ingested_message(db: Session, payload: dict[str, str | int]):
    message = SyslogMessage(
        site=str(payload["site"]),
        link=str(payload["link"]),
        asn=int(payload["asn"]),
        raw=str(payload["raw"]),
    )
    db.add(message)
    apply_new_asn_rule(db, site=message.site, link=message.link, asn=message.asn)
    db.commit()
    db.refresh(message)
    return message
