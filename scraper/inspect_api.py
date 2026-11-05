import re

content = open(r'C:\Users\suley\.gemini\antigravity\brain\10ce2834-b031-4861-a451-646b5d6f7b5c\.system_generated\steps\1868\content.md', 'r', encoding='utf-8').read()

apis = set(re.findall(r'"(/api/[^"]+)"', content))
print("APIs found:", apis)

# Look for fetch or axios or query endpoints
endpoints = set(re.findall(r'"(https?://[^"]+)"', content))
print("Sample http endpoints:")
for ep in endpoints:
    if any(k in ep for k in ['api', 'product', 'deal', 'yaniyo']):
        print(" ", ep)
