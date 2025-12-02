#!/bin/bash
# Script to setup test environment and run coverage analysis
# Run this on your local machine or in Colab

set -e

echo "========================================"
echo "Setting up test environment..."
echo "========================================"

# Create virtual environment (opcional)
# python3 -m venv venv
# . venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install torch torchvision torchaudio numpy
pip install pytest pytest-cov

echo ""
echo "========================================"
echo "Running tests with coverage..."
echo "========================================"

# Run tests with coverage
pytest -v \
  tests/test_training_device.py \
  tests/test_model_forward.py \
  tests/test_replay_buffer.py \
  tests/test_train_optimized.py \
  tests/test_mcts_and_arena.py \
  tests/test_trainer_and_train_optimized.py \
  --cov=training \
  --cov-report=term-missing \
  --cov-report=html \
  --tb=short

echo ""
echo "========================================"
echo "Coverage report generated!"
echo "========================================"
echo "HTML report: htmlcov/index.html"
