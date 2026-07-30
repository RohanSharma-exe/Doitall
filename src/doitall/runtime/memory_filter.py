from doitall.models.memory import Memory


class MemoryFilter:
    def allow(
        self,
        memory: Memory,
    ) -> bool:
        return True
