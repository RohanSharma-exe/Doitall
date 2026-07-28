from doitall.skills.calculator import CalculatorSkill
from doitall.skills.filesystem import FilesystemSkill
from doitall.skills.registry import SkillRegistry


def test_registry_definitions():
    registry = SkillRegistry()

    registry.register(CalculatorSkill)
    registry.register(FilesystemSkill)

    definitions = registry.definitions()

    assert len(definitions) == 2

    names = {definition.name for definition in definitions}

    assert names == {
        "calculator",
        "filesystem",
    }


def test_registry_definition():
    registry = SkillRegistry()

    registry.register(CalculatorSkill)

    definition = registry.definition("calculator")

    assert definition.name == "calculator"
