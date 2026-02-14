from sqlalchemy.orm import Session

from app.models import DriftEvent, KnownASN


def apply_new_asn_rule(db: Session, *, site: str, link: str, asn: int) -> DriftEvent | None:
    known = db.query(KnownASN).filter_by(site=site, link=link, asn=asn).first()
    if known:
        return None

    db.add(KnownASN(site=site, link=link, asn=asn))
    event = DriftEvent(
        event_type="new_asn",
        site=site,
        link=link,
        details=f"Observed previously unseen ASN {asn} on {site}/{link}",
    )
    db.add(event)
    return event
