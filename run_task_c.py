import sys
sys.path.insert(0, 'd:/美团')
from backend.test_harness import SCENARIOS
print(f'Scenarios: {len(SCENARIOS)}')
print(list(SCENARIOS.keys()))