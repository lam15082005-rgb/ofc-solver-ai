# OFC Solver Framework (C++)

This directory contains the C++ implementation of the OFC (Open-Face Chinese Poker) solver.

## What it does
- Game Theory Optimal (GTO) solving using Counterfactual Regret Minimization (CFR)
- Python bindings via Boost.Python
- Fast C++ performance for real-time solving

## Building

### Linux (Railway/Production)
```bash
./build_linux.sh
```

### macOS
```bash
./build_macos.sh
```

## Dependencies
- C++17 compiler (g++ or clang++)
- Python 3.11+ development headers
- Boost.Python
- Boost.NumPy

## Docker Build
The Dockerfile automatically builds this framework during deployment.
