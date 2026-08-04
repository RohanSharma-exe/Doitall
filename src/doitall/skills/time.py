"""Time and timezone querying skill module."""

from datetime import UTC, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from doitall.models.tool_definition import ToolDefinition
from doitall.skills.base import BaseSkill


class TimeSkill(BaseSkill):
    """Returns the current date and time for a timezone."""

    name = "time"
    description = "Get the current date and time for an IANA timezone."

    @classmethod
    def definition(cls) -> ToolDefinition:
        """Return tool definition schema for time skill."""
        return ToolDefinition(

            name=cls.name,
            description=cls.description,
            input_schema={
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "IANA timezone name, for example UTC or America/New_York.",
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
        )

    async def execute(self, timezone: str = "UTC") -> dict[str, str]:
        try:
            tz = ZoneInfo(timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unknown timezone: {timezone}") from exc

        now = datetime.now(tz)
        return {
            "timezone": timezone,
            "iso": now.isoformat(),
            "utc": datetime.now(UTC).isoformat(),
        }
