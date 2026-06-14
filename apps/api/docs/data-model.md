# Data Model

This document describes the first backend data model for Twitch Ladder.

For backend layer boundaries, Twitch integration rules, and long-running scan flow, see [architecture.md](./architecture.md).

## Model Overview

```text
TwitchUser
  has many Videos
  may be linked from VideoChatter after profile enrichment

Video
  belongs to TwitchUser as channel
  has many ScanJobs
  has many VideoChatters

ScanJob
  belongs to Video
  tracks one scan attempt

VideoChatter
  belongs to Video
  optionally belongs to TwitchUser
```

## TwitchUser

`TwitchUser` is a local projection of a Twitch account.

Initial use:

- store checked streamers/channels;
- attach VODs to a stable local channel row;
- show profile data in UI.

Future use:

- optionally link chatters/followers to the same table after profile enrichment.

Important fields:

- `id`: local UUID primary key used by our database relations.
- `twitch_id`: original Twitch user ID. Nullable because a chatter can be known by login before profile enrichment.
- `login`: normalized Twitch login and main lookup key.
- `display_name`: Twitch display name for UI.
- `avatar_url`: Twitch avatar for UI.
- `twitch_created_at`: channel/account creation time from Twitch.
- `fetched_at`: when this projection was last refreshed from Twitch.

Decision: one table for Twitch accounts instead of separate `Channel` and `Chatter` tables. A streamer and a chatter are both Twitch accounts; their role depends on how they are used in the product.

Decision: `login` is always stored lowercase. The repository normalizes it before write, and the database has a check constraint to prevent mixed-case rows.

## Video

`Video` is a Twitch VOD known to the application.

It gives scan jobs and ladder aggregates a stable local target instead of passing raw Twitch video IDs through every layer.

Important fields:

- `id`: local UUID primary key.
- `twitch_video_id`: original Twitch VOD ID.
- `channel_id`: local channel owner, linked to `twitch_users.id`.
- `title`: VOD title for UI.
- `duration_seconds`: normalized duration for sorting and calculations.
- `published_at`: VOD publish time from Twitch.
- `view_count`: Twitch VOD view count.
- `thumbnail_url`: preview image for VOD lists/cards.
- `chat_scan_status`: current chat scan state of this VOD.
- `fetched_at`: when VOD metadata was last refreshed from Twitch.

Allowed `chat_scan_status` values:

```text
not_scanned
pending
running
completed
failed
partial
```

Decision: `Video.chat_scan_status` only describes chat processing. Future metadata, emote, graph, or timeline processing should get separate status fields instead of overloading this one.
Decision: detailed scan attempt history belongs in `ScanJob`.

## ScanJob

`ScanJob` stores persistent state for one long-running scan attempt.

The API should create or read jobs; background tasks or workers should update progress and final status.

Important fields:

- `id`: local UUID job ID that can be returned to the frontend.
- `video_id`: VOD being scanned.
- `kind`: type of scan. Current expected value is `vod_chat`; leaves room for future scan types.
- `status`: current job status.
- `progress_percent`: UI-friendly progress from 0 to 100.
- `processed_messages`: number of chat messages processed so far.
- `total_messages_estimate`: optional estimate if the source provides enough data.
- `error_message`: failure details for debugging and UI.
- `started_at`: when execution actually began.
- `finished_at`: when execution ended.

Allowed `status` values:

```text
pending
running
completed
failed
canceled
```

Decision: keep `ScanJob` separate from `Video` because the same VOD can have multiple scan attempts, retries, or failures over time.

## VideoChatter

`VideoChatter` is the per-user chat activity aggregate for one VOD.

For ladder calculation, we do not need to store every chat message first. If a user wrote 120 messages in one VOD, this table stores one row with `message_count = 120`.

Important fields:

- `id`: local UUID primary key.
- `video_id`: VOD this aggregate belongs to.
- `user_id`: optional link to `TwitchUser`.
- `user_login`: required login snapshot from chat data.
- `user_display_name`: optional display name snapshot from chat data.
- `message_count`: number of messages in this VOD.
- `first_message_at`: first observed message time in this VOD.
- `last_message_at`: last observed message time in this VOD.

Decision: `user_id` is nullable by design. VOD scan should not be blocked by profile enrichment for every chatter. The scan can store `user_login` immediately, and a later enrichment job can resolve users and fill `user_id`.

Decision: uniqueness is enforced by `(video_id, user_login)`, so one chatter has one aggregate row per VOD.

## Why Store Aggregates First

The first product feature is a ladder/ranking of active chat users. It can be calculated from `VideoChatter` aggregates:

```sql
SELECT user_login, SUM(message_count)
FROM video_chatters
WHERE video_id IN (...)
GROUP BY user_login
ORDER BY SUM(message_count) DESC;
```

Storing every chat message is more expensive and should be added only when a feature requires it, such as chat replay analytics, time-series charts, moderation search, or message text search.

## Partial Aggregate Strategy

VOD scan results should be committed atomically.

During a scan, partial results should not replace production `VideoChatter` rows. If the scan fails halfway through, the visible ladder must not include half-processed data.

Preferred strategy:

```text
scan job starts
write intermediate aggregates to a staging buffer
if scan succeeds:
  replace production VideoChatter rows for the video in one transaction
if scan fails:
  keep production VideoChatter rows unchanged
  delete or retain staging rows for debugging
```

The staging storage can be a database table or another durable buffer. For large VODs, a database table is safer than keeping all aggregates in memory.

## Open Questions For Review

- Should `Video.chat_scan_status` remain a string with check constraints, or move to Python/Postgres enums later?
- Do we need a `partial` status on `ScanJob` too, or is `failed` plus `Video.chat_scan_status = partial` enough?
- Should `VideoChatter` include `source` if chat data can come from multiple Twitch endpoints?
- When should we introduce full `ChatMessage` storage, if ever?
- Should staging rows be retained after failed scans for debugging, or deleted immediately?
