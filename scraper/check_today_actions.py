import json

transcript_path = r'C:\Users\suley\.gemini\antigravity\brain\10ce2834-b031-4861-a451-646b5d6f7b5c\.system_generated\logs\transcript.jsonl'

with open(transcript_path, 'r', encoding='utf-8') as f:
    lines = [json.loads(line) for line in f]

print("Total lines:", len(lines))

today_entries = [e for e in lines if '2026-10-24' in e.get('created_at', '')]
print("Entries today (2026-10-24):", len(today_entries))

for i, e in enumerate(today_entries):
    t = e.get('type')
    ts = e.get('created_at')
    tool_calls = e.get('tool_calls')
    content = e.get('content', '')
    if t == 'USER_INPUT':
        print(f"\n[USER_INPUT] {ts}: {content[:100]}...")
    elif tool_calls:
        for tc in tool_calls:
            name = tc.get('name') or tc.get('function', {}).get('name')
            args = tc.get('args') or tc.get('function', {}).get('arguments')
            summary = tc.get('toolSummary') or (args.get('toolSummary') if isinstance(args, dict) else '')
            cmd = (args.get('CommandLine') if isinstance(args, dict) else '') or ''
            print(f"  [TOOL] {ts} - {name} ({summary}): {cmd[:80]}")
    elif t == 'PLANNER_RESPONSE' and content:
        # print first line
        first_line = content.split('\n')[0]
        print(f"[ASSISTANT RESPONSE] {ts}: {first_line[:80]}")
