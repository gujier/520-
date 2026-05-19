import os, re

html_path = r'C:\Users\33145\WorkBuddy\Claw\valorant-shooter\index.html'
assets_dir = r'C:\Users\33145\WorkBuddy\Claw\valorant-shooter\assets'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Read all 4 b64 strings
b64_map = {}
for name in ['jett', 'reyna', 'omen', 'kayo']:
    b64_path = os.path.join(assets_dir, f'{name}.b64.txt')
    with open(b64_path, 'r', encoding='utf-8') as f:
        raw = f.read().strip()
        # Remove BOM if present
        if raw.startswith('\ufeff'):
            raw = raw[1:]
        b64_map[name] = raw
    print(f"  {name}: {len(b64_map[name])} chars")

# 2. Build AGENT_B64 JS block + preload code
b64_lines = ['const AGENT_B64 = {']
for k, v in b64_map.items():
    b64_lines.append(f"  {k}: 'data:image/png;base64,{v}',")
b64_lines.append('};')
# Add agentImages preload right after
b64_lines.append('')
b64_lines.append('// Preload agent images from base64')
b64_lines.append('const agentImages = {};')
b64_lines.append('for (const [key, src] of Object.entries(AGENT_B64)) {')
b64_lines.append('  const img = new Image();')
b64_lines.append('  img.src = src;')
b64_lines.append('  agentImages[key] = img;')
b64_lines.append('}')
b64_block = '\n'.join(b64_lines)

print(f"B64 block size: {len(b64_block)} chars")

# Insert before Character Definitions
marker = '// ── Character Definitions ─────────────'
if marker in html:
    html = html.replace(marker, b64_block + '\n\n' + marker)
    print("Step 1: AGENT_B64 inserted OK")
else:
    print("ERROR: Marker not found!")

# 3. Add imgKey to CHARS using regex (safer than exact emoji match)
html = html.replace(
    "name: '捷风', emoji: '\U0001f32a\ufe0f', color: '#88c9ff',",
    "name: '捷风', emoji: '\U0001f32a\ufe0f', color: '#88c9ff', imgKey: 'jett',"
)
html = html.replace(
    "name: '芮娜', emoji: '\U0001f49c', color: '#c084fc',",
    "name: '芮娜', emoji: '\U0001f49c', color: '#c084fc', imgKey: 'reyna',"
)
html = html.replace(
    "name: '黑梦', emoji: '\U0001f319', color: '#475569',",
    "name: '黑梦', emoji: '\U0001f319', color: '#475569', imgKey: 'omen',"
)
html = html.replace(
    "name: 'KO', emoji: '\U0001f52a', color: '#f43f5e',",
    "name: 'KO', emoji: '\U0001f52a', color: '#f43f5e', imgKey: 'kayo',"
)
print("Step 2: imgKey added to CHARS")

# 4. Replace player draw emoji with drawImage
old_draw = '''    // Character emoji
    ctx.shadowBlur = 0;
    ctx.font = '18px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(this.char.emoji, this.x, this.y);'''

new_draw = '''    // Character portrait image
    if (this.char.imgKey && agentImages[this.char.imgKey]) {
      const img = agentImages[this.char.imgKey];
      const sz = 28;
      ctx.drawImage(img, this.x - sz/2, this.y - sz/2 - 4, sz, sz);
    } else {
      ctx.shadowBlur = 0;
      ctx.font = '18px Arial';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(this.char.emoji, this.x, this.y);
    }'''

if old_draw in html:
    html = html.replace(old_draw, new_draw)
    print("Step 3: Player drawImage replacement OK")
else:
    print("ERROR: Player draw block not found!")
    # Try to find what's actually there
    idx = html.find('// Character emoji')
    if idx >= 0:
        print(f"Found at index {idx}: ...{html[idx:idx+200]}...")

# 5. Replace char-select avatars with img tags
# Use regex to find char-avatar divs by their content pattern
def replace_char_avatar(html, emoji_char, name, b64_key):
    # The pattern is <div class="char-avatar">EMOJI</div>
    # We need to find each unique one
    old_tag = f'<div class="char-avatar">{emoji_char}</div>'
    new_tag = f'<div class="char-avatar"><img src="data:image/png;base64,{b64_map[b64_key]}" alt="{name}"></div>'
    if old_tag in html:
        html = html.replace(old_tag, new_tag)
        print(f"Step 4: {name} avatar replaced OK")
    else:
        print(f"Step 4: {name} avatar NOT found! Searching...")
        # Debug: find char-avatar occurrences
        for m in re.finditer(r'class="char-avatar"[^>]*>([^<]+)</div>', html):
            print(f"  Found: {m.group(0)[:80]}")
    return html

html = replace_char_avatar(html, '\U0001f32a\ufe0f', '捷风', 'jett')
html = replace_char_avatar(html, '\U0001f49c', '芮娜', 'reyna')
html = replace_char_avatar(html, '\U0001f319', '黑梦', 'omen')
html = replace_char_avatar(html, '\U0001f52a', 'KO', 'kayo')

# 6. Add CSS for char-avatar images
css_addition = '''
  .char-avatar img {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    object-fit: cover;
  }'''
# Insert before </style>
if '</style>' in html:
    html = html.replace('</style>', css_addition + '\n</style>')
    print("Step 5: Avatar CSS added OK")
else:
    print("ERROR: </style> not found!")

# Write output
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

final_size = os.path.getsize(html_path)
print(f"\nDone! Final file size: {final_size} bytes ({final_size/1024:.1f} KB)")
