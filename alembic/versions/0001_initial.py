"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-02-14
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
    )

    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("site_id", sa.Integer(), sa.ForeignKey("sites.id"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("expected_asn", sa.Integer(), nullable=False),
    )

    op.create_table(
        "syslog_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("site", sa.String(length=100), nullable=False),
        sa.Column("link", sa.String(length=100), nullable=False),
        sa.Column("asn", sa.Integer(), nullable=False),
        sa.Column("raw", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "known_asns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("site", sa.String(length=100), nullable=False),
        sa.Column("link", sa.String(length=100), nullable=False),
        sa.Column("asn", sa.Integer(), nullable=False),
        sa.UniqueConstraint("site", "link", "asn", name="uq_known_asn"),
    )

    op.create_table(
        "drift_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("site", sa.String(length=100), nullable=False),
        sa.Column("link", sa.String(length=100), nullable=False),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("drift_events")
    op.drop_table("known_asns")
    op.drop_table("syslog_messages")
    op.drop_table("links")
    op.drop_table("sites")
