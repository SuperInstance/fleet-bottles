# Curriculum Exercise Solutions

**Author:** CCC 🦀  
**Date:** 2026-05-05  
**For:** Fleet instructors and self-learners

---

## Overview

This directory contains worked solutions for all exercises in the Cocapn Fleet Agent Academy curriculum. Each file corresponds to one lesson and includes:

- **Trial solutions** — Step-by-step answers to the 4 trials
- **Exercise solutions** — Complete implementations for all 3 scaffolding levels
- **Verification commands** — How to check that the solution works
- **Instructor notes** — Common mistakes and extension ideas

---

## Solutions Index

| Lesson | File | Topics |
|--------|------|--------|
| 001 | `001-first-contact-solutions.md` | HTTP, curl, PLATO submission, health checks |
| 002 | `002-room-mapping-solutions.md` | MUD navigation, room mapping, stale state |
| 003 | `003-tile-submission-solutions.md` | PLATO tiles, batch submission, retry logic |
| 004 | `004-guard-fundamentals-solutions.md` | GUARD parsing, validation, bytecode, fleet evaluation |
| 005 | `005-ci-deployment-solutions.md` | *(Pending)* GitHub Actions, CI pipelines |
| 006 | `006-bottle-writing-solutions.md` | *(Pending)* I2I bottles, structured communication |
| 007 | `007-subagent-orchestration-solutions.md` | *(Pending)* Subagent spawning, baton passing |
| 008 | `008-cross-linking-solutions.md` | *(Pending)* Cross-repo linking, dependency mapping |
| 009 | `009-security-auditing-solutions.md` | *(Pending)* Security audits, vulnerability scanning |
| 010 | `010-fleet-orchestration-solutions.md` | *(Pending)* Service management, health monitoring |
| 011 | `011-service-healing-solutions.md` | *(Pending)* Auto-restart, log analysis, alerts |
| 012 | `012-repo-auditing-solutions.md` | *(Pending)* Git hygiene, commit analysis, linting |
| 013 | `013-fleet-command-solutions.md` | *(Pending)* Architecture decisions, strategy docs |

---

## How to Use

### For Self-Learners
1. Attempt the exercise at your chosen scaffolding level first
2. If stuck, read the corresponding solution
3. Run the verification command to confirm your implementation works
4. Try the extension ideas to deepen your understanding

### For Instructors
1. Use the solutions as reference when reviewing student work
2. Common mistakes section highlights what to watch for
3. Verification commands provide objective pass/fail criteria
4. Extension ideas offer advanced challenges for fast learners

---

## Verification

All solutions include verification commands. A solution is considered correct when:

1. **Level 1 (Recruit):** The script runs without errors and produces expected output
2. **Level 2 (Sailor):** The script handles edge cases (missing files, invalid input)
3. **Level 3 (Officer):** The code is modular, documented, and includes error handling

---

## Contributing

To add a new solution:
1. Create `LESSON-NUMBER-topic-solutions.md`
2. Follow the established format: Trials → Exercise (3 levels) → Verification → Instructor Notes
3. Include actual commands that can be copy-pasted and run
4. Test the verification commands before submitting

---

*CCC 🦀 | Fleet Curriculum Designer*
*2026-05-05*
