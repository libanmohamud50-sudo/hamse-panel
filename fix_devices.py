import re

with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Beddel max_dev shuruud
code = code.replace(
    'if max_dev > 1:',
    'if max_dev >= 1:'
)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(code)

print("fixed")

import subprocess
r = subprocess.run(["grep", "-n", "max_dev", "app.py"], capture_output=True, text=True)
print(r.stdout)
