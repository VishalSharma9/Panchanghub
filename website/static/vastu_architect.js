/**
 * Interactive Visual House (Square / Rectangle) & Outer-Lot Vastu Architect Studio
 * Supports unlimited multi-instance indoor rooms & outdoor lot items, drag-and-drop,
 * resizing, door/gate facing direction arrows, compass rotation, and instant Vastu +
 * Birth-Chart evaluation via /api/vastu/analyze-layout.
 */
(function () {
  const CATALOG = {
    // Indoor Rooms
    entrance:       { label: "Main Entrance", icon: "🚪", scope: "indoor", w: 12, h: 7,  hasDoor: true,  defaultDoor: "NE", bg: "#fef3c7", border: "#d97706" },
    back_door:      { label: "Back Door",     icon: "🚪", scope: "indoor", w: 10, h: 6,  hasDoor: true,  defaultDoor: "NW", bg: "#f1f5f9", border: "#64748b" },
    master_bedroom: { label: "Master Bedroom",icon: "🛏️", scope: "indoor", w: 20, h: 17, hasDoor: true,  defaultDoor: "N",  bg: "#ede9fe", border: "#7c3aed" },
    bedroom:        { label: "Bedroom",       icon: "🛌", scope: "indoor", w: 17, h: 15, hasDoor: true,  defaultDoor: "E",  bg: "#e0e7ff", border: "#4f46e5" },
    guest_room:     { label: "Guest Room",    icon: "🛋️", scope: "indoor", w: 16, h: 14, hasDoor: true,  defaultDoor: "E",  bg: "#fae8ff", border: "#a21caf" },
    living_room:    { label: "Living Room",   icon: "📺", scope: "indoor", w: 22, h: 18, hasDoor: false, defaultDoor: "",   bg: "#e0f2fe", border: "#0284c7" },
    kitchen:        { label: "Kitchen",       icon: "🍳", scope: "indoor", w: 17, h: 15, hasDoor: true,  defaultDoor: "E",  bg: "#ffedd5", border: "#ea580c" },
    bathroom:       { label: "Bathroom",      icon: "🚿", scope: "indoor", w: 11, h: 11, hasDoor: true,  defaultDoor: "E",  bg: "#cffafe", border: "#0891b2" },
    storage:        { label: "Storage",       icon: "📦", scope: "indoor", w: 12, h: 11, hasDoor: false, defaultDoor: "",   bg: "#f3f4f6", border: "#4b5563" },
    balcony:        { label: "Balcony",       icon: "🌤️", scope: "indoor", w: 15, h: 7,  hasDoor: true,  defaultDoor: "N",  bg: "#ecfccb", border: "#65a30d" },
    dining_room:    { label: "Dining Room",   icon: "🍽️", scope: "indoor", w: 15, h: 13, hasDoor: false, defaultDoor: "",   bg: "#fef9c3", border: "#ca8a04" },
    puja_room:      { label: "Puja Altar",    icon: "🛕", scope: "indoor", w: 10, h: 10, hasDoor: true,  defaultDoor: "E",  bg: "#fef08a", border: "#b45309" },
    study_room:     { label: "Study / Office",icon: "💻", scope: "indoor", w: 14, h: 12, hasDoor: false, defaultDoor: "",   bg: "#dbeafe", border: "#2563eb" },
    staircase:      { label: "Staircase",     icon: "🪜", scope: "indoor", w: 12, h: 10, hasDoor: false, defaultDoor: "",   bg: "#e2e8f0", border: "#475569" },
    safe_locker:    { label: "Safe / Locker", icon: "💰", scope: "indoor", w: 8,  h: 8,  hasDoor: true,  defaultDoor: "N",  bg: "#fef08a", border: "#a16207" },

    // Outdoor Lot / Yard Items
    fence:          { label: "Fence / Wall",  icon: "🚧", scope: "outdoor", w: 24, h: 5,  hasDoor: false, defaultDoor: "",   bg: "#e7e5e4", border: "#57534e" },
    gate:           { label: "Main Lot Gate", icon: "⛩️", scope: "outdoor", w: 14, h: 6,  hasDoor: true,  defaultDoor: "NE", bg: "#fde68a", border: "#b45309" },
    parking_gate:   { label: "Parking Gate",  icon: "🚗", scope: "outdoor", w: 16, h: 7,  hasDoor: true,  defaultDoor: "NW", bg: "#cbd5e1", border: "#334155" },
    trees:          { label: "Tall Trees",    icon: "🌳", scope: "outdoor", w: 14, h: 14, hasDoor: false, defaultDoor: "",   bg: "#bbf7d0", border: "#15803d" },
    flowers:        { label: "Flower Bed",    icon: "🌸", scope: "outdoor", w: 12, h: 11, hasDoor: false, defaultDoor: "",   bg: "#fbcfe8", border: "#db2777" },
    bushes:         { label: "Bushes",        icon: "🌿", scope: "outdoor", w: 11, h: 14, hasDoor: false, defaultDoor: "",   bg: "#dcfce7", border: "#16a34a" },
    fireplace:      { label: "Fireplace/BBQ", icon: "🔥", scope: "outdoor", w: 11, h: 11, hasDoor: false, defaultDoor: "",   bg: "#fed7aa", border: "#c2410c" },
    garden:         { label: "Garden Patch",  icon: "🏡", scope: "outdoor", w: 18, h: 10, hasDoor: false, defaultDoor: "",   bg: "#d9f99d", border: "#4d7c0f" },
    grass:          { label: "Grass Lawn",    icon: "🌱", scope: "outdoor", w: 16, h: 18, hasDoor: false, defaultDoor: "",   bg: "#ecfccb", border: "#65a30d" },
    water_body:     { label: "Pool/Fountain", icon: "💧", scope: "outdoor", w: 14, h: 12, hasDoor: false, defaultDoor: "",   bg: "#bae6fd", border: "#0284c7" },
    septic_trash:   { label: "Trash/Septic",  icon: "🗑️", scope: "outdoor", w: 9,  h: 9,  hasDoor: false, defaultDoor: "",   bg: "#e5e7eb", border: "#374151" }
  };

  const DOOR_ARROWS = {
    N: "↑ N", NE: "↗ NE", E: "→ E", SE: "↘ SE",
    S: "↓ S", SW: "↙ SW", W: "← W", NW: "↖ NW"
  };

  const IDEAL_MAP = {
    entrance: ["NE", "E", "N"],
    back_door: ["NW", "W", "E", "N"],
    master_bedroom: ["SW", "S"],
    bedroom: ["W", "S", "E", "NW"],
    guest_room: ["NW", "E", "N"],
    living_room: ["NE", "E", "N", "NW", "Center"],
    kitchen: ["SE", "NW"],
    bathroom: ["NW", "W", "S"],
    storage: ["SW", "S", "W", "NW"],
    balcony: ["NE", "N", "E"],
    dining_room: ["W", "E", "S", "N"],
    puja_room: ["NE", "E", "N"],
    study_room: ["NE", "E", "N", "W"],
    staircase: ["SW", "S", "W"],
    safe_locker: ["SW", "S", "N"],
    fence: ["SW", "S", "W", "N", "E", "NE", "NW", "SE"],
    gate: ["NE", "E", "N"],
    parking_gate: ["NW", "SE", "E", "N"],
    trees: ["SW", "S", "W"],
    flowers: ["NE", "E", "N", "NW", "SE"],
    bushes: ["NW", "W", "S", "SE", "SW"],
    fireplace: ["SE", "S", "NW"],
    garden: ["N", "E", "NE", "NW"],
    grass: ["NE", "N", "E", "NW"],
    water_body: ["NE", "N", "E"],
    septic_trash: ["NW", "W"]
  };

  const BAD_MAP = {
    entrance: ["SW", "S", "SE", "Center"],
    back_door: ["SW", "S", "Center"],
    master_bedroom: ["NE", "SE", "NW", "Center", "E", "N"],
    bedroom: ["NE", "SE", "Center"],
    guest_room: ["SW", "Center", "NE"],
    living_room: ["SW", "SE"],
    kitchen: ["NE", "SW", "N", "W", "Center"],
    bathroom: ["NE", "SW", "Center", "N"],
    storage: ["NE", "E", "N", "Center"],
    balcony: ["SW", "S", "W", "SE", "Center"],
    dining_room: ["SW", "NE", "Center"],
    puja_room: ["S", "SW", "SE", "NW"],
    study_room: ["SE", "Center"],
    staircase: ["NE", "Center", "N", "E"],
    safe_locker: ["SE", "NW", "NE", "Center", "E"],
    fence: [],
    gate: ["SW", "S", "SE", "Center"],
    parking_gate: ["SW", "NE", "Center"],
    trees: ["NE", "N", "E", "Center"],
    flowers: ["Center"],
    bushes: ["NE", "Center"],
    fireplace: ["NE", "N", "SW", "W", "Center"],
    garden: ["Center"],
    grass: [],
    water_body: ["SW", "S", "SE", "W", "Center"],
    septic_trash: ["NE", "N", "E", "SW", "Center"]
  };

  function getIdealPreset() {
    return [
      { id: 1,  type: "entrance",       label: "Main Entrance",      x: 68, y: 18, w: 13, h: 7,  door_dir: "NE", scope: "indoor" },
      { id: 2,  type: "living_room",    label: "Living Room",        x: 47, y: 22, w: 20, h: 17, door_dir: "",   scope: "indoor" },
      { id: 3,  type: "puja_room",      label: "Puja Altar",         x: 70, y: 27, w: 11, h: 10, door_dir: "E",  scope: "indoor" },
      { id: 4,  type: "kitchen",        label: "Kitchen",            x: 64, y: 62, w: 17, h: 16, door_dir: "E",  scope: "indoor" },
      { id: 5,  type: "dining_room",    label: "Dining Room",        x: 66, y: 42, w: 15, h: 16, door_dir: "",   scope: "indoor" },
      { id: 6,  type: "master_bedroom", label: "Master Bedroom",     x: 19, y: 60, w: 22, h: 18, door_dir: "N",  scope: "indoor" },
      { id: 7,  type: "safe_locker",    label: "Safe / Locker",      x: 42, y: 69, w: 9,  h: 9,  door_dir: "N",  scope: "indoor" },
      { id: 8,  type: "bedroom",        label: "Kids Bedroom",       x: 19, y: 40, w: 17, h: 16, door_dir: "E",  scope: "indoor" },
      { id: 9,  type: "guest_room",     label: "Guest Room",         x: 19, y: 20, w: 16, h: 16, door_dir: "E",  scope: "indoor" },
      { id: 10, type: "bathroom",       label: "Bathroom #1",        x: 36, y: 20, w: 10, h: 12, door_dir: "E",  scope: "indoor" },
      { id: 11, type: "storage",        label: "Storage Closet",     x: 52, y: 66, w: 11, h: 12, door_dir: "",   scope: "indoor" },
      { id: 12, type: "balcony",        label: "North Balcony",      x: 49, y: 14, w: 16, h: 6,  door_dir: "N",  scope: "indoor" },
      { id: 13, type: "back_door",      label: "Back Door",          x: 22, y: 14, w: 11, h: 6,  door_dir: "NW", scope: "indoor" },
      // Outdoor Lot Items
      { id: 14, type: "gate",           label: "Main Lot Gate",      x: 68, y: 2,  w: 15, h: 6,  door_dir: "NE", scope: "outdoor" },
      { id: 15, type: "parking_gate",   label: "Parking Gate",       x: 14, y: 2,  w: 18, h: 6,  door_dir: "NW", scope: "outdoor" },
      { id: 16, type: "fence",          label: "South Heavy Fence",  x: 20, y: 92, w: 55, h: 5,  door_dir: "",   scope: "outdoor" },
      { id: 17, type: "trees",          label: "SW Tall Trees",      x: 3,  y: 76, w: 13, h: 15, door_dir: "",   scope: "outdoor" },
      { id: 18, type: "flowers",        label: "NE Flower Bed",      x: 85, y: 12, w: 12, h: 14, door_dir: "",   scope: "outdoor" },
      { id: 19, type: "bushes",         label: "West Shrubs",        x: 3,  y: 38, w: 10, h: 22, door_dir: "",   scope: "outdoor" },
      { id: 20, type: "fireplace",      label: "SE Fire Pit / BBQ",  x: 85, y: 76, w: 12, h: 13, door_dir: "",   scope: "outdoor" },
      { id: 21, type: "garden",         label: "North Veggie Garden",x: 40, y: 3,  w: 24, h: 8,  door_dir: "",   scope: "outdoor" },
      { id: 22, type: "grass",          label: "East Grass Lawn",    x: 85, y: 32, w: 12, h: 34, door_dir: "",   scope: "outdoor" }
    ];
  }

  function detectZone(cx, cy, compassDeg) {
    const dx = cx - 50.0;
    const dy = cy - 50.0;
    if (Math.hypot(dx, dy) < 11.5) return "Center";
    const angleCw = (Math.atan2(dx, -dy) * 180 / Math.PI + 360) % 360;
    const rel = (angleCw - compassDeg + 360) % 360;
    const sectors = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"];
    return sectors[Math.floor(((rel + 22.5) % 360) / 45)];
  }

  window.initVastuArchitect = function (rootId, birthMeta) {
    const root = document.getElementById(rootId);
    if (!root) return;

    let state = {
      houseShape: "square", // 'square' | 'wide_rectangle' | 'deep_rectangle'
      hasOuterLot: true,
      compassRotation: 0,
      items: getIdealPreset(),
      selectedId: 1,
      nextId: 100
    };

    const canvasEl = root.querySelector(".va-canvas");
    const houseBoxEl = root.querySelector(".va-house-box");
    const itemsLayerEl = root.querySelector(".va-items-layer");
    const inspectorEl = root.querySelector(".va-inspector");
    const reportEl = root.querySelector(".va-report-container");

    // Shape & Lot & Compass Controls
    const shapeSel = root.querySelector(".va-shape-select");
    const lotChk = root.querySelector(".va-lot-checkbox");
    const rotSel = root.querySelector(".va-compass-select");

    if (shapeSel) {
      shapeSel.addEventListener("change", () => {
        state.houseShape = shapeSel.value;
        renderCanvas();
        scheduleAnalyze();
      });
    }
    if (lotChk) {
      lotChk.addEventListener("change", () => {
        state.hasOuterLot = lotChk.checked;
        renderCanvas();
        scheduleAnalyze();
      });
    }
    if (rotSel) {
      rotSel.addEventListener("change", () => {
        state.compassRotation = parseFloat(rotSel.value) || 0;
        renderCanvas();
        scheduleAnalyze();
      });
    }

    // Palette Add Buttons
    root.querySelectorAll("[data-va-add]").forEach(btn => {
      btn.addEventListener("click", () => {
        const type = btn.getAttribute("data-va-add");
        const meta = CATALOG[type] || CATALOG.living_room;
        const countSame = state.items.filter(i => i.type === type).length + 1;
        const label = countSame > 1 ? `${meta.label} #${countSame}` : meta.label;
        const isOut = meta.scope === "outdoor";
        const newItem = {
          id: state.nextId++,
          type: type,
          label: label,
          x: isOut ? 8 : 38 + (countSame * 3) % 20,
          y: isOut ? 8 : 38 + (countSame * 3) % 20,
          w: meta.w,
          h: meta.h,
          door_dir: meta.defaultDoor || "",
          scope: meta.scope
        };
        state.items.push(newItem);
        state.selectedId = newItem.id;
        renderCanvas();
        renderInspector();
        scheduleAnalyze();
      });
    });

    // Preset Buttons
    const btnIdeal = root.querySelector(".va-btn-ideal");
    if (btnIdeal) {
      btnIdeal.addEventListener("click", () => {
        state.items = getIdealPreset();
        state.selectedId = state.items[0]?.id || null;
        renderCanvas();
        renderInspector();
        scheduleAnalyze();
      });
    }
    const btnClear = root.querySelector(".va-btn-clear");
    if (btnClear) {
      btnClear.addEventListener("click", () => {
        state.items = [];
        state.selectedId = null;
        renderCanvas();
        renderInspector();
        scheduleAnalyze();
      });
    }

    function getHouseBoundsPercent() {
      if (!state.hasOuterLot) {
        if (state.houseShape === "wide_rectangle") return { left: 4, top: 14, width: 92, height: 72 };
        if (state.houseShape === "deep_rectangle") return { left: 14, top: 4, width: 72, height: 92 };
        return { left: 6, top: 6, width: 88, height: 88 };
      }
      if (state.houseShape === "wide_rectangle") return { left: 14, top: 22, width: 72, height: 56 };
      if (state.houseShape === "deep_rectangle") return { left: 22, top: 14, width: 56, height: 72 };
      return { left: 16, top: 16, width: 68, height: 68 };
    }

    function renderCanvas() {
      const hb = getHouseBoundsPercent();
      houseBoxEl.style.left = hb.left + "%";
      houseBoxEl.style.top = hb.top + "%";
      houseBoxEl.style.width = hb.width + "%";
      houseBoxEl.style.height = hb.height + "%";

      canvasEl.style.background = state.hasOuterLot
        ? "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)"
        : "#f8fafc";

      // Update compass labels around outer border based on compassRotation
      const baseDirs = [
        { code: "N",  label: "N (Kubera / Money)",   x: 50, y: 2 },
        { code: "NE", label: "NE (Ishanya / Shiva)", x: 92, y: 4 },
        { code: "E",  label: "E (Surya / Sun)",      x: 95, y: 50 },
        { code: "SE", label: "SE (Agni / Fire)",     x: 91, y: 96 },
        { code: "S",  label: "S (Yama / Mars)",      x: 50, y: 97 },
        { code: "SW", label: "SW (Nairutya / Earth)",x: 9,  y: 96 },
        { code: "W",  label: "W (Varuna / Saturn)",  x: 5,  y: 50 },
        { code: "NW", label: "NW (Vayu / Air)",      x: 9,  y: 4 }
      ];
      root.querySelectorAll(".va-compass-tag").forEach((el, i) => {
        const shiftIdx = Math.round(state.compassRotation / 45) % 8;
        const dInfo = baseDirs[(i - shiftIdx + 8) % 8];
        el.textContent = dInfo.label;
      });

      itemsLayerEl.innerHTML = "";
      state.items.forEach(item => {
        if (!state.hasOuterLot && item.scope === "outdoor") return;
        const meta = CATALOG[item.type] || CATALOG.living_room;
        const cx = item.x + item.w / 2;
        const cy = item.y + item.h / 2;
        const zone = detectZone(cx, cy, state.compassRotation);

        const ideals = IDEAL_MAP[item.type] || [];
        const bads = BAD_MAP[item.type] || [];
        let statusColor = "#d97706"; // acceptable amber
        let statusBg = meta.bg;
        if (ideals.includes(zone)) {
          statusColor = "#15803d"; // ideal green
        } else if (bads.includes(zone)) {
          statusColor = "#dc2626"; // dosha red
          statusBg = "#fee2e2";
        }

        const el = document.createElement("div");
        el.className = "va-block" + (item.id === state.selectedId ? " va-selected" : "");
        el.style.cssText = `
          position: absolute;
          left: ${item.x}%;
          top: ${item.y}%;
          width: ${item.w}%;
          height: ${item.h}%;
          background: ${statusBg};
          border: 2px ${item.scope === "outdoor" ? "dashed" : "solid"} ${item.id === state.selectedId ? "#111827" : statusColor};
          border-radius: 6px;
          box-sizing: border-box;
          cursor: move;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 2px 4px;
          text-align: center;
          user-select: none;
          box-shadow: ${item.id === state.selectedId ? "0 0 0 3px rgba(245,158,11,0.55)" : "0 1px 3px rgba(0,0,0,0.12)"};
          z-index: ${item.id === state.selectedId ? 30 : (item.scope === "outdoor" ? 10 : 20)};
          overflow: hidden;
        `;

        const doorBadge = item.door_dir
          ? `<span style="font-size:10px;background:#1e293b;color:#fff;padding:0 4px;border-radius:3px;margin-top:1px;">Door ${DOOR_ARROWS[item.door_dir] || item.door_dir}</span>`
          : "";

        el.innerHTML = `
          <div style="font-size:11px;font-weight:700;line-height:1.15;color:#111827;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%;">
            ${meta.icon} ${item.label}
          </div>
          <div style="font-size:10px;font-weight:700;color:${statusColor};line-height:1.1;">
            [${zone}]
          </div>
          ${doorBadge}
          <div class="va-resize-handle" title="Drag to resize" style="position:absolute;right:0;bottom:0;width:11px;height:11px;background:${statusColor};cursor:nwse-resize;border-top-left-radius:4px;"></div>
        `;

        // Dragging & Resizing
        el.addEventListener("mousedown", e => {
          e.stopPropagation();
          state.selectedId = item.id;
          renderInspector();
          const isResize = e.target.classList.contains("va-resize-handle");
          const rect = canvasEl.getBoundingClientRect();
          const startX = e.clientX;
          const startY = e.clientY;
          const origX = item.x;
          const origY = item.y;
          const origW = item.w;
          const origH = item.h;

          function onMove(ev) {
            const dxPct = ((ev.clientX - startX) / rect.width) * 100;
            const dyPct = ((ev.clientY - startY) / rect.height) * 100;
            if (isResize) {
              item.w = Math.max(6, Math.min(95 - item.x, Math.round(origW + dxPct)));
              item.h = Math.max(5, Math.min(95 - item.y, Math.round(origH + dyPct)));
            } else {
              item.x = Math.max(1, Math.min(99 - item.w, Math.round(origX + dxPct)));
              item.y = Math.max(1, Math.min(99 - item.h, Math.round(origY + dyPct)));
            }
            renderCanvas();
          }

          function onUp() {
            window.removeEventListener("mousemove", onMove);
            window.removeEventListener("mouseup", onUp);
            renderInspector();
            scheduleAnalyze();
          }

          window.addEventListener("mousemove", onMove);
          window.addEventListener("mouseup", onUp);
          renderCanvas();
        });

        itemsLayerEl.appendChild(el);
      });
    }

    function renderInspector() {
      if (!inspectorEl) return;
      const item = state.items.find(i => i.id === state.selectedId);
      if (!item) {
        inspectorEl.innerHTML = `<div class="neutral" style="font-size:13px;">Click any room or yard item on the canvas to customize its label, size, door direction, or delete it.</div>`;
        return;
      }
      const meta = CATALOG[item.type] || CATALOG.living_room;
      const zone = detectZone(item.x + item.w / 2, item.y + item.h / 2, state.compassRotation);
      const dirs = ["", "N", "NE", "E", "SE", "S", "SW", "W", "NW"];
      const dirOpts = dirs.map(d => `<option value="${d}" ${item.door_dir === d ? "selected" : ""}>${d ? "Facing " + d : "No Door / N/A"}</option>`).join("");

      inspectorEl.innerHTML = `
        <div style="display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;justify-content:space-between;">
          <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;">
            <div>
              <label style="font-size:12px;font-weight:700;display:block;">Selected Item (${zone} Zone)</label>
              <input type="text" class="va-inp-label" value="${item.label}" style="padding:5px 8px;border:1px solid #cbd5e1;border-radius:4px;width:165px;">
            </div>
            <div>
              <label style="font-size:12px;font-weight:700;display:block;">Door / Gate Facing</label>
              <select class="va-inp-door" style="padding:5px 8px;border:1px solid #cbd5e1;border-radius:4px;">${dirOpts}</select>
            </div>
            <div>
              <label style="font-size:12px;font-weight:700;display:block;">Placement Area</label>
              <select class="va-inp-scope" style="padding:5px 8px;border:1px solid #cbd5e1;border-radius:4px;">
                <option value="indoor" ${item.scope === "indoor" ? "selected" : ""}>Inside House</option>
                <option value="outdoor" ${item.scope === "outdoor" ? "selected" : ""}>Outside on Lot / Yard</option>
              </select>
            </div>
            <div>
              <label style="font-size:12px;font-weight:700;display:block;">Width %</label>
              <input type="number" class="va-inp-w" min="6" max="80" value="${item.w}" style="padding:5px 6px;border:1px solid #cbd5e1;border-radius:4px;width:62px;">
            </div>
            <div>
              <label style="font-size:12px;font-weight:700;display:block;">Height %</label>
              <input type="number" class="va-inp-h" min="5" max="80" value="${item.h}" style="padding:5px 6px;border:1px solid #cbd5e1;border-radius:4px;width:62px;">
            </div>
          </div>
          <div style="display:flex;gap:8px;">
            <button type="button" class="btn va-btn-dup" style="background:#0f766e;color:#fff;padding:6px 12px;font-size:12px;">➕ Duplicate</button>
            <button type="button" class="btn va-btn-del" style="background:#dc2626;color:#fff;padding:6px 12px;font-size:12px;">🗑️ Remove</button>
          </div>
        </div>
      `;

      inspectorEl.querySelector(".va-inp-label").addEventListener("input", e => {
        item.label = e.target.value;
        renderCanvas();
        scheduleAnalyze();
      });
      inspectorEl.querySelector(".va-inp-door").addEventListener("change", e => {
        item.door_dir = e.target.value;
        renderCanvas();
        scheduleAnalyze();
      });
      inspectorEl.querySelector(".va-inp-scope").addEventListener("change", e => {
        item.scope = e.target.value;
        renderCanvas();
        scheduleAnalyze();
      });
      inspectorEl.querySelector(".va-inp-w").addEventListener("change", e => {
        item.w = Math.max(6, Math.min(80, parseInt(e.target.value, 10) || item.w));
        renderCanvas();
        scheduleAnalyze();
      });
      inspectorEl.querySelector(".va-inp-h").addEventListener("change", e => {
        item.h = Math.max(5, Math.min(80, parseInt(e.target.value, 10) || item.h));
        renderCanvas();
        scheduleAnalyze();
      });
      inspectorEl.querySelector(".va-btn-dup").addEventListener("click", () => {
        const copy = Object.assign({}, item, {
          id: state.nextId++,
          label: item.label + " (Copy)",
          x: Math.min(85, item.x + 4),
          y: Math.min(85, item.y + 4)
        });
        state.items.push(copy);
        state.selectedId = copy.id;
        renderCanvas();
        renderInspector();
        scheduleAnalyze();
      });
      inspectorEl.querySelector(".va-btn-del").addEventListener("click", () => {
        state.items = state.items.filter(i => i.id !== item.id);
        state.selectedId = state.items[0]?.id || null;
        renderCanvas();
        renderInspector();
        scheduleAnalyze();
      });
    }

    let timer = null;
    function scheduleAnalyze() {
      clearTimeout(timer);
      timer = setTimeout(runAnalyze, 220);
    }

    async function runAnalyze() {
      if (!reportEl) return;
      const visibleItems = state.items.filter(i => state.hasOuterLot || i.scope !== "outdoor");
      const payload = Object.assign({
        house_shape: state.houseShape,
        has_outer_lot: state.hasOuterLot,
        compass_rotation: state.compassRotation,
        items: visibleItems
      }, birthMeta || {});

      try {
        const r = await fetch("/api/vastu/analyze-layout", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (!r.ok) return;
        const data = await r.json();
        renderReport(data);
      } catch (e) {}
    }

    function renderReport(data) {
      const scoreColor = data.overall_vastu_score_percent >= 80 ? "#15803d" : (data.overall_vastu_score_percent >= 65 ? "#d97706" : "#dc2626");
      const rows = (data.item_by_item_breakdown || []).map(it => {
        const badgeStyle = it.badge_color === "good"
          ? "background:#dcfce7;color:#15803d;border:1px solid #86efac;"
          : (it.badge_color === "bad"
              ? "background:#fee2e2;color:#b91c1c;border:1px solid #fca5a5;"
              : "background:#fef3c7;color:#b45309;border:1px solid #fde68a;");
        return `
          <tr>
            <td><strong>${it.label}</strong><br><small class="neutral">${it.scope}</small></td>
            <td><b>${it.detected_zone}</b><br><small>${it.zone_full_name}</small><br><small class="neutral">${it.zone_planet_and_element}</small></td>
            <td>${it.door_or_gate_facing}</td>
            <td><span class="badge" style="${badgeStyle}">${it.status} (${it.score_out_of_10}/10)</span><br><small>Ideal: ${it.ideal_zones_for_this_item.join(", ")}</small></td>
            <td>
              <div>${it.verdict_in_simple_words}</div>
              <div style="margin-top:4px;font-size:12px;color:#475569;"><b>Plain-English Rule:</b> ${it.why_this_rule_exists}</div>
              ${it.birth_chart_synergy ? `<div style="margin-top:4px;font-size:12px;color:#0f766e;"><b>🌟 ${it.birth_chart_synergy}</b></div>` : ""}
            </td>
            <td><small>${it.zero_demolition_remedy}</small></td>
          </tr>
        `;
      }).join("");

      const doshasHtml = (data.critical_doshas_and_fixes || []).map(d => `<li>${d}</li>`).join("");
      const strengthsHtml = (data.auspicious_strengths || []).map(s => `<li>${s}</li>`).join("");

      reportEl.innerHTML = `
        <div class="grid-3" style="margin-top:14px;">
          <div class="stat">
            <span class="label">Live Layout Vastu Score</span>
            <span class="value" style="color:${scoreColor};font-size:1.5rem;">${data.overall_vastu_score_percent}%</span>
            <small><b>${data.overall_grade}</b> (${data.total_items_evaluated} items placed)</small>
          </div>
          <div class="stat">
            <span class="label">House Shape Geometry</span>
            <span class="value" style="font-size:1rem;">${data.house_shape_analysis.name}</span>
            <small>${data.house_shape_analysis.explanation}</small>
          </div>
          <div class="stat">
            <span class="label">Outer Lot &amp; Compass</span>
            <span class="value" style="font-size:1rem;">${data.has_outer_lot ? "House + Outer Lot/Yard Active" : "Interior House Footprint Only"}</span>
            <small>Compass Rotation: ${data.compass_rotation_degrees}° from True North</small>
          </div>
        </div>

        <div class="grid-2" style="margin-top:16px;">
          <div style="padding:14px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;">
            <h4 style="margin-top:0;color:#15803d;">✅ Auspicious Placements Boosting Your Chart</h4>
            <ul style="margin:0;padding-left:18px;font-size:13px;">${strengthsHtml}</ul>
          </div>
          <div style="padding:14px;background:#fef2f2;border:1px solid #fecaca;border-radius:8px;">
            <h4 style="margin-top:0;color:#b91c1c;">🛠️ Vastu Defects (Doshas) &amp; Priority Fixes</h4>
            <ul style="margin:0;padding-left:18px;font-size:13px;">${doshasHtml}</ul>
          </div>
        </div>

        <h3 style="margin-top:18px;">📐 Complete Room-by-Room &amp; Outer-Lot Vastu Breakdown (Plain-English Explanations &amp; Fixes)</h3>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Placed Block &amp; Area</th>
                <th>Detected Compass Zone</th>
                <th>Door / Gate Facing</th>
                <th>Vastu Verdict &amp; Score</th>
                <th>Plain-English Explanation &amp; Birth-Chart Synergy</th>
                <th>Zero-Demolition Fix / Remedy</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      `;
    }

    renderCanvas();
    renderInspector();
    runAnalyze();
  };
})();
