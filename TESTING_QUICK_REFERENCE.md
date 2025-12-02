# Quick Reference: Training Package Testing

## Current Status
- **Coverage**: 39% (544/887 lines)
- **Tests**: 27 passing
- **Duration**: ~3.9 seconds
- **Status**: ✓ All passing

## Run Tests

### All training tests:
```bash
cd /home/mike/ProjetosPython/Xadrez_AI_Final
python3 -m pytest tests/test_training*.py -v
```

### With coverage report:
```bash
python3 -m pytest tests/test_training*.py --cov=training --cov-report=term-missing
```

### Generate HTML coverage:
```bash
python3 -m pytest tests/test_training*.py --cov=training --cov-report=html
```

Then open `htmlcov/index.html` in a browser.

## Module Coverage Summary

| Module | Coverage | Status |
|--------|----------|--------|
| config.py | 92% | ✓ Production Ready |
| eval_arena.py | 100% | ✓ Complete |
| replay_buffer.py | 87% | ✓ Excellent |
| selfplay.py | 77% | ✓ Good |
| prechecks.py | 75% | ✓ Good |
| checks.py | 78% | ✓ Good |
| encoder.py | 71% | ✓ Good |
| mcts.py | 65% | Need more tests |
| model.py | 66% | Need more tests |
| device.py | 62% | Need more tests |
| trainer.py | 33% | Need more tests |
| batch_sampler.py | 22% | Need more tests |
| arena_runner.py | 23% | Need more tests |
| run_smoke.py | 15% | Need more tests |
| run_iteration.py | 10% | Need many tests |
| train_optimized.py | 0% | Critical gap |
| train.py | 0% | Critical gap |
| eval_loop.py | 0% | Critical gap |

## High-Value Targets for Test Addition

### Must Have (0% coverage, core functionality):
1. **train_optimized.py** (121 lines)
   - test_train_step_basic
   - test_train_step_with_accumulation
   - test_train_step_with_amp
   - test_checkpoint_manager

2. **train.py** (43 lines)
   - test_main_entry_point
   - test_argument_parsing
   - test_training_workflow

3. **eval_loop.py** (42 lines)
   - test_evaluation_loop
   - test_metrics_calculation
   - test_result_reporting

### Should Have (>50% coverage, important paths):
4. **run_iteration.py** (91 lines, 10%)
   - test_complete_iteration
   - test_selfplay_training_eval

5. **run_smoke.py** (52 lines, 15%)
   - test_smoke_test_runs

## Test Development Tips

### Testing Device-Aware Code:
```python
def test_something_with_device(monkeypatch):
    import torch
    # Patch to force CPU
    monkeypatch.setattr(torch.cuda, 'is_available', lambda: False)
    # Now test code that checks device
```

### Testing Torch Operations:
```python
def test_tensor_creation():
    device = torch.device('cpu')
    t = torch.randn(2, 13, 8, 8, device=device)
    assert t.device == device
```

### Testing with Temp Directories:
```python
def test_file_operations(tmp_path):
    path = tmp_path / 'test_file.pt'
    # Use path for testing file I/O
```

## File Locations

- **Test Files**: `/home/mike/ProjetosPython/Xadrez_AI_Final/tests/test_training_*.py`
- **Source Files**: `/home/mike/ProjetosPython/Xadrez_AI_Final/training/`
- **Coverage Report**: `/home/mike/ProjetosPython/Xadrez_AI_Final/htmlcov_training/index.html`

## Target: 95% Coverage

**Currently**: 39% (544 lines covered)
**Target**: 95% (~ 843 lines covered)
**Gap**: 299 lines to cover

**Strategy**:
1. Add tests for 0% modules (200 lines) → ~56% coverage
2. Add tests for <50% modules (200 lines) → ~81% coverage
3. Edge cases and error handling → ~95% coverage

---
Last updated: December 1, 2024
