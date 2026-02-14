from app.database import SessionLocal
from app.models import KnownASN, Link, Site


def run_seed() -> None:
    db = SessionLocal()
    try:
        if db.query(Site).count() > 0:
            print("Seed already present; skipping")
            return

        alpha = Site(name="site-a")
        bravo = Site(name="site-b")
        db.add_all([alpha, bravo])
        db.flush()

        links = [
            Link(site_id=alpha.id, name="wan1", expected_asn=64512),
            Link(site_id=alpha.id, name="wan2", expected_asn=64513),
            Link(site_id=bravo.id, name="wan1", expected_asn=64514),
        ]
        db.add_all(links)

        db.add_all(
            [
                KnownASN(site="site-a", link="wan1", asn=64512),
                KnownASN(site="site-a", link="wan2", asn=64513),
                KnownASN(site="site-b", link="wan1", asn=64514),
            ]
        )

        db.commit()
        print("Seed complete")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
