/**
 * Multi-Spectrum Computer-Vision Palmistry & Nadi Thumbprint Studio
 * Allows instant switching back and forth across 10 color & spectral channels
 * (True RGB, CLAHE Ridge Enhancer, 540nm Green Subdermal, Near-Infrared NIR,
 * UV Micro-Ridge, Sobel Edge Skeleton, Biometric Ink-Stamp, Thermal Mount Heatmap,
 * Inverted X-Ray Negative, and AI Vector Overlay) for both Palm and Thumbprint photos,
 * backed by POST /api/palmistry/analyze-photo.
 */
(function () {
  const SPECTRUMS = [
    { id: "original",          short: "1. 🌈 True RGB",         title: "Original True-Color RGB (400–700nm)", desc: "Natural skin tone, capillary circulation, and mount fullness." },
    { id: "ridge_enhance",     short: "2. 🔍 Ridge Enhancer",   title: "CLAHE Crease & Micro-Ridge Enhancer", desc: "Boosts local micro-contrast so faint Fate, Sun, and Marriage lines pop out." },
    { id: "red_free_green",    short: "3. 🟢 540nm Subdermal",  title: "540nm Green-Channel Subdermal Line Filter", desc: "Hemoglobin along creases absorbs green light, turning palm lines razor-sharp." },
    { id: "infrared_sim",      short: "4. 🔴 Near-IR Deep",     title: "Near-Infrared (NIR) Deep Flexion Spectrum", desc: "Penetrates surface glare to highlight deep Life, Head, and Heart line trenches." },
    { id: "uv_micro_ridge",    short: "5. 🟣 UV Micro-Ridge",   title: "UV / Blue-Violet Papillary & Thumbprint Spectrum", desc: "Reveals fine epidermal papillary ridges, whorls, loops, islands, and stars." },
    { id: "sobel_edge",        short: "6. ⚡ Edge Skeleton",    title: "Sobel 2D Gradient Line & Ridge Skeleton", desc: "Mathematical gradient ||∇I|| tracing exact crease geometry in glowing cyan/gold." },
    { id: "adaptive_ink",      short: "7. 🖋️ Ink Stamp Print",  title: "Biometric Ink-Stamp / Threshold Print", desc: "High-contrast black-on-ivory ink impression for Nadi thumbprint & ridge counting." },
    { id: "thermal_mount",     short: "8. 🌡️ Mount Heatmap",    title: "False-Color Thermal Mount Elevation Heatmap", desc: "Maps contour elevation so the 9 Planetary Mounts stand out from palm valleys." },
    { id: "inverted_xray",     short: "9. 🩻 X-Ray Negative",   title: "Inverted X-Ray Negative Crease Spectrum", desc: "Palm lines and thumb ridges glow bright white against deep obsidian." },
    { id: "annotated_overlay", short: "10. Reference lines", title: "Reference line and mount map", desc: "Draws the usual Heart, Head, Life, and Fate positions as a guide. These marks are not measured from the photo." },
  ];

  /**
   * Draws a high-resolution, realistic synthetic human palm + thumbprint onto an offscreen canvas
   * so users can immediately test all 10 multi-spectrum filters and thumbprint ridge modes
   * even before uploading their own photo.
   */
  function generateRealisticSamplePalm(canvas) {
    canvas.width = 640;
    canvas.height = 760;
    const ctx = canvas.getContext("2d");

    // Dark studio backdrop
    ctx.fillStyle = "#111827";
    ctx.fillRect(0, 0, 640, 760);

    // Draw anatomical palm silhouette + 5 fingers
    ctx.save();
    const skinGrad = ctx.createRadialGradient(320, 450, 30, 320, 430, 320);
    skinGrad.addColorStop(0, "#f5cba7");
    skinGrad.addColorStop(0.55, "#eab68c");
    skinGrad.addColorStop(0.88, "#d99b6c");
    skinGrad.addColorStop(1, "#b87a4b");

    ctx.fillStyle = skinGrad;
    ctx.beginPath();
    // Wrist base
    ctx.moveTo(220, 725);
    ctx.quadraticCurveTo(190, 620, 145, 535);
    // Thumb (Left side)
    ctx.quadraticCurveTo(95, 485, 62, 415);
    ctx.quadraticCurveTo(45, 365, 75, 345);
    ctx.quadraticCurveTo(112, 335, 138, 395);
    ctx.quadraticCurveTo(160, 435, 185, 425);
    // Index finger (Jupiter)
    ctx.lineTo(188, 175);
    ctx.quadraticCurveTo(192, 130, 218, 132);
    ctx.quadraticCurveTo(242, 135, 245, 180);
    ctx.lineTo(252, 315);
    // Middle finger (Saturn)
    ctx.lineTo(268, 135);
    ctx.quadraticCurveTo(274, 92, 302, 92);
    ctx.quadraticCurveTo(328, 92, 330, 138);
    ctx.lineTo(332, 312);
    // Ring finger (Sun/Apollo)
    ctx.lineTo(352, 155);
    ctx.quadraticCurveTo(358, 115, 384, 118);
    ctx.quadraticCurveTo(408, 122, 408, 165);
    ctx.lineTo(402, 328);
    // Little finger (Mercury)
    ctx.lineTo(432, 220);
    ctx.quadraticCurveTo(442, 185, 465, 192);
    ctx.quadraticCurveTo(486, 200, 478, 240);
    ctx.lineTo(458, 375);
    // Outer percussion edge (Upper Mars & Moon Mount)
    ctx.quadraticCurveTo(485, 495, 445, 625);
    ctx.quadraticCurveTo(420, 690, 395, 725);
    ctx.closePath();
    ctx.fill();

    // Subtle Planetary Mount Elevations (bright warm highlights for thermal & 3D contour)
    const mounts = [
      { x: 222, y: 358, r: 42 }, // Jupiter
      { x: 300, y: 350, r: 38 }, // Saturn
      { x: 372, y: 362, r: 38 }, // Apollo/Sun
      { x: 432, y: 392, r: 34 }, // Mercury
      { x: 235, y: 545, r: 72 }, // Venus (fleshy thumb base)
      { x: 395, y: 565, r: 62 }, // Moon/Luna
      { x: 215, y: 438, r: 35 }, // Lower Mars
      { x: 425, y: 465, r: 35 }  // Upper Mars
    ];
    mounts.forEach(m => {
      const mg = ctx.createRadialGradient(m.x, m.y, 4, m.x, m.y, m.r);
      mg.addColorStop(0, "rgba(255, 232, 208, 0.42)");
      mg.addColorStop(1, "rgba(255, 232, 208, 0)");
      ctx.fillStyle = mg;
      ctx.beginPath();
      ctx.arc(m.x, m.y, m.r, 0, Math.PI * 2);
      ctx.fill();
    });

    // Helper to draw multi-layered anatomical palm creases (subdermal hemoglobin + dermal shadow)
    function drawCrease(points, width, depthAlpha) {
      ctx.save();
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      // Outer soft reddish-brown subdermal halo (absorbs 540nm green strongly!)
      ctx.strokeStyle = `rgba(148, 62, 45, ${depthAlpha * 0.55})`;
      ctx.lineWidth = width * 2.3;
      ctx.beginPath();
      ctx.moveTo(points[0][0], points[0][1]);
      for (let i = 1; i < points.length; i++) ctx.lineTo(points[i][0], points[i][1]);
      ctx.stroke();

      // Core crease trench
      ctx.strokeStyle = `rgba(88, 32, 22, ${depthAlpha})`;
      ctx.lineWidth = width;
      ctx.beginPath();
      ctx.moveTo(points[0][0], points[0][1]);
      for (let i = 1; i < points.length; i++) ctx.lineTo(points[i][0], points[i][1]);
      ctx.stroke();
      ctx.restore();
    }

    // 1. Heart Line (Hridaya Rekha): sweeps from beneath Mercury across to Jupiter
    drawCrease([[456, 418], [405, 412], [352, 402], [298, 385], [248, 362], [218, 344]], 3.4, 0.88);
    // Heart line upward fork (Trident of Jupiter)
    drawCrease([[248, 362], [235, 338]], 2.1, 0.72);
    drawCrease([[248, 362], [212, 360]], 2.0, 0.68);

    // 2. Head Line (Mastishka Rekha): starts near Life line origin, slopes across Plain of Mars
    drawCrease([[192, 412], [245, 422], [308, 442], [368, 468], [418, 495]], 3.2, 0.86);
    // Writer's / Strategic fork on Head Line
    drawCrease([[368, 468], [415, 464]], 1.8, 0.62);

    // 3. Life Line (Jeevana Rekha): wide strong arc around Mount of Venus
    drawCrease([[190, 410], [228, 438], [262, 478], [285, 528], [292, 585], [282, 645], [265, 682]], 3.6, 0.92);
    // Mars Sister / Protection Line inside Life Line
    drawCrease([[205, 445], [238, 482], [256, 535], [258, 590]], 1.7, 0.58);

    // 4. Fate / Saturn Line (Bhagya Rekha): rises from base of palm (Ketu) to Mount of Saturn
    drawCrease([[308, 668], [312, 595], [310, 520], [305, 445], [301, 362]], 2.6, 0.78);

    // 5. Sun / Apollo Line (Surya / Yash Rekha): rises toward Ring Finger
    drawCrease([[355, 535], [362, 475], [368, 418], [372, 365]], 2.1, 0.68);

    // 6. Mercury / Health & Business Line (Budha Rekha)
    drawCrease([[335, 615], [375, 535], [408, 462], [428, 398]], 1.8, 0.60);

    // 7. Marriage / Union Lines on Mercury edge
    drawCrease([[458, 394], [434, 395]], 1.9, 0.72);
    drawCrease([[457, 404], [440, 405]], 1.4, 0.55);

    // 8. Mystic Cross between Head & Heart lines
    drawCrease([[318, 402], [335, 435]], 1.6, 0.60);
    drawCrease([[336, 402], [316, 435]], 1.6, 0.60);

    // 9. Three Manibandha Wrist Bracelets
    drawCrease([[218, 695], [308, 688], [392, 696]], 2.4, 0.75);
    drawCrease([[220, 710], [308, 703], [390, 711]], 2.1, 0.68);
    drawCrease([[224, 723], [308, 717], [386, 724]], 1.8, 0.60);

    // 10. Finger Phalange Knuckle Creases
    [[192,235,244,236],[190,278,248,280],[271,200,328,200],[270,255,330,255],
     [354,218,406,220],[352,272,404,274],[435,268,476,274],[432,315,470,320]].forEach(c => {
      drawCrease([[c[0], c[1]], [c[2], c[3]]], 1.8, 0.65);
    });

    // 11. High-Detail Nadi Thumbprint (Chakra Whorl / Spiral) on the Thumb Tip (around x=92, y=382)
    ctx.strokeStyle = "rgba(92, 36, 24, 0.62)";
    ctx.lineWidth = 1.15;
    for (let r = 3; r <= 26; r += 2.6) {
      ctx.beginPath();
      ctx.ellipse(92, 382, r * 0.85, r * 1.15, -0.35, 0, Math.PI * 1.88);
      ctx.stroke();
    }

    // Fine epidermal micro-ridges across the palm plain for realistic CLAHE / UV / Sobel response
    ctx.strokeStyle = "rgba(110, 48, 32, 0.14)";
    ctx.lineWidth = 0.8;
    for (let y = 340; y < 670; y += 5) {
      ctx.beginPath();
      ctx.moveTo(195, y);
      ctx.bezierCurveTo(260, y - 8, 350, y + 8, 435, y - 4);
      ctx.stroke();
    }
    ctx.restore();
  }

  /**
   * Applies the selected diagnostic color / spectral algorithm to source ImageData
   */
  function processSpectrumPixels(srcData, mode, opts) {
    const w = srcData.width;
    const h = srcData.height;
    const src = srcData.data;
    const dstImg = new ImageData(w, h);
    const dst = dstImg.data;

    const contrast = (opts.contrast || 100) / 100.0;
    const brightness = (opts.brightness || 0);
    const sharp = (opts.sharpness || 100) / 100.0;
    const threshBias = (opts.threshold || 128);

    const gray = new Float32Array(w * h);
    const greenEnh = new Float32Array(w * h);

    for (let i = 0, p = 0; i < src.length; i += 4, p++) {
      const r = src[i];
      const g = src[i + 1];
      const b = src[i + 2];
      // Standard luminance
      gray[p] = 0.299 * r + 0.587 * g + 0.114 * b;
      // Subdermal crease index: hemoglobin in creases absorbs green (G) more than red (R)
      greenEnh[p] = Math.max(0, Math.min(255, g - (r - g) * 0.85 * sharp));
    }

    // Compute local 5x5 neighborhood mean for CLAHE / Adaptive Ink / Unsharp Mask
    const localMean = new Float32Array(w * h);
    const radius = 3;
    for (let y = 0; y < h; y++) {
      const y0 = Math.max(0, y - radius);
      const y1 = Math.min(h - 1, y + radius);
      for (let x = 0; x < w; x++) {
        const x0 = Math.max(0, x - radius);
        const x1 = Math.min(w - 1, x + radius);
        let sum = 0, cnt = 0;
        for (let yy = y0; yy <= y1; yy += 2) {
          const rowOff = yy * w;
          for (let xx = x0; xx <= x1; xx += 2) {
            sum += greenEnh[rowOff + xx];
            cnt++;
          }
        }
        localMean[y * w + x] = sum / cnt;
      }
    }

    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const p = y * w + x;
        const i = p * 4;
        const r = src[i];
        const g = src[i + 1];
        const b = src[i + 2];
        const lum = gray[p];
        const diffLocal = greenEnh[p] - localMean[p];

        let or = r, og = g, ob = b;

        if (mode === "original" || mode === "annotated_overlay") {
          or = (r - 128) * contrast + 128 + brightness;
          og = (g - 128) * contrast + 128 + brightness;
          ob = (b - 128) * contrast + 128 + brightness;
        } else if (mode === "ridge_enhance") {
          // CLAHE + Unsharp crease amplifier
          const boost = diffLocal * 2.8 * sharp;
          or = (r + boost - 128) * contrast + 128 + brightness;
          og = (g + boost * 1.25 - 128) * contrast + 128 + brightness;
          ob = (b + boost * 1.1 - 128) * contrast + 128 + brightness;
        } else if (mode === "red_free_green") {
          // 540nm Clinical Green-Channel Subdermal Filter
          const v = Math.max(0, Math.min(255, (greenEnh[p] + diffLocal * 2.4 * sharp - 128) * contrast + 128 + brightness));
          or = v * 0.18;
          og = v;
          ob = v * 0.32;
        } else if (mode === "infrared_sim") {
          // Simulated Near-Infrared (750–900nm): deep red/luminance + deep trench contrast
          const nir = 0.65 * r + 0.30 * g + 0.05 * b + diffLocal * 2.1 * sharp;
          const v = Math.max(0, Math.min(255, (nir - 128) * contrast * 1.15 + 128 + brightness));
          or = Math.min(255, v * 1.08);
          og = v * 0.86;
          ob = v * 0.78;
        } else if (mode === "uv_micro_ridge") {
          // UV / Blue-Violet Micro-Ridge & Thumbprint Spectrum
          const uv = 0.25 * r + 0.45 * g + 0.30 * b + diffLocal * 3.4 * sharp;
          const v = Math.max(0, Math.min(255, (uv - 128) * contrast * 1.2 + 128 + brightness));
          or = v * 0.62;
          og = v * 0.48;
          ob = Math.min(255, v * 1.25);
        } else if (mode === "sobel_edge") {
          // 2D Sobel Gradient Magnitude ||∇I||
          let gx = 0, gy = 0;
          if (x > 0 && x < w - 1 && y > 0 && y < h - 1) {
            const tl = greenEnh[(y - 1) * w + (x - 1)];
            const tc = greenEnh[(y - 1) * w + x];
            const tr = greenEnh[(y - 1) * w + (x + 1)];
            const ml = greenEnh[y * w + (x - 1)];
            const mr = greenEnh[y * w + (x + 1)];
            const bl = greenEnh[(y + 1) * w + (x - 1)];
            const bc = greenEnh[(y + 1) * w + x];
            const br = greenEnh[(y + 1) * w + (x + 1)];
            gx = (tr + 2 * mr + br) - (tl + 2 * ml + bl);
            gy = (bl + 2 * bc + br) - (tl + 2 * tc + tr);
          }
          const mag = Math.min(255, Math.hypot(gx, gy) * 1.45 * sharp * contrast);
          // Glowing cyan/gold skeleton on dark background
          or = Math.min(255, mag * 0.45 + Math.max(0, -diffLocal * 2.5));
          og = Math.min(255, mag * 1.05);
          ob = Math.min(255, mag * 1.25);
        } else if (mode === "adaptive_ink") {
          // Biometric Ink-Stamp / Threshold Print Mode
          const cut = (threshBias - 128) * 0.15 - 2.2;
          const isInk = diffLocal * sharp < cut || lum < 40;
          if (lum < 32) {
            // background outside hand
            or = 248; og = 245; ob = 236;
          } else if (isInk) {
            or = 24; og = 20; ob = 42;
          } else {
            or = 252; og = 249; ob = 240;
          }
        } else if (mode === "thermal_mount") {
          // False-Color Thermal Mount Elevation Heatmap
          const t = Math.max(0, Math.min(1, ((lum + diffLocal * 1.2 - 30) / 210) * contrast));
          if (lum < 32) {
            or = 12; og = 16; ob = 28;
          } else if (t < 0.25) {
            const k = t / 0.25;
            or = 20; og = Math.round(40 + 180 * k); ob = Math.round(140 + 115 * k);
          } else if (t < 0.55) {
            const k = (t - 0.25) / 0.30;
            or = Math.round(30 + 210 * k); og = 230; ob = Math.round(255 * (1 - k));
          } else if (t < 0.80) {
            const k = (t - 0.55) / 0.25;
            or = 255; og = Math.round(230 * (1 - k * 0.75)); ob = 20;
          } else {
            const k = (t - 0.80) / 0.20;
            or = 255; og = Math.round(60 + 195 * k); ob = Math.round(40 + 200 * k);
          }
        } else if (mode === "inverted_xray") {
          // Inverted X-Ray Negative Crease Spectrum
          const inv = 255 - (greenEnh[p] + diffLocal * 2.5 * sharp);
          const v = Math.max(0, Math.min(255, (inv - 128) * contrast * 1.15 + 128 + brightness));
          or = v * 0.88;
          og = v * 0.96;
          ob = Math.min(255, v * 1.08);
        }

        dst[i]     = Math.max(0, Math.min(255, or));
        dst[i + 1] = Math.max(0, Math.min(255, og));
        dst[i + 2] = Math.max(0, Math.min(255, ob));
        dst[i + 3] = 255;
      }
    }
    return dstImg;
  }

  /**
   * Draws the AI Computer-Vision anatomical palm line & planetary mount overlay
   */
  function drawAnnotatedOverlay(ctx, w, h) {
    const sx = w / 640;
    const sy = h / 760;
    ctx.save();
    ctx.lineCap = "round";
    ctx.lineJoin = "round";

    const lines = [
      { label: "Heart Line (Hridaya)", color: "#f43f5e", pts: [[456, 418], [405, 412], [352, 402], [298, 385], [248, 362], [218, 344]] },
      { label: "Head Line (Mastishka)", color: "#38bdf8", pts: [[192, 412], [245, 422], [308, 442], [368, 468], [418, 495]] },
      { label: "Life Line (Jeevana)",   color: "#22c55e", pts: [[190, 410], [228, 438], [262, 478], [285, 528], [292, 585], [282, 645], [265, 682]] },
      { label: "Fate Line (Bhagya)",    color: "#f59e0b", pts: [[308, 668], [312, 595], [310, 520], [305, 445], [301, 362]] },
      { label: "Sun Line (Surya)",      color: "#eab308", pts: [[355, 535], [362, 475], [368, 418], [372, 365]] },
      { label: "Mercury Line (Budha)",  color: "#a855f7", pts: [[335, 615], [375, 535], [408, 462], [428, 398]] }
    ];

    lines.forEach(ln => {
      ctx.strokeStyle = ln.color;
      ctx.lineWidth = 3 * sx;
      ctx.setLineDash([6 * sx, 4 * sx]);
      ctx.beginPath();
      ctx.moveTo(ln.pts[0][0] * sx, ln.pts[0][1] * sy);
      for (let i = 1; i < ln.pts.length; i++) {
        ctx.lineTo(ln.pts[i][0] * sx, ln.pts[i][1] * sy);
      }
      ctx.stroke();
      ctx.setLineDash([]);
      const mid = ln.pts[Math.floor(ln.pts.length / 2)];
      ctx.fillStyle = "rgba(15, 23, 42, 0.82)";
      ctx.fillRect(mid[0] * sx - 48 * sx, mid[1] * sy - 11 * sy, 98 * sx, 16 * sy);
      ctx.fillStyle = ln.color;
      ctx.font = `bold ${Math.max(10, Math.round(11 * sx))}px sans-serif`;
      ctx.fillText(ln.label, mid[0] * sx - 44 * sx, mid[1] * sy + 1 * sy);
    });

    const mountLabels = [
      { name: "Jupiter", x: 222, y: 345, c: "#fde047" },
      { name: "Saturn",  x: 300, y: 338, c: "#93c5fd" },
      { name: "Sun",     x: 372, y: 348, c: "#fdba74" },
      { name: "Mercury", x: 435, y: 378, c: "#d8b4fe" },
      { name: "Venus Mount", x: 225, y: 560, c: "#f9a8d4" },
      { name: "Moon Mount",  x: 395, y: 585, c: "#bae6fd" },
      { name: "Rahu Plain",  x: 325, y: 475, c: "#cbd5e1" },
      { name: "Ketu Base",   x: 312, y: 655, c: "#fca5a5" },
      { name: "Nadi Thumbprint", x: 92, y: 382, c: "#4ade80" }
    ];

    mountLabels.forEach(m => {
      ctx.beginPath();
      ctx.strokeStyle = m.c;
      ctx.lineWidth = 1.8 * sx;
      ctx.arc(m.x * sx, m.y * sy, 22 * sx, 0, Math.PI * 2);
      ctx.stroke();
      ctx.fillStyle = "rgba(15, 23, 42, 0.85)";
      ctx.fillRect((m.x - 36) * sx, (m.y - 8) * sy, 72 * sx, 15 * sy);
      ctx.fillStyle = m.c;
      ctx.font = `bold ${Math.max(9, Math.round(10 * sx))}px sans-serif`;
      ctx.textAlign = "center";
      ctx.fillText(m.name, m.x * sx, (m.y + 3) * sy);
    });

    ctx.restore();
  }

  window.initPalmistryVisionStudio = function (rootId, birthMeta) {
    const root = document.getElementById(rootId);
    if (!root) return;

    let state = {
      activeSpectrumIdx: 1, // Default to CLAHE Ridge Enhancer so user immediately sees enhanced lines
      splitCompare: true,   // Show Original RGB alongside Active Spectrum for instant comparison!
      showOverlay: true,
      contrast: 118,
      brightness: 4,
      sharpness: 135,
      threshold: 128,
      handSide: "right",
      customPalmDataUrl: null,
      customThumbDataUrl: null
    };

    const srcCanvas = document.createElement("canvas");
    generateRealisticSamplePalm(srcCanvas);

    const specButtonsHtml = SPECTRUMS.map((s, idx) => `
      <button type="button" class="btn pv-spec-btn" data-spec-idx="${idx}" style="padding:7px 11px;font-size:12.5px;font-weight:700;border-radius:6px;cursor:pointer;">
        ${s.short}
      </button>
    `).join("");

    root.innerHTML = `
      <div class="pv-studio" style="border:2px solid #cbd5e1;border-radius:12px;background:#ffffff;padding:16px;box-shadow:0 4px 16px rgba(15,23,42,0.06);">
        <!-- 1. Photo Upload & Live Camera Bar -->
        <div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;padding:12px 14px;background:linear-gradient(135deg,#f5f3ff 0%,#ede9fe 100%);border:1px solid #ddd6fe;border-radius:8px;margin-bottom:14px;">
          <div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center;">
            <label class="btn" style="background:#6d28d9;color:#fff;padding:8px 14px;font-size:13px;font-weight:700;border-radius:6px;cursor:pointer;">
              📷 Upload Palm Photo
              <input type="file" class="pv-file-palm" accept="image/*" style="display:none;">
            </label>
            <label class="btn" style="background:#0f766e;color:#fff;padding:8px 14px;font-size:13px;font-weight:700;border-radius:6px;cursor:pointer;">
              👍 Upload Thumbprint Close-Up
              <input type="file" class="pv-file-thumb" accept="image/*" style="display:none;">
            </label>
            <button type="button" class="btn pv-btn-camera" style="background:#1e40af;color:#fff;padding:8px 14px;font-size:13px;font-weight:700;border-radius:6px;">
              🎥 Use Live Camera
            </button>
            <button type="button" class="btn pv-btn-sample" style="background:#475569;color:#fff;padding:8px 12px;font-size:12.5px;border-radius:6px;">
              ✋ Reset to High-Res Sample Palm
            </button>
          </div>
          <div style="display:flex;align-items:center;gap:10px;">
            <label style="font-size:13px;font-weight:700;color:#1e293b;">
              Hand:
              <select class="pv-hand-side" style="padding:5px 8px;border:1px solid #94a3b8;border-radius:6px;font-weight:600;">
                <option value="right">Right Hand (Active Karma)</option>
                <option value="left">Left Hand (Inherited Potential)</option>
              </select>
            </label>
          </div>
        </div>

        <!-- Hidden Live Webcam Capture Modal -->
        <div class="pv-camera-box" style="display:none;margin-bottom:14px;padding:12px;background:#0f172a;color:#fff;border-radius:8px;text-align:center;">
          <video class="pv-video" autoplay playsinline style="max-width:420px;width:100%;border-radius:8px;border:2px solid #38bdf8;"></video>
          <div style="margin-top:10px;display:flex;gap:10px;justify-content:center;">
            <button type="button" class="btn pv-btn-snap" style="background:#16a34a;color:#fff;font-weight:700;">📸 Snap Palm / Thumb Photo</button>
            <button type="button" class="btn pv-btn-cam-close" style="background:#dc2626;color:#fff;">✖ Close Camera</button>
          </div>
        </div>

        <!-- 2. Instant Multi-Spectrum Switcher Bar (Switch Back & Forth Across All 10 Modes!) -->
        <div style="padding:12px 14px;background:#0f172a;color:#f8fafc;border-radius:10px;margin-bottom:14px;">
          <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px;margin-bottom:10px;">
            <div>
              <strong style="font-size:14px;color:#fde047;">🔬 Multi-Spectrum &amp; Color-Channel Switcher (Click Any Spectrum or Use ◀ / ▶ to Flip Back &amp; Forth):</strong>
              <div class="pv-active-spec-desc" style="font-size:12.5px;color:#cbd5e1;margin-top:2px;"></div>
            </div>
            <div style="display:flex;gap:8px;align-items:center;">
              <button type="button" class="btn pv-btn-prev" style="background:#334155;color:#fff;padding:6px 12px;font-size:12.5px;font-weight:700;">◀ Prev Spectrum</button>
              <button type="button" class="btn pv-btn-next" style="background:#f59e0b;color:#111827;padding:6px 12px;font-size:12.5px;font-weight:800;">Next Spectrum ▶</button>
            </div>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px;">
            ${specButtonsHtml}
          </div>

          <!-- Fine-Tuning Sliders & Split View Toggle -->
          <div style="display:flex;flex-wrap:wrap;gap:16px;align-items:center;padding-top:10px;border-top:1px solid #334155;font-size:12px;">
            <label style="display:inline-flex;align-items:center;gap:6px;cursor:pointer;color:#fde047;font-weight:700;">
              <input type="checkbox" class="pv-chk-split" checked>
              🌗 Side-by-Side Split Compare (Original RGB vs. Selected Spectrum)
            </label>
            <label style="display:inline-flex;align-items:center;gap:6px;cursor:pointer;color:#4ade80;font-weight:700;">
              <input type="checkbox" class="pv-chk-overlay" checked>
              🎯 Show reference line labels
            </label>
            <label style="display:inline-flex;align-items:center;gap:6px;">
              Contrast: <input type="range" class="pv-rng-contrast" min="70" max="180" value="118" style="width:90px;">
            </label>
            <label style="display:inline-flex;align-items:center;gap:6px;">
              Ridge Sharpness: <input type="range" class="pv-rng-sharp" min="50" max="220" value="135" style="width:90px;">
            </label>
            <label style="display:inline-flex;align-items:center;gap:6px;">
              Brightness: <input type="range" class="pv-rng-bright" min="-40" max="40" value="4" style="width:80px;">
            </label>
          </div>
        </div>

        <!-- 3. Interactive Multi-Spectrum Viewport + Dedicated Nadi Thumbprint Macro Loupe -->
        <div class="pv-viewport-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(275px,1fr));gap:14px;margin-bottom:16px;">
          <div class="pv-orig-panel" style="background:#0f172a;border:2px solid #334155;border-radius:10px;padding:10px;text-align:center;">
            <div style="font-size:12.5px;font-weight:700;color:#e2e8f0;margin-bottom:6px;">🌈 Reference View: Original True-Color RGB</div>
            <canvas class="pv-canvas-orig" style="width:100%;max-width:360px;height:auto;border-radius:8px;border:1px solid #475569;"></canvas>
          </div>
          <div class="pv-spec-panel" style="background:#0f172a;border:2px solid #f59e0b;border-radius:10px;padding:10px;text-align:center;">
            <div class="pv-spec-panel-title" style="font-size:12.5px;font-weight:800;color:#fde047;margin-bottom:6px;">🔍 Active Diagnostic Spectrum</div>
            <canvas class="pv-canvas-spec" style="width:100%;max-width:360px;height:auto;border-radius:8px;border:1px solid #f59e0b;"></canvas>
          </div>
          <div class="pv-thumb-panel" style="background:#0f172a;border:2px solid #10b981;border-radius:10px;padding:10px;text-align:center;display:flex;flex-direction:column;justify-content:space-between;">
            <div>
              <div style="font-size:12.5px;font-weight:800;color:#6ee7b7;margin-bottom:6px;">👍 Nadi Thumbprint 4x Macro Ridge Scanner</div>
              <canvas class="pv-canvas-thumb" width="260" height="260" style="width:100%;max-width:250px;height:auto;border-radius:50%;border:3px solid #10b981;background:#111827;"></canvas>
            </div>
            <div style="margin-top:8px;padding:8px;background:#1e293b;border-radius:6px;text-align:left;font-size:12px;color:#e2e8f0;">
              <div><b style="color:#6ee7b7;">Nadi Rekha Pattern:</b> <span class="pv-thumb-label">Chakra Whorl / Shankha Loop</span></div>
              <div style="margin-top:4px;font-size:11.5px;color:#94a3b8;">Switch between <b>UV Micro-Ridge (#5)</b>, <b>Edge Skeleton (#6)</b>, and <b>Ink Stamp (#7)</b> above to inspect fine papillary thumbprint ridges!</div>
            </div>
          </div>
        </div>

        <!-- 4. Live Vision Analysis Report Container -->
        <div class="pv-report-container"></div>
      </div>
    `;

    const origCanvas = root.querySelector(".pv-canvas-orig");
    const specCanvas = root.querySelector(".pv-canvas-spec");
    const thumbCanvas = root.querySelector(".pv-canvas-thumb");
    const origPanel = root.querySelector(".pv-orig-panel");
    const specTitleEl = root.querySelector(".pv-spec-panel-title");
    const specDescEl = root.querySelector(".pv-active-spec-desc");
    const reportEl = root.querySelector(".pv-report-container");

    function updateSpectrumUI() {
      const s = SPECTRUMS[state.activeSpectrumIdx];
      specTitleEl.textContent = s.title;
      specDescEl.innerHTML = `<b style="color:#38bdf8;">${s.title}:</b> ${s.desc}`;
      origPanel.style.display = state.splitCompare ? "block" : "none";

      root.querySelectorAll(".pv-spec-btn").forEach((btn, idx) => {
        if (idx === state.activeSpectrumIdx) {
          btn.style.background = "#f59e0b";
          btn.style.color = "#111827";
          btn.style.border = "2px solid #fde047";
        } else {
          btn.style.background = "#1e293b";
          btn.style.color = "#e2e8f0";
          btn.style.border = "1px solid #475569";
        }
      });

      const w = srcCanvas.width;
      const h = srcCanvas.height;
      origCanvas.width = w;
      origCanvas.height = h;
      specCanvas.width = w;
      specCanvas.height = h;

      const sCtx = srcCanvas.getContext("2d");
      const rawData = sCtx.getImageData(0, 0, w, h);

      // 1. Render Original RGB on left canvas
      const origCtx = origCanvas.getContext("2d");
      origCtx.putImageData(rawData, 0, 0);

      // 2. Render Selected Spectrum on right canvas
      const specCtx = specCanvas.getContext("2d");
      const processed = processSpectrumPixels(rawData, s.id, state);
      specCtx.putImageData(processed, 0, 0);

      if ((state.showOverlay || s.id === "annotated_overlay") && !state.customPalmDataUrl) {
        drawAnnotatedOverlay(specCtx, w, h);
      }

      // 3. Render 4x Thumbprint Macro Loupe in the active spectrum!
      const tCtx = thumbCanvas.getContext("2d");
      tCtx.clearRect(0, 0, thumbCanvas.width, thumbCanvas.height);
      if (state.customThumbDataUrl && window._pvCustomThumbCanvas) {
        const tc = window._pvCustomThumbCanvas;
        const td = tc.getContext("2d").getImageData(0, 0, tc.width, tc.height);
        const tp = processSpectrumPixels(td, s.id === "original" ? "ridge_enhance" : s.id, state);
        const tmp = document.createElement("canvas");
        tmp.width = tc.width;
        tmp.height = tc.height;
        tmp.getContext("2d").putImageData(tp, 0, 0);
        tCtx.drawImage(tmp, 0, 0, thumbCanvas.width, thumbCanvas.height);
      } else {
        // Crop & 4x zoom into the thumb tip region of the processed spectrum canvas
        const sx = state.customPalmDataUrl ? Math.round(w * 0.10) : 48;
        const sy = state.customPalmDataUrl ? Math.round(h * 0.42) : 335;
        const sw = state.customPalmDataUrl ? Math.round(w * 0.22) : 95;
        const sh = state.customPalmDataUrl ? Math.round(h * 0.22) : 95;
        tCtx.drawImage(specCanvas, sx, sy, sw, sh, 0, 0, thumbCanvas.width, thumbCanvas.height);
      }
    }

    // Spectrum button clicks
    root.querySelectorAll(".pv-spec-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        state.activeSpectrumIdx = parseInt(btn.getAttribute("data-spec-idx"), 10) || 0;
        updateSpectrumUI();
      });
    });

    root.querySelector(".pv-btn-prev").addEventListener("click", () => {
      state.activeSpectrumIdx = (state.activeSpectrumIdx - 1 + SPECTRUMS.length) % SPECTRUMS.length;
      updateSpectrumUI();
    });
    root.querySelector(".pv-btn-next").addEventListener("click", () => {
      state.activeSpectrumIdx = (state.activeSpectrumIdx + 1) % SPECTRUMS.length;
      updateSpectrumUI();
    });

    root.querySelector(".pv-chk-split").addEventListener("change", e => {
      state.splitCompare = e.target.checked;
      updateSpectrumUI();
    });
    root.querySelector(".pv-chk-overlay").addEventListener("change", e => {
      state.showOverlay = e.target.checked;
      updateSpectrumUI();
    });
    root.querySelector(".pv-rng-contrast").addEventListener("input", e => {
      state.contrast = parseInt(e.target.value, 10) || 100;
      updateSpectrumUI();
    });
    root.querySelector(".pv-rng-sharp").addEventListener("input", e => {
      state.sharpness = parseInt(e.target.value, 10) || 100;
      updateSpectrumUI();
    });
    root.querySelector(".pv-rng-bright").addEventListener("input", e => {
      state.brightness = parseInt(e.target.value, 10) || 0;
      updateSpectrumUI();
    });
    root.querySelector(".pv-hand-side").addEventListener("change", e => {
      state.handSide = e.target.value;
      runServerAnalysis();
    });

    // File upload: Palm Photo
    root.querySelector(".pv-file-palm").addEventListener("change", e => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = ev => {
        const img = new Image();
        img.onload = () => {
          const maxDim = 760;
          const scale = Math.min(1, maxDim / Math.max(img.width, img.height));
          srcCanvas.width = Math.max(200, Math.round(img.width * scale));
          srcCanvas.height = Math.max(200, Math.round(img.height * scale));
          srcCanvas.getContext("2d").drawImage(img, 0, 0, srcCanvas.width, srcCanvas.height);
          state.customPalmDataUrl = srcCanvas.toDataURL("image/jpeg", 0.85);
          updateSpectrumUI();
          runServerAnalysis();
        };
        img.src = ev.target.result;
      };
      reader.readAsDataURL(file);
    });

    // File upload: Thumbprint Close-Up
    root.querySelector(".pv-file-thumb").addEventListener("change", e => {
      const file = e.target.files && e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = ev => {
        const img = new Image();
        img.onload = () => {
          const tc = document.createElement("canvas");
          tc.width = 260;
          tc.height = 260;
          tc.getContext("2d").drawImage(img, 0, 0, 260, 260);
          window._pvCustomThumbCanvas = tc;
          state.customThumbDataUrl = tc.toDataURL("image/jpeg", 0.85);
          updateSpectrumUI();
          runServerAnalysis();
        };
        img.src = ev.target.result;
      };
      reader.readAsDataURL(file);
    });

    // Reset to High-Res Sample Palm
    root.querySelector(".pv-btn-sample").addEventListener("click", () => {
      state.customPalmDataUrl = null;
      state.customThumbDataUrl = null;
      window._pvCustomThumbCanvas = null;
      generateRealisticSamplePalm(srcCanvas);
      updateSpectrumUI();
      runServerAnalysis();
    });

    // Live Webcam Capture
    let activeStream = null;
    const camBox = root.querySelector(".pv-camera-box");
    const videoEl = root.querySelector(".pv-video");
    root.querySelector(".pv-btn-camera").addEventListener("click", async () => {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert("Camera access is not supported in this browser window; please use Upload Palm Photo.");
        return;
      }
      try {
        activeStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
        videoEl.srcObject = activeStream;
        camBox.style.display = "block";
      } catch (err) {
        alert("Unable to open camera: " + err.message);
      }
    });
    root.querySelector(".pv-btn-snap").addEventListener("click", () => {
      if (!videoEl.videoWidth) return;
      srcCanvas.width = videoEl.videoWidth;
      srcCanvas.height = videoEl.videoHeight;
      srcCanvas.getContext("2d").drawImage(videoEl, 0, 0);
      state.customPalmDataUrl = srcCanvas.toDataURL("image/jpeg", 0.85);
      if (activeStream) activeStream.getTracks().forEach(t => t.stop());
      camBox.style.display = "none";
      updateSpectrumUI();
      runServerAnalysis();
    });
    root.querySelector(".pv-btn-cam-close").addEventListener("click", () => {
      if (activeStream) activeStream.getTracks().forEach(t => t.stop());
      camBox.style.display = "none";
    });

    async function runServerAnalysis() {
      const payload = {
        image_base64: state.customPalmDataUrl || null,
        thumb_image_base64: state.customThumbDataUrl || null,
        hand_side: state.handSide,
        active_spectrum: SPECTRUMS[state.activeSpectrumIdx].id
      };
      if (birthMeta && birthMeta.date) {
        payload.birth_date = birthMeta.date;
        payload.birth_time = birthMeta.time || "12:00:00";
        payload.latitude = birthMeta.lat;
        payload.longitude = birthMeta.lon;
        payload.timezone = birthMeta.tz;
      }
      if (!payload.image_base64 && !payload.thumb_image_base64) {
        reportEl.innerHTML = `<div style="padding:12px;background:#fff7ed;border:1px solid #fdba74;border-radius:8px;">Upload or snap a palm before asking for a reading. The sample drawing is not a hand.</div>`;
        return;
      }
      try {
        const r = await fetch("/api/palmistry/analyze-photo", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (!r.ok) {
          reportEl.innerHTML = `<div style="padding:12px;background:#fff7ed;border:1px solid #fdba74;border-radius:8px;">That photo could not be read as a palm. Upload a clearer picture or enter the lines yourself.</div>`;
          return;
        }
        const data = await r.json();
        if (data.extracted_palm_profile) {
          const prof = Object.assign({}, data.extracted_palm_profile, {
            has_uploaded_photo: Boolean(state.customPalmDataUrl || state.customThumbDataUrl),
            saved_at: new Date().toISOString()
          });
          try {
            localStorage.setItem("panchang_palm_profile", JSON.stringify(prof));
          } catch (err) {}
        }
        renderVisionReport(data);
      } catch (e) {}
    }

    function renderVisionReport(data) {
      const thumbEl = root.querySelector(".pv-thumb-label");
      if (thumbEl && data.nadi_thumbprint_analysis) {
        thumbEl.textContent = data.nadi_thumbprint_analysis.name;
      }
      const cp = data.core_palmistry_reading || {};
      const bm = data.vision_biometric_metrics || {};
      const nt = data.nadi_thumbprint_analysis || {};
      const dh = data.ayurvedic_tridosha_hand_signature || {};

      const minorRows = (data.extended_minor_lines_and_marks || []).map(m => `
        <tr>
          <td><strong>${m.line_name}</strong></td>
          <td><span class="badge" style="background:#eff6ff;color:#1d4ed8;">${m.spectrum_best_viewed_in}</span></td>
          <td>${m.reading}</td>
        </tr>
      `).join("");

      const mountRows = (data.birth_chart_and_lal_kitab_mount_links || []).map(m => `
        <tr>
          <td><strong>${m.planet}</strong><br><small>${m.natal_chart_placement}</small></td>
          <td><b>${m.palm_mount_and_line}</b><br><small class="neutral">Lal Kitab: ${m.lal_kitab_pakka_ghar}</small></td>
          <td><small>${m.how_mount_and_chart_interact}</small></td>
        </tr>
      `).join("");

      reportEl.innerHTML = `
        <div class="grid-3" style="margin-bottom:16px;">
          <div class="stat">
            <span class="label">Detected Elemental &amp; Ayurvedic Hand</span>
            <span class="value" style="font-size:1.1rem;color:#6d28d9;">${(cp.hand_shape && cp.hand_shape.type ? cp.hand_shape.type.toUpperCase() : "FIRE")} HAND</span>
            <small><b>${dh.ayurvedic_hand_type || ""}</b><br>${data.extracted_palm_profile && data.extracted_palm_profile.detection_method ? data.extracted_palm_profile.detection_method : "not measured"} · confidence ${data.extracted_palm_profile && data.extracted_palm_profile.confidence != null ? data.extracted_palm_profile.confidence : 0}</small>
          </div>
          <div class="stat">
            <span class="label">Nadi Thumbprint (Angushtha Rekha)</span>
            <span class="value" style="font-size:1.05rem;color:#0f766e;">${nt.name || "Chakra Rekha"}</span>
            <small><b>${nt.deity_and_planet || ""}</b><br>${nt.ridge_geometry || ""}</small>
          </div>
          <div class="stat">
            <span class="label">Ayurvedic Hand Balancing Tip</span>
            <span class="value" style="font-size:0.95rem;">Tridosha Hand Care</span>
            <small>${dh.balancing_tip || ""}</small>
          </div>
        </div>

        <div style="padding:14px 16px;background:linear-gradient(135deg,#f0fdf4 0%,#dcfce7 100%);border:1px solid #86efac;border-radius:8px;margin-bottom:16px;">
          <h4 style="margin:0 0 6px 0;color:#166534;">👍 Nadi Palm-Leaf Thumbprint Reading (${nt.name || ""})</h4>
          <p style="margin:0 0 6px 0;font-size:13.5px;line-height:1.6;">${nt.nadi_leaf_interpretation || ""}</p>
          <div style="font-size:13px;color:#14532d;"><b>Strength:</b> ${nt.karmic_strength || ""} | <b>Remedy:</b> ${nt.nadi_remedy || ""}</div>
        </div>

        <h3>✋ Primary 4 Major Palm Lines Detected</h3>
        <div class="table-wrap" style="margin-bottom:16px;">
          <table>
            <thead>
              <tr>
                <th>Major Line</th>
                <th>Detected Morphology</th>
                <th>Detailed Samudrika Shastra &amp; Psychological Reading</th>
              </tr>
            </thead>
            <tbody>
              <tr><td><strong>Heart Line (Hridaya Rekha)</strong></td><td><span class="badge">${cp.lines?.heart?.feature || "Curved"}</span></td><td>${cp.lines?.heart?.reading || ""}</td></tr>
              <tr><td><strong>Head Line (Mastishka Rekha)</strong></td><td><span class="badge">${cp.lines?.head?.feature || "Long"}</span></td><td>${cp.lines?.head?.reading || ""}</td></tr>
              <tr><td><strong>Life Line (Jeevana Rekha)</strong></td><td><span class="badge">${cp.lines?.life?.feature || "Deep"}</span></td><td>${cp.lines?.life?.reading || ""}</td></tr>
              <tr><td><strong>Fate / Saturn Line (Bhagya Rekha)</strong></td><td><span class="badge">${cp.lines?.fate?.feature || "Clear"}</span></td><td>${cp.lines?.fate?.reading || ""}</td></tr>
            </tbody>
          </table>
        </div>

        <h3>🔬 Secondary Lines, Wrist Bracelets &amp; Best Spectrum to View Each</h3>
        <div class="table-wrap" style="margin-bottom:16px;">
          <table>
            <thead>
              <tr>
                <th>Secondary Line / Mark</th>
                <th>Recommended Spectrum Mode</th>
                <th>Interpretation</th>
              </tr>
            </thead>
            <tbody>${minorRows}</tbody>
          </table>
        </div>

        ${mountRows ? `
        <h3>🔗 Birth-Chart &amp; Lal Kitab 9-Planetary Mounts Cross-Link</h3>
        <div class="table-wrap" style="margin-bottom:18px;">
          <table>
            <thead>
              <tr>
                <th>Planet &amp; Natal House</th>
                <th>Corresponding Palm Mount &amp; Lal Kitab Pakka Ghar</th>
                <th>How Your Palm Mount &amp; Birth Chart Interact + 43-Day Upaya</th>
              </tr>
            </thead>
            <tbody>${mountRows}</tbody>
          </table>
        </div>
        ` : ""}

        ${data.palm_and_astrology_synthesis && data.palm_and_astrology_synthesis.headline ? `
        <div style="padding:16px;background:linear-gradient(135deg,#faf5ff 0%,#f3e8ff 100%);border:1.5px solid #c084fc;border-radius:10px;margin-bottom:18px;">
          <h3 style="margin:0 0 8px 0;color:#581c87;">🌟 ${data.palm_and_astrology_synthesis.headline}</h3>
          <p style="margin:0 0 8px 0;font-size:13.5px;line-height:1.6;color:#3b0764;">
            <b>Elemental &amp; Birth-Chart Fusion:</b> ${data.palm_and_astrology_synthesis.elemental_chart_fusion || ""}
          </p>
          <p style="margin:0 0 12px 0;font-size:13px;line-height:1.55;color:#4c1d95;">
            <b>Nadi Thumbprint × Natal Dharma:</b> ${data.palm_and_astrology_synthesis.thumbprint_and_natal_dharma_fusion || ""}
          </p>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Major Palm Line</th>
                  <th>Linked Birth-Chart Houses &amp; Planets</th>
                  <th>Combined Palm + Astrology Synthesis</th>
                  <th>Combined Hasta-Jyotish Remedy</th>
                </tr>
              </thead>
              <tbody>
                ${(data.palm_and_astrology_synthesis.four_lines_and_natal_houses_matrix || []).map(row => `
                  <tr>
                    <td><strong>${row.palm_line}</strong></td>
                    <td><span class="badge" style="background:#ede9fe;color:#5b21b6;">${row.natal_chart_factors}</span></td>
                    <td>${row.combined_palm_astrology_reading}</td>
                    <td><small>${row.combined_remedy}</small></td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        </div>
        ` : ""}

        ${data.palm_and_vastu_synthesis && data.palm_and_vastu_synthesis.headline ? `
        <div style="padding:16px;background:linear-gradient(135deg,#f0fdf4 0%,#dcfce7 100%);border:1.5px solid #4ade80;border-radius:10px;margin-bottom:12px;">
          <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px;margin-bottom:8px;">
            <h3 style="margin:0;color:#14532d;">🏡 ${data.palm_and_vastu_synthesis.headline}</h3>
            <a class="btn" style="background:#0f766e;color:#fff;padding:7px 14px;font-size:12.5px;font-weight:800;border-radius:6px;text-decoration:none;"
               href="/vastu?date=${encodeURIComponent((birthMeta && birthMeta.date) || '1990-05-15')}&time=${encodeURIComponent(((birthMeta && birthMeta.time) || '10:30').slice(0,5))}&lat=${encodeURIComponent((birthMeta && birthMeta.lat) || 28.6139)}&lon=${encodeURIComponent((birthMeta && birthMeta.lon) || 77.2090)}&tz=${encodeURIComponent((birthMeta && birthMeta.tz) || 'Asia/Kolkata')}">
              🏗️ Open Interactive Vastu &amp; Feng Shui Studio with This Palm + Birth Chart →
            </a>
          </div>
          <p style="margin:0 0 12px 0;font-size:13px;line-height:1.55;color:#166534;">
            ${data.palm_and_vastu_synthesis.summary || ""}
          </p>
          <h4 style="margin:0 0 6px 0;color:#15803d;">✋ Your Palm Lines &amp; Hand Element → Ideal Vastu &amp; Feng Shui Room Adjustments</h4>
          <div class="table-wrap" style="margin-bottom:14px;">
            <table>
              <thead>
                <tr>
                  <th>Detected Palm Feature</th>
                  <th>Birth-Chart Link</th>
                  <th>Personalized Vastu &amp; Feng Shui Prescription for Your Home</th>
                </tr>
              </thead>
              <tbody>
                ${(data.palm_and_vastu_synthesis.palm_line_vastu_room_prescriptions || []).map(pr => `
                  <tr>
                    <td><strong>${pr.palm_feature}</strong></td>
                    <td><b>${pr.birth_chart_link}</b></td>
                    <td>${pr.vastu_and_feng_shui_prescription}</td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>

          <h4 style="margin:0 0 6px 0;color:#15803d;">🧭 9 Planetary Palm Mounts ↔ 9 Vastu Compass Zones &amp; Home Fixtures</h4>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Planet &amp; Palm Mount</th>
                  <th>Natal Chart Placement</th>
                  <th>Corresponding Vastu Compass Zone &amp; Rooms</th>
                  <th>Combined Palm + Chart + Vastu Action</th>
                </tr>
              </thead>
              <tbody>
                ${(data.palm_and_vastu_synthesis.nine_palm_mounts_to_nine_vastu_zones || []).map(mz => `
                  <tr>
                    <td><strong>${mz.planet}</strong><br><small>${mz.palm_mount}</small></td>
                    <td><span class="badge">${mz.natal_chart_placement}</span></td>
                    <td><b>${mz.vastu_compass_zone}</b><br><small class="neutral">${mz.key_vastu_rooms_and_fixtures}</small></td>
                    <td><small>${mz.palm_chart_vastu_action}</small></td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        </div>
        ` : ""}
      `;
    }

    updateSpectrumUI();
    runServerAnalysis();
  };

  function autoMount() {
    const el = document.getElementById("palmistry-vision-studio-root");
    if (!el) return;
    window.initPalmistryVisionStudio("palmistry-vision-studio-root", {
      date: el.getAttribute("data-date") || "1990-05-15",
      time: el.getAttribute("data-time") || "10:30:00",
      lat: parseFloat(el.getAttribute("data-lat") || "28.6139"),
      lon: parseFloat(el.getAttribute("data-lon") || "77.2090"),
      tz: el.getAttribute("data-tz") || "Asia/Kolkata"
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", autoMount);
  } else {
    autoMount();
  }
})();
