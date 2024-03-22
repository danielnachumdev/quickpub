import danielutils


# need it like this for the testing
def cm(*args, **kwargs)->tuple[int,bytes,bytes]:
    return danielutils.cm(*args, **kwargs)


__all__ = [
    "cm"
]
