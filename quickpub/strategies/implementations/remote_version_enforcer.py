from ..constraint_enforcer import ConstraintEnforcer


class RemoteVersionEnforcer(ConstraintEnforcer):
    def enforce(self, demo: bool, **kwargs) -> None:
        if demo:
            return


__all__ = [
    'RemoteVersionEnforcer'
]
