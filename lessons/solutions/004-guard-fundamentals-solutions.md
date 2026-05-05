# Exercise Solutions — Lesson 004: Guard Fundamentals

**Author:** CCC 🦀  
**Date:** 2026-05-05  
**For:** Fleet instructors and self-learners

---

## Trial A — Parse a GUARD Declaration

**Prompt:**
> Write a Python function that extracts the guard name, type, and threshold from a GUARD declaration.

**Solution:**
```python
import re

def parse_guard(guard_text):
    """Parse a GUARD declaration and return its components."""
    pattern = r'GUARD\s+(\w+)\s*\{\s*(\w+)\s+(\w+)\s*<\s*(\d+)\s*;\s*\}'
    match = re.match(pattern, guard_text)
    
    if match:
        return {
            "name": match.group(1),
            "type": match.group(2),
            "variable": match.group(3),
            "threshold": int(match.group(4)),
        }
    return {"error": "Invalid GUARD syntax"}

# Test
guard = "GUARD altitude_safety { FLOAT altitude < 1000 ; }"
result = parse_guard(guard)
print(result)
```

**Expected output:**
```python
{'name': 'altitude_safety', 'type': 'FLOAT', 'variable': 'altitude', 'threshold': 1000}
```

---

## Trial B — Validate GUARD Syntax

**Prompt:**
> Write a Python function that checks if a GUARD declaration is syntactically valid.

**Solution:**
```python
import re

def validate_guard(guard_text):
    """Validate GUARD syntax. Returns (is_valid, error_message)."""
    # Check basic structure
    if not guard_text.startswith("GUARD"):
        return False, "GUARD declaration must start with 'GUARD'"
    
    if "{" not in guard_text or "}" not in guard_text:
        return False, "Missing braces { }"
    
    if ";" not in guard_text:
        return False, "Missing semicolon ;"
    
    # Check for valid type
    valid_types = ["FLOAT", "INT", "BOOL"]
    has_valid_type = any(t in guard_text for t in valid_types)
    if not has_valid_type:
        return False, f"Must declare one of: {', '.join(valid_types)}"
    
    # Check threshold is numeric
    threshold_match = re.search(r'<\s*(\d+)', guard_text)
    if not threshold_match:
        return False, "Must have numeric threshold (e.g., < 1000)"
    
    return True, "Valid"

# Tests
print(validate_guard("GUARD altitude_safety { FLOAT altitude < 1000 ; }"))
print(validate_guard("GUARD bad { altitude < 1000 ; }"))  # Missing type
```

**Expected output:**
```
(True, 'Valid')
(False, "Must declare one of: FLOAT, INT, BOOL")
```

---

## Trial C — Generate FLUX-C Bytecode

**Prompt:**
> Write a Python function that compiles a simple GUARD into FLUX-C bytecode instructions.

**Solution:**
```python
def compile_guard_to_bytecode(guard_name, var_name, threshold, guard_type="FLOAT"):
    """Compile a simple threshold GUARD into FLUX-C bytecode."""
    
    bytecode = []
    
    # Load variable
    if guard_type == "FLOAT":
        bytecode.append({"op": "LOAD", "addr": var_name, "comment": f"Load {var_name}"})
    else:
        bytecode.append({"op": "LOADB", "addr": var_name, "comment": f"Load {var_name}"})
    
    # Push threshold
    bytecode.append({"op": "PUSH", "value": threshold, "comment": f"Push threshold {threshold}"})
    
    # Compare
    bytecode.append({"op": "LT", "comment": "Check if var < threshold"})
    
    # Jump if true (violation) to FAIL
    bytecode.append({"op": "JZ", "offset": 2, "comment": "Skip if not violated"})
    
    # If violated: FAIL
    bytecode.append({"op": "FAIL", "code": "GUARD_VIOLATION", "comment": f"Guard {guard_name} violated"})
    
    # If not violated: HALT (pass)
    bytecode.append({"op": "HALT", "comment": "Guard passed"})
    
    return bytecode

# Test
bc = compile_guard_to_bytecode("altitude_safety", "altitude", 1000)
for i, instr in enumerate(bc):
    print(f"{i:02d}: {instr['op']:<8} ; {instr['comment']}")
```

**Expected output:**
```
00: LOAD     ; Load altitude
01: PUSH     ; Push threshold 1000
02: LT       ; Check if var < threshold
03: JZ       ; Skip if not violated
04: FAIL     ; Guard altitude_safety violated
05: HALT     ; Guard passed
```

---

## Trial D — Check Guard Against Data

**Prompt:**
> Write a function that evaluates a guard against actual sensor data.

**Solution:**
```python
def evaluate_guard(guard_spec, sensor_data):
    """Evaluate a guard against sensor data.
    
    guard_spec: dict with 'name', 'type', 'variable', 'threshold'
    sensor_data: dict of variable values
    """
    var_name = guard_spec["variable"]
    threshold = guard_spec["threshold"]
    
    if var_name not in sensor_data:
        return {"status": "ERROR", "reason": f"Missing variable: {var_name}"}
    
    value = sensor_data[var_name]
    
    # Type checking
    if guard_spec["type"] == "FLOAT" and not isinstance(value, (int, float)):
        return {"status": "ERROR", "reason": f"Expected float, got {type(value).__name__}"}
    
    # Evaluate condition
    if value < threshold:
        return {
            "status": "VIOLATION",
            "guard": guard_spec["name"],
            "value": value,
            "threshold": threshold,
            "message": f"{var_name} = {value} < {threshold}"
        }
    else:
        return {
            "status": "PASS",
            "guard": guard_spec["name"],
            "value": value,
            "threshold": threshold,
        }

# Test
sensor = {"altitude": 500, "temperature": 85}
guard = {"name": "altitude_safety", "type": "FLOAT", "variable": "altitude", "threshold": 1000}

result = evaluate_guard(guard, sensor)
print(result)

# Change to safe
sensor["altitude"] = 1200
result = evaluate_guard(guard, sensor)
print(result)
```

**Expected output:**
```python
{'status': 'VIOLATION', 'guard': 'altitude_safety', 'value': 500, 'threshold': 1000, 'message': 'altitude = 500 < 1000'}
{'status': 'PASS', 'guard': 'altitude_safety', 'value': 1200, 'threshold': 1000}
```

---

## Exercise: Scaffolding Level 1 (Recruit)

**Task:** Write a bash script that validates a GUARD declaration using basic string checks.

**Solution:**
```bash
#!/bin/bash
# validate-guard.sh

GUARD="$1"

if [ -z "$GUARD" ]; then
    echo "Usage: ./validate-guard.sh 'GUARD name { TYPE var < threshold ; }'"
    exit 1
fi

# Check starts with GUARD
if ! echo "$GUARD" | grep -q "^GUARD"; then
    echo "❌ Must start with 'GUARD'"
    exit 1
fi

# Check has braces
if ! echo "$GUARD" | grep -q "{"; then
    echo "❌ Missing opening brace"
    exit 1
fi

if ! echo "$GUARD" | grep -q "}"; then
    echo "❌ Missing closing brace"
    exit 1
fi

# Check has semicolon
if ! echo "$GUARD" | grep -q ";"; then
    echo "❌ Missing semicolon"
    exit 1
fi

# Check has valid type
if ! echo "$GUARD" | grep -qE "FLOAT|INT|BOOL"; then
    echo "❌ Must declare type: FLOAT, INT, or BOOL"
    exit 1
fi

# Check has comparison operator
if ! echo "$GUARD" | grep -q "<"; then
    echo "❌ Must have comparison operator <"
    exit 1
fi

# Check has numeric threshold
if ! echo "$GUARD" | grep -qE "<\s*[0-9]+"; then
    echo "❌ Must have numeric threshold (e.g., < 1000)"
    exit 1
fi

echo "✅ GUARD syntax is valid"
```

**Verification:**
```bash
chmod +x validate-guard.sh

# Valid
./validate-guard.sh 'GUARD altitude_safety { FLOAT altitude < 1000 ; }'
# Expected: ✅ GUARD syntax is valid

# Invalid
./validate-guard.sh 'GUARD bad { altitude < 1000 ; }'
# Expected: ❌ Must declare type: FLOAT, INT, or BOOL
```

---

## Exercise: Scaffolding Level 2 (Sailor)

**Task:** Create a Python script that reads a file of GUARD declarations and generates a report showing which ones are valid and which have errors.

**Solution:**
```python
#!/usr/bin/env python3
"""guard-audit.py — validate multiple GUARD declarations"""

import re
import sys

def validate_guard(guard_text):
    errors = []
    
    if not guard_text.startswith("GUARD"):
        errors.append("Must start with 'GUARD'")
    
    if "{" not in guard_text or "}" not in guard_text:
        errors.append("Missing braces")
    
    if ";" not in guard_text:
        errors.append("Missing semicolon")
    
    if not re.search(r"FLOAT|INT|BOOL", guard_text):
        errors.append("Must declare type (FLOAT/INT/BOOL)")
    
    if not re.search(r"<\s*\d+", guard_text):
        errors.append("Must have numeric threshold")
    
    name_match = re.search(r"GUARD\s+(\w+)", guard_text)
    name = name_match.group(1) if name_match else "unknown"
    
    return {
        "name": name,
        "valid": len(errors) == 0,
        "errors": errors,
        "text": guard_text,
    }

def audit_guards(filename):
    with open(filename) as f:
        guards = [line.strip() for line in f if line.strip()]
    
    print(f"Auditing {len(guards)} GUARD declarations...")
    print("=" * 50)
    
    valid_count = 0
    invalid_count = 0
    
    for guard_text in guards:
        result = validate_guard(guard_text)
        status = "✅" if result["valid"] else "❌"
        
        print(f"{status} {result['name']:<20} {', '.join(result['errors']) if result['errors'] else 'OK'}")
        
        if result["valid"]:
            valid_count += 1
        else:
            invalid_count += 1
    
    print("=" * 50)
    print(f"Results: {valid_count} valid, {invalid_count} invalid")
    return valid_count, invalid_count

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 guard-audit.py guards.txt")
        sys.exit(1)
    
    audit_guards(sys.argv[1])
```

**Sample guards.txt:**
```
GUARD altitude_safety { FLOAT altitude < 1000 ; }
GUARD temperature_limit { INT temperature < 85 ; }
GUARD bad_guard { altitude < 1000 ; }
GUARD speed_check { FLOAT velocity < 500 ; }
GUARD incomplete { FLOAT pressure < 50 }
```

**Verification:**
```bash
python3 guard-audit.py guards.txt
# Expected:
# Auditing 5 GUARD declarations...
# ==================================================
# ✅ altitude_safety      OK
# ✅ temperature_limit   OK
# ❌ bad_guard            Must declare type (FLOAT/INT/BOOL)
# ✅ speed_check          OK
# ❌ incomplete           Missing semicolon, Must have numeric threshold
# ==================================================
# Results: 3 valid, 2 invalid
```

---

## Exercise: Scaffolding Level 3 (Officer)

**Task:** Build a Python class that manages a fleet of guards, evaluates them against live sensor data, and generates violation reports.

**Solution:**
```python
#!/usr/bin/env python3
"""guard-fleet.py — fleet-level guard management"""

import json
import re
from datetime import datetime

class GuardFleet:
    def __init__(self, name="default-fleet"):
        self.name = name
        self.guards = {}
        self.violations = []
    
    def add_guard(self, guard_text):
        """Parse and add a GUARD declaration."""
        pattern = r'GUARD\s+(\w+)\s*\{\s*(\w+)\s+(\w+)\s*\u003c\s*(\d+)\s*;\s*\}'
        match = re.match(pattern, guard_text)
        
        if not match:
            raise ValueError(f"Invalid GUARD syntax: {guard_text}")
        
        name, gtype, variable, threshold = match.groups()
        
        self.guards[name] = {
            "name": name,
            "type": gtype,
            "variable": variable,
            "threshold": int(threshold),
            "declaration": guard_text,
        }
        
        return name
    
    def evaluate(self, sensor_data):
        """Evaluate all guards against sensor data."""
        results = []
        
        for name, guard in self.guards.items():
            var = guard["variable"]
            threshold = guard["threshold"]
            
            if var not in sensor_data:
                result = {
                    "guard": name,
                    "status": "ERROR",
                    "reason": f"Missing sensor: {var}",
                }
            elif sensor_data[var] < threshold:
                result = {
                    "guard": name,
                    "status": "VIOLATION",
                    "value": sensor_data[var],
                    "threshold": threshold,
                    "timestamp": datetime.now().isoformat(),
                }
                self.violations.append(result)
            else:
                result = {
                    "guard": name,
                    "status": "PASS",
                    "value": sensor_data[var],
                    "threshold": threshold,
                }
            
            results.append(result)
        
        return results
    
    def report(self):
        """Generate a fleet status report."""
        total = len(self.guards)
        violations = len([v for v in self.violations if v["status"] == "VIOLATION"])
        
        return {
            "fleet": self.name,
            "guards": total,
            "total_violations": violations,
            "guards_detail": self.guards,
            "recent_violations": self.violations[-10:],  # Last 10
        }
    
    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.report(), f, indent=2)
    
    @classmethod
    def load(cls, filename):
        with open(filename) as f:
            data = json.load(f)
        
        fleet = cls(data["fleet"])
        # Guards would need to be reparsed from declarations
        return fleet

# Usage
if __name__ == '__main__':
    fleet = GuardFleet("eVTOL-safety")
    
    # Add guards
    fleet.add_guard("GUARD altitude_safety { FLOAT altitude < 1000 ; }")
    fleet.add_guard("GUARD temperature_limit { INT temperature < 85 ; }")
    fleet.add_guard("GUARD speed_check { FLOAT velocity < 500 ; }")
    
    # Simulate safe flight
    print("=== Safe Flight ===")
    results = fleet.evaluate({
        "altitude": 1200,
        "temperature": 70,
        "velocity": 450,
    })
    for r in results:
        print(f"  {r['guard']:<20} {r['status']}")
    
    # Simulate emergency
    print("\n=== Emergency ===")
    results = fleet.evaluate({
        "altitude": 500,      # Too low!
        "temperature": 95,   # Overheating!
        "velocity": 450,
    })
    for r in results:
        print(f"  {r['guard']:<20} {r['status']}")
    
    # Report
    print("\n=== Fleet Report ===")
    report = fleet.report()
    print(f"Guards: {report['guards']}")
    print(f"Total violations: {report['total_violations']}")
    
    # Save
    fleet.save("guard-fleet-report.json")
    print("Saved to guard-fleet-report.json")
```

**Verification:**
```bash
python3 guard-fleet.py
# Expected:
# === Safe Flight ===
#   altitude_safety        PASS
#   temperature_limit      PASS
#   speed_check            PASS
#
# === Emergency ===
#   altitude_safety        VIOLATION
#   temperature_limit      VIOLATION
#   speed_check            PASS
#
# === Fleet Report ===
# Guards: 3
# Total violations: 2
# Saved to guard-fleet-report.json
```

---

## Instructor Notes

### Common Mistakes

1. **Missing type declaration:** `GUARD g { var < 100 ; }` — must specify FLOAT, INT, or BOOL
2. **Forgetting semicolon:** `GUARD g { FLOAT var < 100 }` — missing `;`
3. **Wrong comparison:** `GUARD g { FLOAT var > 100 ; }` — GUARD uses `<` (upper bound)
4. **Numeric threshold:** `GUARD g { FLOAT var < MAX ; }` — threshold must be a number

### Extension Ideas

- Add support for `>` (lower bound) guards
- Implement `AND`/`OR` composite guards
- Add time-based guards (e.g., `GUARD battery { FLOAT voltage < 20 FOR 30s ; }`)
- Build a web dashboard showing guard status in real-time
- Integrate with actual sensor feeds via MQTT or WebSocket

---

*CCC 🦀 | Fleet Curriculum Designer*
*2026-05-05*
