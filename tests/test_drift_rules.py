from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.drift_engine.rules import apply_new_asn_rule
from app.models import DriftEvent, KnownASN


def test_new_asn_triggers_once_deterministically():
    engine = create_engine("sqlite:///:memory:")
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    db = TestingSession()
    try:
        event = apply_new_asn_rule(db, site="site-a", link="wan1", asn=65010)
        db.commit()
        assert event is not None

        second = apply_new_asn_rule(db, site="site-a", link="wan1", asn=65010)
        db.commit()
        assert second is None

        assert db.query(KnownASN).count() == 1
        assert db.query(DriftEvent).count() == 1
    finally:
        db.close()
