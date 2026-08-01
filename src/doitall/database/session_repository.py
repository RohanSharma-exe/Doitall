"""SessionRepository — thin data-access layer for sessions and messages."""
from datetime import UTC, datetime

from sqlmodel import select

from doitall.database.models import MessageRecord, SessionRecord
from doitall.database.session import get_session as _default_get_session


def _now() -> datetime:
    return datetime.now(UTC)


class SessionRepository:
    """Synchronous CRUD operations over sessions and messages.

    Each method opens and closes its own DB session.  Pass ``session_factory``
    to override the default production ``get_session`` — useful in tests where
    you want to supply an isolated in-memory engine without monkeypatching.

    Example (test usage)::

        engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(engine)

        @contextmanager
        def factory():
            with Session(engine) as s:
                yield s

        repo = SessionRepository(session_factory=factory)
    """

    def __init__(self, session_factory=None) -> None:
        self._get_session = session_factory or _default_get_session

    # ------------------------------------------------------------------
    # Session operations
    # ------------------------------------------------------------------

    def get_or_create(
        self,
        session_id: str,
        agent_name: str = "Doitall",
        system_prompt: str = "You are a helpful AI assistant.",
        provider: str | None = None,
    ) -> SessionRecord:
        """Return an existing session or create a new one (idempotent)."""
        with self._get_session() as db:
            record = db.get(SessionRecord, session_id)
            if record is None:
                record = SessionRecord(
                    session_id=session_id,
                    agent_name=agent_name,
                    system_prompt=system_prompt,
                    provider=provider,
                )
                db.add(record)
                db.commit()
                db.refresh(record)
            return record

    def touch(self, session_id: str) -> None:
        """Update last_accessed_at to now (extend TTL)."""
        with self._get_session() as db:
            record = db.get(SessionRecord, session_id)
            if record:
                record.last_accessed_at = _now()
                db.add(record)
                db.commit()

    def delete(self, session_id: str) -> bool:
        """Hard-delete a session and all its messages. Returns True if found."""
        with self._get_session() as db:
            # Delete messages first (SQLite doesn't enforce FK cascades by default)
            stmt = select(MessageRecord).where(
                MessageRecord.session_id == session_id
            )
            messages = db.exec(stmt).all()
            for msg in messages:
                db.delete(msg)

            record = db.get(SessionRecord, session_id)
            if record is None:
                return False
            db.delete(record)
            db.commit()
            return True

    def list_sessions(self) -> list[SessionRecord]:
        """Return all sessions ordered by last_accessed_at desc."""
        with self._get_session() as db:
            stmt = select(SessionRecord).order_by(
                SessionRecord.last_accessed_at.desc()  # type: ignore[attr-defined]
            )
            return list(db.exec(stmt).all())

    def exists(self, session_id: str) -> bool:
        """Return True if the session exists in the database."""
        with self._get_session() as db:
            return db.get(SessionRecord, session_id) is not None

    # ------------------------------------------------------------------
    # Message operations
    # ------------------------------------------------------------------

    def get_messages(self, session_id: str) -> list[MessageRecord]:
        """Return all messages for a session ordered by creation time."""
        with self._get_session() as db:
            stmt = (
                select(MessageRecord)
                .where(MessageRecord.session_id == session_id)
                .order_by(MessageRecord.created_at)  # type: ignore[arg-type]
            )
            return list(db.exec(stmt).all())

    def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_calls: list[dict] | None = None,
        tool_call_id: str | None = None,
        name: str | None = None,
    ) -> MessageRecord:
        """Append a message row and return the persisted record."""
        with self._get_session() as db:
            msg = MessageRecord(
                session_id=session_id,
                role=role,
                content=content,
                tool_call_id=tool_call_id,
                name=name,
            )
            if tool_calls:
                msg.set_tool_calls(tool_calls)
            db.add(msg)
            db.commit()
            db.refresh(msg)
            return msg

    def clear_messages(self, session_id: str) -> int:
        """Delete all messages for a session. Returns number deleted."""
        with self._get_session() as db:
            stmt = select(MessageRecord).where(
                MessageRecord.session_id == session_id
            )
            messages = db.exec(stmt).all()
            count = len(messages)
            for msg in messages:
                db.delete(msg)
            db.commit()
            return count

    def message_count(self, session_id: str) -> int:
        """Return the number of messages in a session."""
        return len(self.get_messages(session_id))
