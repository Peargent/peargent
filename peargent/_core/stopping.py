## peargent/core/stopping.py

class StopCondition:
    def should_stop(self, step_number: int, memory: list) -> bool:
        raise NotImplementedError("Must implement should_stop method")
    
class StepLimitCondition(StopCondition):
    def __init__(self, max_steps: int):
        self.max_steps = max_steps
    
    def should_stop(self, step_number: int, memory: list) -> bool:
        return step_number >= self.max_steps
    
def limit_steps(n: int) -> StopCondition:
    return StepLimitCondition(n)