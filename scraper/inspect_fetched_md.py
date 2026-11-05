import re

with open(r'C:\Users\suley\.gemini\antigravity\brain\10ce2834-b031-4861-a451-646b5d6f7b5c\.system_generated\steps\3383\content.md', 'r', encoding='utf-8') as f:
    text = f.read()

matches = re.findall(r'(\d+(?:\.\d+)*,\d{2}\s*(?:TL|₺))', text)
print('TL matches:', matches)
p_boxes = re.findall(r'price["\'\:\s]+([0-9\.]+)', text, re.IGNORECASE)
print('Price regex matches:', p_boxes[:10])

# check reduxStore
idx = text.find('reduxStore')
print('reduxStore found?', idx != -1)
if idx != -1:
    print('Around reduxStore:', text[idx:idx+300])
