"""initial ladder models

Revision ID: 20260613_0001
Revises:
Create Date: 2026-06-13 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260613_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "twitch_users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("twitch_id", sa.String(length=64), nullable=True),
        sa.Column("login", sa.String(length=128), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=True),
        sa.Column("avatar_url", sa.String(length=2048), nullable=True),
        sa.Column("twitch_created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("login = lower(login)", name="ck_twitch_users_login_lowercase"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_twitch_users_login"), "twitch_users", ["login"], unique=True)
    op.create_index(op.f("ix_twitch_users_twitch_id"), "twitch_users", ["twitch_id"], unique=True)

    op.create_table(
        "videos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("twitch_video_id", sa.String(length=64), nullable=False),
        sa.Column("channel_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("view_count", sa.Integer(), nullable=True),
        sa.Column("thumbnail_url", sa.String(length=2048), nullable=True),
        sa.Column(
            "chat_scan_status",
            sa.Enum(
                "not_scanned",
                "pending",
                "running",
                "completed",
                "failed",
                "partial",
                name="video_chat_scan_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("duration_seconds IS NULL OR duration_seconds >= 0"),
        sa.CheckConstraint("view_count IS NULL OR view_count >= 0"),
        sa.ForeignKeyConstraint(["channel_id"], ["twitch_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_videos_channel_id"), "videos", ["channel_id"], unique=False)
    op.create_index(op.f("ix_videos_twitch_video_id"), "videos", ["twitch_video_id"], unique=True)

    op.create_table(
        "scan_jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("video_id", sa.Uuid(), nullable=False),
        sa.Column("kind", sa.String(length=64), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "running",
                "completed",
                "failed",
                "canceled",
                name="scan_job_status",
                native_enum=False,
                create_constraint=True,
            ),
            nullable=False,
        ),
        sa.Column("progress_percent", sa.Integer(), nullable=False),
        sa.Column("processed_messages", sa.Integer(), nullable=False),
        sa.Column("total_messages_estimate", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "progress_percent >= 0 AND progress_percent <= 100",
            name="ck_scan_jobs_progress_percent",
        ),
        sa.CheckConstraint("processed_messages >= 0"),
        sa.CheckConstraint("total_messages_estimate IS NULL OR total_messages_estimate >= 0"),
        sa.ForeignKeyConstraint(["video_id"], ["videos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_scan_jobs_status"), "scan_jobs", ["status"], unique=False)
    op.create_index(op.f("ix_scan_jobs_video_id"), "scan_jobs", ["video_id"], unique=False)

    op.create_table(
        "video_chatters",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("video_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("user_login", sa.String(length=128), nullable=False),
        sa.Column("user_display_name", sa.String(length=128), nullable=True),
        sa.Column("message_count", sa.Integer(), nullable=False),
        sa.Column("first_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("message_count >= 0"),
        sa.ForeignKeyConstraint(["user_id"], ["twitch_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["video_id"], ["videos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("video_id", "user_login", name="uq_video_chatters_video_login"),
    )
    op.create_index(op.f("ix_video_chatters_user_id"), "video_chatters", ["user_id"], unique=False)
    op.create_index(op.f("ix_video_chatters_user_login"), "video_chatters", ["user_login"], unique=False)
    op.create_index(op.f("ix_video_chatters_video_id"), "video_chatters", ["video_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_video_chatters_video_id"), table_name="video_chatters")
    op.drop_index(op.f("ix_video_chatters_user_login"), table_name="video_chatters")
    op.drop_index(op.f("ix_video_chatters_user_id"), table_name="video_chatters")
    op.drop_table("video_chatters")

    op.drop_index(op.f("ix_scan_jobs_video_id"), table_name="scan_jobs")
    op.drop_index(op.f("ix_scan_jobs_status"), table_name="scan_jobs")
    op.drop_table("scan_jobs")

    op.drop_index(op.f("ix_videos_twitch_video_id"), table_name="videos")
    op.drop_index(op.f("ix_videos_channel_id"), table_name="videos")
    op.drop_table("videos")

    op.drop_index(op.f("ix_twitch_users_twitch_id"), table_name="twitch_users")
    op.drop_index(op.f("ix_twitch_users_login"), table_name="twitch_users")
    op.drop_table("twitch_users")
