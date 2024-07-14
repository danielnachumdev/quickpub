from ...constraint_enforcer import ConstraintEnforcer


class RemoteVersionEnforcer(ConstraintEnforcer):
    def enforce(self, demo: bool, **kwargs) -> None: # type: ignore
        if demo:
            return


__all__ = [
    'RemoteVersionEnforcer'
]
