from patch import edit, run

L = 'part_logic.js'

# --- two more zones, and an explicit decor style per zone ---------------------
edit(L, """const ZONES = [
  { id: 0, name: 'The Crypts', tint: null, amb: '#f0a23c', boss: 'Count Hollow', bcol: '#8d93a8' },
  { id: 1, name: 'The Drowned Halls', tint: 'rgba(40,120,160,.17)', amb: '#5fc4e8', boss: 'The Drowned Count', bcol: '#4fa3b8' },
  { id: 2, name: 'Mossroot Caverns', tint: 'rgba(70,130,50,.16)', amb: '#9bd16a', boss: 'The Mossroot Count', bcol: '#7aa05a' },
  { id: 3, name: 'The Cinder Vaults', tint: 'rgba(190,70,20,.17)', amb: '#ff7a3a', boss: 'The Cinder Count', bcol: '#c2563f' }
];""", """const ZONES = [
  { id: 0, name: 'The Crypts', dec: 0, tint: null, amb: '#f0a23c', boss: 'Count Hollow', bcol: '#8d93a8' },
  { id: 1, name: 'The Drowned Halls', dec: 1, tint: 'rgba(40,120,160,.17)', amb: '#5fc4e8', boss: 'The Drowned Count', bcol: '#4fa3b8' },
  { id: 2, name: 'Mossroot Caverns', dec: 2, tint: 'rgba(70,130,50,.16)', amb: '#9bd16a', boss: 'The Mossroot Count', bcol: '#7aa05a' },
  { id: 3, name: 'The Cinder Vaults', dec: 3, tint: 'rgba(190,70,20,.17)', amb: '#ff7a3a', boss: 'The Cinder Count', bcol: '#c2563f' },
  { id: 4, name: 'The Bone Gardens', dec: 4, tint: 'rgba(150,140,110,.13)', amb: '#e8dfc0', boss: 'The Pale Count', bcol: '#d8d2bd' },
  { id: 5, name: 'The Obsidian Reach', dec: 5, tint: 'rgba(92,58,150,.18)', amb: '#b98cff', boss: 'The Obsidian Count', bcol: '#8a6bd6' }
];""")

# --- prop pools for the new zones --------------------------------------------
edit(L, """   ['p_cauldron', 10, 1.15, 2], ['p_anvil', 8, 1.25, 2], ['p_weaponstand', 10, 1.0, 2], ['p_dummy', 9, 1.0, 1], ['p_workbench', 12, 1.0, 1], ['rts_gold2', 12, 1.0, 2], ['p_candlestick', 5, 1.2, 1, 70], ['r_column_square', 9, 1.1, 1], ['p_sword', 0, 1.5, 1], ['p_shield', 0, 1.4, 1]]
];""", """   ['p_cauldron', 10, 1.15, 2], ['p_anvil', 8, 1.25, 2], ['p_weaponstand', 10, 1.0, 2], ['p_dummy', 9, 1.0, 1], ['p_workbench', 12, 1.0, 1], ['rts_gold2', 12, 1.0, 2], ['p_candlestick', 5, 1.2, 1, 70], ['r_column_square', 9, 1.1, 1], ['p_sword', 0, 1.5, 1], ['p_shield', 0, 1.4, 1]],
  [['grave_round', 8, 1.5, 3], ['grave_cross', 8, 1.5, 3], ['grave_broken', 0, 1.5, 2], ['grave_bevel', 7, 1.5, 2], ['coffin', 0, 1.3, 2], ['cross', 7, 1.3, 2], ['r_skull', 0, 1.8, 3], ['candles', 0, 1.7, 2, 56],
   ['urn', 5, 1.6, 2], ['altar', 14, 1.1, 1], ['r_statue_stag', 10, 1.15, 1], ['r_bricks', 0, 1.3, 2], ['p_bookstand', 6, 1.2, 1], ['rocks', 12, 1.1, 1], ['r_column_round', 9, 1.1, 2], ['p_pouch', 0, 1.4, 1]],
  [['r_column_square', 9, 1.1, 3], ['pillar', 5, 1.5, 2], ['brazier', 8, 1.6, 2, 120], ['p_cauldron', 10, 1.15, 2], ['altar', 14, 1.1, 2], ['r_skull', 0, 1.8, 2], ['p_candlestick', 5, 1.2, 2, 70],
   ['p_bookcase', 12, 1.0, 1], ['p_books', 0, 1.3, 1], ['p_scroll', 0, 1.4, 1], ['r_statue_fox', 10, 1.15, 1], ['rts_gold2', 12, 1.0, 1], ['p_chalice', 0, 1.5, 1], ['r_pot2', 7, 1.3, 2], ['trap', 0, 1.2, 1]]
];""")

# --- colour grades per zone ---------------------------------------------------
edit(L, """const FGRADE = ['#a4aecb', '#8fc0d2', '#adc48e', '#d49c80'], WGRADE = ['#7d88a8', '#6898b2', '#88a068', '#b07a60'];""",
     """const FGRADE = ['#a4aecb', '#8fc0d2', '#adc48e', '#d49c80', '#cfc7a8', '#a99ad0'], WGRADE = ['#7d88a8', '#6898b2', '#88a068', '#b07a60', '#a89f84', '#8276b0'];""")

# --- decor switches on dec, not id, and the new zones get their own litter ----
edit(L, """  const t = G.map[ty * MW + tx], px = tx * T, py = ty * T, Zn = G.zone || ZONES[0], zn = Zn.id;""",
     """  const t = G.map[ty * MW + tx], px = tx * T, py = ty * T, Zn = G.zone || ZONES[0], zn = Zn.dec != null ? Zn.dec : Zn.id;""")

edit(L, """      if (zn === 3 && hr(tx, ty, 84) < .25) { b.fillStyle = 'rgba(255,120,50,.55)'; b.fillRect(px + 5 + hr(tx, ty, 85) * 20, py + T - 10, 6, 1.5); }""",
     """      if (zn === 3 && hr(tx, ty, 84) < .25) { b.fillStyle = 'rgba(255,120,50,.55)'; b.fillRect(px + 5 + hr(tx, ty, 85) * 20, py + T - 10, 6, 1.5); }
      if (zn === 5 && hr(tx, ty, 86) < .3) { b.fillStyle = 'rgba(185,140,255,.5)'; for (let i = 0; i < 2; i++) { const gx = px + 7 + hr(tx, ty, 87 + i) * 18, gy = py + T - 13; b.beginPath(); b.moveTo(gx - 2, gy); b.lineTo(gx, gy + 7 + hr(tx, ty, 89 + i) * 5); b.lineTo(gx + 2, gy); b.fill(); } }""")

edit(L, """    for (const [w, col] of [[4, 'rgba(255,110,40,.22)'], [1.4, '#ff8a3a']]) { b.strokeStyle = col; b.lineWidth = w; b.beginPath(); pts.forEach((p, i) => i ? b.lineTo(p[0], p[1]) : b.moveTo(p[0], p[1])); b.stroke(); }
  }""", """    for (const [w, col] of [[4, 'rgba(255,110,40,.22)'], [1.4, '#ff8a3a']]) { b.strokeStyle = col; b.lineWidth = w; b.beginPath(); pts.forEach((p, i) => i ? b.lineTo(p[0], p[1]) : b.moveTo(p[0], p[1])); b.stroke(); }
  } else if (zn === 4 && r5 < .22) {
    b.fillStyle = 'rgba(226,218,190,.38)';
    for (let i = 0; i < 3; i++) { const sx2 = cx + (hr(tx, ty, 130 + i) - .5) * 17, sy2 = cy + (hr(tx, ty, 134 + i) - .5) * 12; b.fillRect(sx2, sy2, 5 + hr(tx, ty, 138 + i) * 6, 1.7); }
    if (r6 < .4) { b.beginPath(); b.arc(cx + 4, cy + 3, 2.6, 0, TAU); b.fill(); b.fillStyle = '#12151c'; b.fillRect(cx + 2.8, cy + 2.2, 1.1, 1.4); b.fillRect(cx + 4.8, cy + 2.2, 1.1, 1.4); }
  } else if (zn === 5 && r5 < .2) {
    for (let i = 0; i < 3; i++) {
      const gx = cx + (hr(tx, ty, 140 + i) - .5) * 15, gy = cy + (hr(tx, ty, 144 + i) - .5) * 11, gh = 4 + hr(tx, ty, 148 + i) * 7;
      b.fillStyle = 'rgba(150,110,220,.42)'; b.beginPath(); b.moveTo(gx - 2.3, gy + 1); b.lineTo(gx, gy - gh); b.lineTo(gx + 2.3, gy + 1); b.fill();
      b.fillStyle = 'rgba(214,190,255,.5)'; b.beginPath(); b.moveTo(gx - .7, gy + 1); b.lineTo(gx, gy - gh); b.lineTo(gx + .8, gy + 1); b.fill();
    }
  }""")

run()
