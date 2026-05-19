import os, re

html_path = r'C:\Users\33145\WorkBuddy\Claw\valorant-shooter\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

print(f"Original size: {len(html)} chars")

# === PROBLEM 1: Remove duplicate AGENT_B64 + agentImages blocks ===
# Keep only the FIRST occurrence, remove subsequent duplicates

# Pattern: "const AGENT_B64 = {" ... "};" followed by optional agentImages preload ... then another "const AGENT_B64"
# Strategy: find ALL occurrences, keep first, delete rest

# Find positions of each "const AGENT_B64 = {" occurrence
pattern_start = r'const AGENT_B64 = \{'
positions = [m.start() for m in re.finditer(pattern_start, html)]
print(f"Found {len(positions)} AGENT_B64 declarations at positions: {positions}")

if len(positions) > 1:
    # Keep everything before the second occurrence
    # But we need to also include the first complete block (AGENT_B64 + agentImages) + what follows up to the next AGENT_B64
    
    # Find end of first agentImages block (the one right after first AGENT_B64)
    # First, find where the first agentImages block ends
    first_b64_end = html.find('};', positions[0])
    # Find the matching closing - need to count braces... simpler approach:
    
    # Find "// ── Character Definitions" after the last duplicate
    chars_marker = '// \u00a4\u00a4\u00a4 Character Definitions'
    
    # Actually let's use a different approach: find the LAST AGENT_B64 block's end,
    # then find the CHARS marker after it
    
    # Get position of the CHARS definition that comes AFTER all duplicates
    # Search for "const CHARS = {" which appears after the last duplicate
    chars_pos = html.find('const CHARS = {')
    print(f"CHARS found at: {chars_pos}")
    
    # Find the text between the END of the first complete block and CHARS
    # The first block is: AGENT_B64 {...}; + agentImages {...}
    # We want to keep from start to end_of_first_block, then skip to CHARS
    
    # Let's find the end of the first agentImages preload block
    # It ends with "}\n\n// ── Character Definitions" in the ORIGINAL intended structure
    # But now there are duplicates between them
    
    # Simpler approach: extract content in segments
    # Segment 1: from start to just BEFORE the second AGENT_B64
    # Segment 2: from CHARS marker to end
    
    pos2 = positions[1]  # Start of 2nd AGENT_B64 (first duplicate)
    
    # Now we need to find where the LAST duplicate block ends and CHARS begins
    # Look for "const CHARS = {" after the last AGENT_B64
    last_pos = positions[-1]
    chars_after_last = html.find('const CHARS = {', last_pos)
    
    # Build cleaned HTML: [start..pos2) + [chars_after_last..end]
    # But wait - we also need to make sure the first block has agentImages correctly
    prefix = html[:pos2].rstrip()
    suffix = html[chars_after_last:]
    
    cleaned = prefix + '\n\n' + suffix
else:
    cleaned = html

print(f"After dedup size: {len(cleaned)} chars")

# === PROBLEM 2: Fix triple imgKey ===
# Pattern: imgKey: 'jett', imgKey: 'jett', imgKey: 'jett',
def fix_triple_imgkey(text):
    for name in ['jett', 'reyna', 'omen', 'kayo']:
        triple = f"imgKey: '{name}', imgKey: '{name}', imgKey: '{name}',"
        double = f"imgKey: '{name}', imgKey: '{name}',"
        single = f"imgKey: '{name}',"
        if triple in text:
            text = text.replace(triple, single)
            print(f"  Fixed triple imgKey for {name}")
        elif double in text:
            text = text.replace(double, single)
            print(f"  Fixed double imgKey for {name}")
    return text

cleaned = fix_triple_imgkey(cleaned)

# Verify no more duplicates
remaining = len(re.findall(r'const AGENT_B64 = \{', cleaned))
print(f"Remaining AGENT_B64 declarations: {remaining}")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(cleaned)

print(f"Final size: {os.path.getsize(html_path)} bytes")
print("DONE!")
