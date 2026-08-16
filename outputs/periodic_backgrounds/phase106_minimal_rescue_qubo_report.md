# Fase 107 - Exact minimal-rescue QUBO compilation

**Verdict:** `EXACT_MINIMAL_RESCUE_QUBO_COMPILATION_VERIFIED`

- Independent QUBO models: 265
- Certified ground states: 1476
- Variables accumulated across independent models: 19100
- Variables per model: 9..172
- Sparse nonzero QUBO terms: 32861
- Models JSONL SHA-256: `d6c813602e914b8863d248d47d7cecfcd498172ba2c3831441b750d5203c82ab`

## Methodological limits

- The QUBOs compile already enumerated minimal rescues; they do not discover new rescues.
- The certified objective uses unit node costs only.
- No quantum hardware, annealer, heuristic solver, or CA simulation was executed.
- QUBO compatibility is not evidence of quantum speedup or practical advantage.
- Results remain limited to the 265 frozen target-period-metric instances.
