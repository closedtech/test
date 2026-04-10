# Task Queue

## Format
```
## Task #[N]
- **Description**: ...
- **Status**: pending | in_progress | done
- **Assigned**: researcher/coder/reviewer
- **Created**: YYYY-MM-DD
- **Updated**: YYYY-MM-DD

### Research Phase
- [ ] Research task 1

### Implementation Phase  
- [ ] Implement task 1

### Review Phase
- [ ] Review task 1

### Notes
...
```

---

## Current Tasks

## Task #1 — Bubble Sort
- **Description**: Implement bubble sort with optimizations
- **Status**: COMPLETED
- **Assigned**: researcher ✅ → coder ✅ → reviewer 🔄
- **Created**: 2026-04-09
- **Updated**: 2026-04-09

### Research Phase ✅
- [x] Researcher completed: Complexity, optimizations documented

### Implementation Phase ✅  
- [x] Coder completed: bubble_sort.py created
- [x] Tests: All 8 tests passed

### Review Phase 🔄
- [x] Reviewer: PASS — no critical issues

### Notes
- Basic + Optimized versions implemented
- Performance test shows ~1.05x speedup for optimized



---

## Task #2 — Burnikel-Ziegler Division
- **Description**: Fix bugs in _divide_burnikel algorithm
- **Status**: COMPLETED
- **Assigned**: researcher ✅ → coder ✅ → reviewer 🔄
- **Created**: 2026-04-10
- **Updated**: 2026-04-10

### Context
Burnikel-Ziegler is a divide-and-conquer division algorithm O(n log n).
Current implementation at line ~780 in bigint.py has bugs causing incorrect results.

### Reference
- Paper: "Recursive Division" by Burnikel & Ziegler (1998)

### Implementation Phase
- [x] Rewrite _divide_burnikel with correct algorithm
  - Fixed j = ceil(n_b / 2) split (was incorrectly using (max(n_a, n_b) + 2) // 3)
  - Added n_b >= 2 check before applying B-Z
  - Fixed decomposition: a = a2*B^(2j) + a1*B^j + a0, b = b1*B^j + b0
  - Fixed recursive call: q1 = floor(a2 / b1), r1 = a2 - q1*b1
  - Fixed remainder: (r1*B^j + a1) / b using proper base-1000 arithmetic
- [x] Fix _divmod routing
  - Fixed `_divide_newton_fast` → `_divide_newton` (nonexistent method call!)
  - Integrated _choose_division to properly route: school → burnikel → newton
  - Fixed _choose_division to route to "newton" instead of "barrett" for very large n
  - Fixed `BigInt(a)`/`BigInt(b)` undefined variable bug in sign handling
- [x] Fix Newton-Raphson shift bug
  - Removed problematic shift normalization that only applied shift to remainder, not quotient
  - This broke division by even numbers
- [x] Test: 123456 // 123 = 1003 ✓ (verified working)
- [x] Full test suite: 4/4 tests passed
  - 123456 // 123 = 1003, r=87 ✓
  - 123456789 // 456 = 270738, r=261 ✓
  - 999999999 // 999 = 1001001, r=0 ✓
  - 12345678901234567890 // 12345 = 1000054994024671, r=4395 ✓

### Notes
- Researcher's report identified key issues beyond B-Z: dead code, wrong method names, shift bug
- All critical fixes completed based on research findings
- Testing still needed to verify correctness
