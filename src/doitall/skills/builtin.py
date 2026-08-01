from doitall.skills.calculator import CalculatorSkill
from doitall.skills.filesystem import FilesystemSkill
from doitall.skills.registry import SkillRegistry
from doitall.skills.time import TimeSkill
from doitall.skills.web_search import WebFetchSkill, WebSearchSkill


def register_builtin_skills(
    registry: SkillRegistry,
) -> None:
    registry.register(CalculatorSkill)
    registry.register(FilesystemSkill)
    registry.register(TimeSkill)
    registry.register(WebSearchSkill)
    registry.register(WebFetchSkill)
