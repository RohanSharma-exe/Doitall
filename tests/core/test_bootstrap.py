from doitall.core.bootstrap import bootstrap
from doitall.services.registry import container
from doitall.skills.manager import SkillManager
from doitall.skills.registry import SkillRegistry


def test_bootstrap_registers_skill_services():
    container.clear()

    bootstrap()

    assert container.has("skill_registry")
    assert container.has("skill_manager")

    assert isinstance(
        container.resolve("skill_registry"),
        SkillRegistry,
    )

    assert isinstance(
        container.resolve("skill_manager"),
        SkillManager,
    )
