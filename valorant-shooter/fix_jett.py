import re

html_path = r'C:\Users\33145\WorkBuddy\Claw\valorant-shooter\index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

print(f"Original size: {len(html)} chars")

# ============================================================
# STEP 1: Add mousePos tracking variable
# Find "let state = 'menu';" and add mousePos after it
# ============================================================
pattern_state = r"(let state = 'menu';)"
replacement_state = r"\1\nlet mousePos = {x: W/2, y: H/2};  // 始终跟踪鼠标位置"
if re.search(pattern_state, html):
    html = re.sub(pattern_state, replacement_state, html)
    print("Step 1: mousePos variable added")
else:
    print("WARNING: 'let state = 'menu'' not found!")

# ============================================================
# STEP 2: Add mousemove event listener
# Find the keydown event listener and add mousemove after all event listeners
# Actually, let's add it before the first addEventListener
# ============================================================
mousemove_handler = """
// 始终跟踪鼠标位置（用于捷风技能方向）
canvas.addEventListener('mousemove', e => {
  const rect = canvas.getBoundingClientRect();
  mousePos.x = (e.clientX - rect.left) * (W / rect.width);
  mousePos.y = (e.clientY - rect.top) * (H / rect.height);
});
"""

# Insert before the first addEventListener
pattern_first_listener = r"(addEventListener\('keydown')"
if re.search(pattern_first_listener, html):
    html = re.sub(pattern_first_listener, mousemove_handler + r"\1", html)
    print("Step 2: mousemove event listener added")
else:
    print("WARNING: keydown addEventListener not found!")

# ============================================================
# STEP 3: Rewrite Jett skill in activateSkill()
# Replace the ENTIRE jett case block
# ============================================================

old_jett_skill = """    case 'jett': {
      // 捷风：烟痕冲刺（修复版：独立计时器，烟痕一次生成）
      lastDashX = player.x;
      lastDashY = player.y;

      let dx = 0, dy = -1;
      if (touch.active && player) {
        const tdx = touch.x - player.x;
        const tdy = touch.y - player.y;
        const dist = Math.sqrt(tdx*tdx + tdy*tdy);
        if (dist > 5) { dx = tdx/dist; dy = tdy/dist; }
      } else if (keys['ArrowLeft'] || keys['KeyA']) { dx = -1; dy = 0; }
      else if (keys['ArrowRight'] || keys['KeyD']) { dx = 1; dy = 0; }
      else if (keys['ArrowUp'] || keys['KeyW']) { dx = 0; dy = -1; }
      else if (keys['ArrowDown'] || keys['KeyS']) { dx = 0; dy = 1; }

      // 瞬间位移
      player.x += dx * 120;
      player.y += dy * 120;
      player.x = Math.max(20, Math.min(W - 20, player.x));
      player.y = Math.max(40, Math.min(H - 40, player.y));

      // 沿冲刺路径一次性生成所有烟痕粒子
      for (let i = 0; i < 22; i++) {
        const t = i / 22;
        jettDashes.push({
          x: lastDashX + (player.x - lastDashX) * t + (Math.random()-0.5)*18,
          y: lastDashY + (player.y - lastDashY) * t + (Math.random()-0.5)*18,
          life: 30 + Math.random()*25,
          maxLife: 55,
          r: 8 + Math.random()*22
        });
        if (jettDashes.length > JETT_DASH_MAX) jettDashes.shift();
      }

      // 冲刺后在原地冒几帧余烟
      jettDashFrames = 10;
      player.dashing = true;
      player.dashTimer = 10;
      SFX.killJett();
      break;
    }"""

new_jett_skill = """    case 'jett': {
      // 捷风：烟痕冲刺 —— 向鼠标或键盘方向冲刺固定距离
      lastDashX = player.x;
      lastDashY = player.y;

      // 方向：键盘优先，鼠标其次，默认向上
      let dx = 0, dy = 0;
      if (keys['ArrowLeft']  || keys['KeyA']) dx -= 1;
      if (keys['ArrowRight'] || keys['KeyD']) dx += 1;
      if (keys['ArrowUp']    || keys['KeyW']) dy -= 1;
      if (keys['ArrowDown']  || keys['KeyS']) dy += 1;

      // 键盘无输入时，朝鼠标位置冲刺
      if (dx === 0 && dy === 0) {
        const tdx = mousePos.x - player.x;
        const tdy = mousePos.y - player.y;
        const dist = Math.sqrt(tdx*tdx + tdy*tdy);
        if (dist > 5) { dx = tdx/dist; dy = tdy/dist; }
      }

      // 兜底：仍无方向则向上
      if (dx === 0 && dy === 0) { dy = -1; }

      // 冲刺！固定距离 150px
      const DASH = 150;
      player.x += dx * DASH;
      player.y += dy * DASH;
      player.x = Math.max(20, Math.min(W - 20, player.x));
      player.y = Math.max(40, Math.min(H - 40, player.y));

      // 沿路径生成烟痕粒子
      for (let i = 0; i < 22; i++) {
        const t = i / 22;
        jettDashes.push({
          x: lastDashX + (player.x - lastDashX) * t + (Math.random()-0.5)*18,
          y: lastDashY + (player.y - lastDashY) * t + (Math.random()-0.5)*18,
          life: 30 + Math.random()*25,
          maxLife: 55,
          r: 8 + Math.random()*22
        });
        if (jettDashes.length > JETT_DASH_MAX) jettDashes.shift();
      }

      jettDashFrames = 10;
      SFX.killJett();
      break;
    }"""

if old_jett_skill in html:
    html = html.replace(old_jett_skill, new_jett_skill)
    print("Step 3: Jett skill rewritten")
else:
    print("WARNING: Old Jett skill block not found! Trying regex...")
    # Try regex approach - the code might have slight differences
    # Let's find the Jett case by pattern
    pattern_jett = r"case 'jett': \{[^}]*break;\s*\}"
    match = re.search(pattern_jett, html, re.DOTALL)
    if match:
        print(f"Found Jett case at position {match.start()}")
        print(f"Content: {match.group()[:200]}...")
    else:
        print("ERROR: Cannot find Jett case at all!")

# ============================================================
# STEP 4: Also fix touch.x/y to use mousePos when touch is not active
# (The touch object is updated on mousedown/touchstart)
# We already handle this in the new Jett skill (uses mousePos)
# ============================================================
# Also need to update touch object on mousemove? 
# Actually we added mousePos, and the Jett skill uses mousePos.
# But we should also update touch.x/y on mousemove for consistency.
# Let's update the mousemove handler to also set touch.x/y:
# (This is optional but good for consistency)

# ============================================================
# Write output
# ============================================================
with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

final_size = len(html)
print(f"\nFinal size: {final_size} chars ({final_size//1024} KB)")
print("DONE!")
