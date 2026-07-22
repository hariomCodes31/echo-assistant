import os
import sys

# Add root directory to python path
sys.path.insert(0, os.path.abspath('.'))

modules_to_test = []
for r, d, files in os.walk('.'):
    d[:] = [dirname for dirname in d if dirname not in ('.venv', '.git', '__pycache__', 'scratch')]
    for f in files:
        if f.endswith('.py') and f != 'app.py' and not f.startswith('test_'):
            filepath = os.path.join(r, f)
            # convert filepath to module name
            mod_name = filepath.replace('.\\', '').replace('\\', '.').replace('.py', '')
            modules_to_test.append((filepath, mod_name))

print(f"Found {len(modules_to_test)} modules to test import.")

failed = 0
for filepath, mod in modules_to_test:
    try:
        __import__(mod)
        print(f"SUCCESS: {mod} imported successfully.")
    except Exception as e:
        print(f"FAILED: {mod} ({filepath}) failed to import: {type(e).__name__}: {e}")
        failed += 1

if failed:
    print(f"\nTotal failures: {failed}")
    sys.exit(1)
else:
    print("\nAll modules imported successfully.")
