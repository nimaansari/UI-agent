#!/usr/bin/env python3
# run_all_desktop_tests.py
# Run all desktop control tests (DC.1 - DC.5)

import subprocess
import sys
import os

tests = [
    ("DC.1", "test_dc1_screenshot.py", "Screenshot Real Desktop"),
    ("DC.2", "test_dc2_click.py", "Mouse Click"),
    ("DC.3", "test_dc3_keyboard.py", "Keyboard Input"),
    ("DC.4", "test_dc4_open_app.py", "Open Desktop App"),
]

results = {}

print("\n" + "=" * 60)
print("UIAgent Desktop Control Test Suite")
print("=" * 60)

for code, script, name in tests:
    print(f"\n{'#' * 60}")
    print(f"RUNNING {code}: {name}")
    print(f"{'#' * 60}\n")

    script_path = os.path.join(os.path.dirname(__file__), script)
    
    if not os.path.exists(script_path):
        results[code] = ("⏭ SKIP", name)
        print(f"⏭ File not found: {script_path}\n")
        continue

    r = subprocess.run([sys.executable, script_path])
    results[code] = ("✅ PASS" if r.returncode == 0 else "❌ FAIL", name)
    print()

# Print summary
print("\n" + "=" * 60)
print("DESKTOP TEST RESULTS")
print("=" * 60)

passed = failed = skipped = 0
for code, (status, name) in results.items():
    print(f" {status} {code:<8} {name}")
    if "PASS" in status:
        passed += 1
    elif "SKIP" in status:
        skipped += 1
    else:
        failed += 1

print("=" * 60)
print(f" Passed  : {passed}")
print(f" Skipped : {skipped}")
print(f" Failed  : {failed}")
print("=" * 60)

if failed == 0 and passed > 0:
    print("\n✅ ALL DESKTOP TESTS PASSED")
    print(" UIAgent desktop control is production ready")
    sys.exit(0)
else:
    print("\n❌ SOME TESTS FAILED")
    sys.exit(1)
