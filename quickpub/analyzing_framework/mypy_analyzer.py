from .analyzer import Analyzer
class MyPyAnalyzer(Analyzer):
    def analyze(self, target_path: str) -> float:
        pass


__all__=[
    'MyPyAnalyzer',
]