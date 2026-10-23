/**
 * Interactive Visual House (Square / Rectangle) & Outer-Lot Vastu + Feng Shui Architect Studio
 * Supports:
 * - 38+ Indoor Rooms, Sacred Spaces, Appliances (Stove, Taps, Washer/Dryer, Gym, Medication Cabinet, Grain Pantry),
 *   Wall Hangings & Photo Frames (Living Members, Deceased Ancestors, Gods/Deities, TV Screen, Mirror, Clock),
 *   and Outdoor Lot / Boundary Items (Main Gate, Parking Gate, Side Gate, Sliding/Swinging Gate Mechanics,
 *   Trench/Ditch inside or outside property boundary with drainage flow direction, Water Hose, Kids Slide,
 *   Overhead Tank, Pool/Well, Septic, Fireplace, Trees, Bushes, Flowers, Garden, Grass).
 * - Interactive Wall Line Drawing ("Draw Wall by Line" click-drag tool with 90° ortho snap).
 * - Interactive Perimeter Fence Loop Builder (Closed 360° Loop or Open Loop with selectable open side, or custom drawn loop).
 * - Automatic initialization with Personalized Birth-Chart Ideal Vastu & Feng Shui Arrangement.
 * - Explicit "Evaluate" button workflow: edits stage cleanly until the user presses "Evaluate".
 */
(function () {
  const CATALOG = {
    // Category 1: Indoor Rooms, Doors & Sacred Spaces
    entrance:              { label: "Main Entrance Door",      icon: "🚪", cat: "indoor_rooms", scope: "indoor", w: 13, h: 7,  hasDoor: true,  defaultDoor: "NE", hasGateMech: true,  defaultGateMech: "swing_in_cw", bg: "#fef3c7", border: "#d97706" },
    back_door:             { label: "Back / Utility Door",     icon: "🚪", cat: "indoor_rooms", scope: "indoor", w: 11, h: 6,  hasDoor: true,  defaultDoor: "NW", hasGateMech: true,  defaultGateMech: "swing_in_cw", bg: "#f1f5f9", border: "#64748b" },
    puja_room:             { label: "Temple / Prayer Hall",    icon: "🛕", cat: "indoor_rooms", scope: "indoor", w: 11, h: 10, hasDoor: true,  defaultDoor: "E",  bg: "#fef08a", border: "#b45309" },
    meditation_hall:       { label: "Meditation / Yoga Hall",  icon: "🧘", cat: "indoor_rooms", scope: "indoor", w: 11, h: 10, hasDoor: true,  defaultDoor: "E",  bg: "#e0e7ff", border: "#4338ca" },
    master_bedroom:        { label: "Master Bedroom",          icon: "🛏️", cat: "indoor_rooms", scope: "indoor", w: 20, h: 17, hasDoor: true,  defaultDoor: "N",  bg: "#ede9fe", border: "#7c3aed" },
    bedroom:               { label: "Bedroom (Kids/Family)",   icon: "🛌", cat: "indoor_rooms", scope: "indoor", w: 17, h: 15, hasDoor: true,  defaultDoor: "E",  bg: "#e0e7ff", border: "#4f46e5" },
    guest_room:            { label: "Guest Room",              icon: "🛋️", cat: "indoor_rooms", scope: "indoor", w: 16, h: 14, hasDoor: true,  defaultDoor: "E",  bg: "#fae8ff", border: "#a21caf" },
    living_room:           { label: "Living Room",             icon: "🛋️", cat: "indoor_rooms", scope: "indoor", w: 22, h: 18, hasDoor: true,  defaultDoor: "E",  bg: "#e0f2fe", border: "#0284c7" },
    kitchen:               { label: "Kitchen Room",            icon: "🍳", cat: "indoor_rooms", scope: "indoor", w: 17, h: 15, hasDoor: true,  defaultDoor: "E",  bg: "#ffedd5", border: "#ea580c" },
    dining_room:           { label: "Dining Room",             icon: "🍽️", cat: "indoor_rooms", scope: "indoor", w: 15, h: 13, hasDoor: false, defaultDoor: "",   bg: "#fef9c3", border: "#ca8a04" },
    study_room:            { label: "Study / Office",          icon: "💻", cat: "indoor_rooms", scope: "indoor", w: 14, h: 12, hasDoor: true,  defaultDoor: "NE", bg: "#dbeafe", border: "#2563eb" },
    bathroom:              { label: "Bathroom / Toilet",       icon: "🚿", cat: "indoor_rooms", scope: "indoor", w: 11, h: 11, hasDoor: true,  defaultDoor: "E",  bg: "#cffafe", border: "#0891b2" },
    gym_room:              { label: "Gym / Workout Area",      icon: "🏋️", cat: "indoor_rooms", scope: "indoor", w: 13, h: 11, hasDoor: true,  defaultDoor: "E",  bg: "#fee2e2", border: "#dc2626" },
    storage:               { label: "Heavy Storage Room",      icon: "📦", cat: "indoor_rooms", scope: "indoor", w: 12, h: 11, hasDoor: true,  defaultDoor: "N",  bg: "#f3f4f6", border: "#4b5563" },
    grain_pantry:          { label: "Food & Grain Pantry",     icon: "🌾", cat: "indoor_rooms", scope: "indoor", w: 10, h: 9,  hasDoor: true,  defaultDoor: "E",  bg: "#fef3c7", border: "#b45309" },
    balcony:               { label: "Balcony / Veranda",       icon: "🌤️", cat: "indoor_rooms", scope: "indoor", w: 15, h: 7,  hasDoor: true,  defaultDoor: "N",  bg: "#ecfccb", border: "#65a30d" },
    staircase:             { label: "Staircase",               icon: "🪜", cat: "indoor_rooms", scope: "indoor", w: 12, h: 10, hasDoor: false, defaultDoor: "",   bg: "#e2e8f0", border: "#475569" },

    // Category 2: Indoor Appliances, Stove, Taps, Washer/Dryer & Medication
    kitchen_stove:         { label: "Kitchen Stove / Burner",  icon: "🔥", cat: "indoor_fixtures", scope: "indoor", w: 8,  h: 7,  hasDoor: true,  defaultDoor: "E",  bg: "#fed7aa", border: "#c2410c" },
    indoor_taps:           { label: "Water Taps / Sink",       icon: "🚰", cat: "indoor_fixtures", scope: "indoor", w: 8,  h: 6,  hasDoor: true,  defaultDoor: "NE", bg: "#bae6fd", border: "#0284c7" },
    washer_dryer:          { label: "Washer & Dryer",          icon: "🧺", cat: "indoor_fixtures", scope: "indoor", w: 9,  h: 8,  hasDoor: true,  defaultDoor: "E",  bg: "#e0f2fe", border: "#0369a1" },
    medication_cabinet:    { label: "Medication / Medicine",   icon: "💊", cat: "indoor_fixtures", scope: "indoor", w: 9,  h: 7,  hasDoor: true,  defaultDoor: "NE", bg: "#dcfce7", border: "#15803d" },
    safe_locker:           { label: "Cash Safe / Locker",      icon: "💰", cat: "indoor_fixtures", scope: "indoor", w: 9,  h: 8,  hasDoor: true,  defaultDoor: "N",  bg: "#fef08a", border: "#a16207" },
    shoe_rack:             { label: "Shoe Rack",               icon: "👟", cat: "indoor_fixtures", scope: "indoor", w: 8,  h: 6,  hasDoor: false, defaultDoor: "",   bg: "#e5e7eb", border: "#4b5563" },
    electrical_inverter:   { label: "Electrical / Inverter",   icon: "⚡", cat: "indoor_fixtures", scope: "indoor", w: 8,  h: 7,  hasDoor: false, defaultDoor: "",   bg: "#fef08a", border: "#ca8a04" },
    aquarium_indoor_water: { label: "Aquarium / Fountain",     icon: "🐠", cat: "indoor_fixtures", scope: "indoor", w: 9,  h: 7,  hasDoor: false, defaultDoor: "",   bg: "#cffafe", border: "#0891b2" },
    indoor_plants_tulsi:   { label: "Tulsi / Sacred Plant",    icon: "🪴", cat: "indoor_fixtures", scope: "indoor", w: 8,  h: 8,  hasDoor: false, defaultDoor: "",   bg: "#bbf7d0", border: "#16a34a" },

    // Category 3: Photo Frames (Living, Deceased, Gods), TV Screen, Mirror & Wall Clock
    photo_living:          { label: "Living Family Photo",     icon: "🖼️", cat: "wall_decor", scope: "indoor", w: 10, h: 6,  hasDoor: true,  defaultDoor: "N",  hasWallSide: true, defaultWallSide: "SW", bg: "#fce7f3", border: "#db2777" },
    photo_deceased:        { label: "Deceased Ancestors Photo",icon: "🕯️", cat: "wall_decor", scope: "indoor", w: 10, h: 6,  hasDoor: true,  defaultDoor: "N",  hasWallSide: true, defaultWallSide: "S",  bg: "#f3e8ff", border: "#7e22ce" },
    photo_gods:            { label: "Gods / Deities Photo",    icon: "🙏", cat: "wall_decor", scope: "indoor", w: 10, h: 6,  hasDoor: true,  defaultDoor: "E",  hasWallSide: true, defaultWallSide: "NE", bg: "#fef9c3", border: "#b45309" },
    tv_screen:             { label: "TV / Television Screen",  icon: "🖥️", cat: "wall_decor", scope: "indoor", w: 10, h: 6,  hasDoor: true,  defaultDoor: "E",  hasWallSide: true, defaultWallSide: "E",  bg: "#dbeafe", border: "#1d4ed8" },
    wall_mirror:           { label: "Wall / Dressing Mirror",  icon: "🪞", cat: "wall_decor", scope: "indoor", w: 9,  h: 6,  hasDoor: true,  defaultDoor: "E",  hasWallSide: true, defaultWallSide: "N",  bg: "#e0f2fe", border: "#0284c7" },
    wall_clock:            { label: "Wall Clock",              icon: "🕰️", cat: "wall_decor", scope: "indoor", w: 8,  h: 6,  hasDoor: true,  defaultDoor: "E",  hasWallSide: true, defaultWallSide: "N",  bg: "#f1f5f9", border: "#334155" },

    // Category 4: Outdoor Lot, Gates (Sliding / Swing), Trench / Ditch, Water Hose, Kids Slide & Landscaping
    gate:                  { label: "Main Lot Gate",           icon: "⛩️", cat: "outdoor", scope: "outdoor", w: 15, h: 6,  hasDoor: true,  defaultDoor: "NE", hasGateMech: true, defaultGateMech: "swing_in_cw", bg: "#fde68a", border: "#b45309" },
    parking_gate:          { label: "Parking / Driveway Gate", icon: "🚗", cat: "outdoor", scope: "outdoor", w: 17, h: 7,  hasDoor: true,  defaultDoor: "NW", hasGateMech: true, defaultGateMech: "slide_ne",    bg: "#cbd5e1", border: "#334155" },
    side_pedestrian_gate:  { label: "Side Pedestrian Gate",    icon: "🚶", cat: "outdoor", scope: "outdoor", w: 12, h: 6,  hasDoor: true,  defaultDoor: "E",  hasGateMech: true, defaultGateMech: "swing_in_cw", bg: "#fed7aa", border: "#c2410c" },
    trench_ditch:          { label: "Trench / Ditch / Drain",  icon: "🕳️", cat: "outdoor", scope: "outdoor", w: 18, h: 6,  hasDoor: false, defaultDoor: "",   hasFlowDir: true,  defaultFlowDir: "NE",        bg: "#bae6fd", border: "#0369a1" },
    water_hose:            { label: "Water Hose / Tap",        icon: "🚿", cat: "outdoor", scope: "outdoor", w: 10, h: 7,  hasDoor: true,  defaultDoor: "NE", bg: "#cffafe", border: "#0891b2" },
    kids_slide:            { label: "Kids Slide / Play Set",   icon: "🛝", cat: "outdoor", scope: "outdoor", w: 12, h: 10, hasDoor: true,  defaultDoor: "E",  bg: "#fef08a", border: "#ca8a04" },
    overhead_tank:         { label: "Overhead Water Tank",     icon: "🛢️", cat: "outdoor", scope: "outdoor", w: 12, h: 10, hasDoor: false, defaultDoor: "",   bg: "#e2e8f0", border: "#334155" },
    water_body:            { label: "Pool / Well / Sump",      icon: "💧", cat: "outdoor", scope: "outdoor", w: 14, h: 12, hasDoor: false, defaultDoor: "",   bg: "#bae6fd", border: "#0284c7" },
    septic_trash:          { label: "Trash / Septic Tank",     icon: "🗑️", cat: "outdoor", scope: "outdoor", w: 10, h: 9,  hasDoor: false, defaultDoor: "",   bg: "#e5e7eb", border: "#374151" },
    fireplace:             { label: "Outdoor Fireplace/BBQ",   icon: "🔥", cat: "outdoor", scope: "outdoor", w: 12, h: 12, hasDoor: false, defaultDoor: "",   bg: "#fed7aa", border: "#c2410c" },
    trees:                 { label: "Tall Heavy Trees",        icon: "🌳", cat: "outdoor", scope: "outdoor", w: 14, h: 14, hasDoor: false, defaultDoor: "",   bg: "#bbf7d0", border: "#15803d" },
    bushes:                { label: "Bushes / Shrubs",         icon: "🌿", cat: "outdoor", scope: "outdoor", w: 11, h: 15, hasDoor: false, defaultDoor: "",   bg: "#dcfce7", border: "#16a34a" },
    flowers:               { label: "Flower Bed",              icon: "🌸", cat: "outdoor", scope: "outdoor", w: 13, h: 11, hasDoor: false, defaultDoor: "",   bg: "#fbcfe8", border: "#db2777" },
    garden:                { label: "Veggie / Herb Garden",    icon: "🏡", cat: "outdoor", scope: "outdoor", w: 20, h: 9,  hasDoor: false, defaultDoor: "",   bg: "#d9f99d", border: "#4d7c0f" },
    grass:                 { label: "Grass Lawn",              icon: "🌱", cat: "outdoor", scope: "outdoor", w: 13, h: 24, hasDoor: false, defaultDoor: "",   bg: "#ecfccb", border: "#65a30d" },
    fence:                 { label: "Fence / Wall Segment",    icon: "🚧", cat: "outdoor", scope: "outdoor", w: 26, h: 5,  hasDoor: false, defaultDoor: "",   bg: "#e7e5e4", border: "#57534e" }
  };

  const DOOR_ARROWS = {
    N: "↑ N", NE: "↗ NE", E: "→ E", SE: "↘ SE",
    S: "↓ S", SW: "↙ SW", W: "← W", NW: "↖ NW"
  };

  const GATE_MECH_OPTIONS = [
    { value: "",             label: "Standard / Not Specified" },
    { value: "swing_in_cw",  label: "✅ Swing Inward Clockwise (Left-to-Right — Best)" },
    { value: "double_in",    label: "✅ Double-Leaf Opening Inward (Equal Leaves)" },
    { value: "slide_ne",     label: "✅ Sliding Gate/Door → Slides Toward North / East" },
    { value: "swing_in_ccw", label: "⚠️ Swing Inward Counter-Clockwise (Right-to-Left)" },
    { value: "slide_sw",     label: "⚠️ Sliding Gate/Door → Slides Toward South / West" },
    { value: "swing_out",    label: "❌ Swing Outward Toward Street (Leaks Prana/Wealth)" },
    { value: "rollup",       label: "🔄 Overhead Roll-Up / Automated Shutter" }
  ];

  const WALL_SIDE_OPTIONS = [
    { value: "",   label: "Not Mounted on Specific Wall" },
    { value: "N",  label: "Mounted on North Wall (Faces South)" },
    { value: "NE", label: "Mounted on North-East Wall (Faces SW)" },
    { value: "E",  label: "Mounted on East Wall (Faces West)" },
    { value: "SE", label: "Mounted on South-East Wall (Faces NW)" },
    { value: "S",  label: "Mounted on South Wall (Faces North — Required for Ancestors)" },
    { value: "SW", label: "Mounted on South-West Wall (Faces NE — Great for Family)" },
    { value: "W",  label: "Mounted on West Wall (Faces East)" },
    { value: "NW", label: "Mounted on North-West Wall (Faces SE)" }
  ];

  const FLOW_DIR_OPTIONS = [
    { value: "",         label: "Select Trench / Drainage Slope Direction..." },
    { value: "NE",       label: "✅ Slopes / Drains Toward North-East (Ishanya — Best)" },
    { value: "N",        label: "✅ Slopes / Drains Toward North (Kubera — Auspicious)" },
    { value: "E",        label: "✅ Slopes / Drains Toward East (Surya — Auspicious)" },
    { value: "NW",       label: "⚠️ Slopes / Drains Toward North-West" },
    { value: "SE",       label: "⚠️ Slopes / Drains Toward South-East" },
    { value: "W",        label: "❌ Slopes / Drains Toward West (Loss Defect)" },
    { value: "S",        label: "❌ Slopes / Drains Toward South (Yama Drain Defect)" },
    { value: "SW",       label: "❌ Slopes / Drains Toward South-West (Severe Nairutya Leak)" },
    { value: "stagnant", label: "❌ Open Pit / Stagnant Ditch (No Outflow)" }
  ];

  const IDEAL_MAP = {
    entrance: ["NE", "E", "N"],
    back_door: ["NW", "W", "E", "N"],
    puja_room: ["NE", "E", "N"],
    meditation_hall: ["NE", "E", "N"],
    master_bedroom: ["SW", "S"],
    bedroom: ["W", "S", "E", "NW"],
    guest_room: ["NW", "E", "N"],
    living_room: ["NE", "E", "N", "NW", "Center"],
    kitchen: ["SE", "NW"],
    dining_room: ["W", "E", "S", "N"],
    study_room: ["NE", "E", "N", "W"],
    bathroom: ["NW", "W", "S"],
    gym_room: ["SE", "S", "NW", "W"],
    storage: ["SW", "S", "W", "NW"],
    grain_pantry: ["NW", "SW", "S", "W"],
    balcony: ["NE", "N", "E"],
    staircase: ["SW", "S", "W"],
    kitchen_stove: ["SE", "E"],
    indoor_taps: ["NE", "N", "E"],
    washer_dryer: ["NW", "SE", "W"],
    medication_cabinet: ["NE", "N", "E"],
    safe_locker: ["SW", "S", "N"],
    shoe_rack: ["NW", "W", "SW"],
    electrical_inverter: ["SE", "NW", "S"],
    aquarium_indoor_water: ["NE", "N", "E"],
    indoor_plants_tulsi: ["NE", "E", "N"],
    photo_living: ["SW", "W", "E", "N", "NW"],
    photo_deceased: ["S", "SW"],
    photo_gods: ["NE", "E", "N"],
    tv_screen: ["E", "N", "SE", "NW"],
    wall_mirror: ["N", "E", "NE"],
    wall_clock: ["N", "E", "NE"],
    gate: ["NE", "E", "N"],
    parking_gate: ["NW", "SE", "E", "N"],
    side_pedestrian_gate: ["E", "N", "NE", "NW"],
    trench_ditch: ["NE", "N", "E"],
    water_hose: ["NE", "N", "E"],
    kids_slide: ["NE", "E", "N", "NW"],
    overhead_tank: ["SW", "W", "S"],
    water_body: ["NE", "N", "E"],
    septic_trash: ["NW", "W"],
    fireplace: ["SE", "S", "NW"],
    trees: ["SW", "S", "W"],
    bushes: ["NW", "W", "S", "SE", "SW"],
    flowers: ["NE", "E", "N", "NW", "SE"],
    garden: ["N", "E", "NE", "NW"],
    grass: ["NE", "N", "E", "NW"],
    fence: ["SW", "S", "W", "N", "E", "NE", "NW", "SE"]
  };

  const BAD_MAP = {
    entrance: ["SW", "S", "SE", "Center"],
    back_door: ["SW", "S", "Center"],
    puja_room: ["S", "SW", "SE", "NW"],
    meditation_hall: ["SE", "SW", "NW"],
    master_bedroom: ["NE", "SE", "NW", "Center", "E", "N"],
    bedroom: ["NE", "SE", "Center"],
    guest_room: ["SW", "Center", "NE"],
    living_room: ["SW", "SE"],
    kitchen: ["NE", "SW", "N", "W", "Center"],
    dining_room: ["SW", "NE", "Center"],
    study_room: ["SE", "Center"],
    bathroom: ["NE", "SW", "Center", "N"],
    gym_room: ["NE", "Center", "N"],
    storage: ["NE", "E", "N", "Center"],
    grain_pantry: ["NE", "Center"],
    balcony: ["SW", "S", "W", "SE", "Center"],
    staircase: ["NE", "Center", "N", "E"],
    kitchen_stove: ["NE", "N", "SW", "Center", "W"],
    indoor_taps: ["SE", "SW", "S", "Center"],
    washer_dryer: ["NE", "SW", "Center"],
    medication_cabinet: ["SW", "S", "SE", "NW", "Center"],
    safe_locker: ["SE", "NW", "NE", "Center", "E"],
    shoe_rack: ["NE", "E", "N", "Center", "SE"],
    electrical_inverter: ["NE", "N", "SW", "Center"],
    aquarium_indoor_water: ["SE", "SW", "S", "Center"],
    indoor_plants_tulsi: ["SW", "S"],
    photo_living: ["S", "SE"],
    photo_deceased: ["NE", "N", "E", "Center", "NW", "W", "SE"],
    photo_gods: ["S", "SW", "SE", "NW"],
    tv_screen: ["SW", "Center"],
    wall_mirror: ["S", "SW", "SE", "W"],
    wall_clock: ["S", "SW"],
    gate: ["SW", "S", "SE", "Center"],
    parking_gate: ["SW", "NE", "Center"],
    side_pedestrian_gate: ["SW", "S", "SE"],
    trench_ditch: ["SW", "S", "W", "SE", "Center"],
    water_hose: ["SW", "SE", "S", "Center"],
    kids_slide: ["SW", "S", "Center"],
    overhead_tank: ["NE", "N", "E", "Center", "SE"],
    water_body: ["SW", "S", "SE", "W", "Center"],
    septic_trash: ["NE", "N", "E", "SW", "Center"],
    fireplace: ["NE", "N", "SW", "W", "Center"],
    trees: ["NE", "N", "E", "Center"],
    bushes: ["NE", "Center"],
    flowers: ["Center"],
    garden: ["Center"],
    grass: [],
    fence: []
  };

  function getStandardIdealPreset() {
    return {
      preset_title: "Classical Ideal Vastu & Feng Shui Blueprint (100% Harmonized)",
      items: [
        { id: 1,  type: "entrance",           label: "Main Entrance Door",          x: 68, y: 16, w: 13, h: 6,  door_dir: "NE", gate_mech: "swing_in_cw", scope: "indoor" },
        { id: 2,  type: "puja_room",          label: "Temple / Prayer Hall",        x: 70, y: 23, w: 12, h: 10, door_dir: "E",  scope: "indoor" },
        { id: 3,  type: "meditation_hall",    label: "Meditation / Yoga Corner",    x: 57, y: 23, w: 11, h: 9,  door_dir: "E",  scope: "indoor" },
        { id: 4,  type: "medication_cabinet", label: "Medication Cabinet (Dhanvantari)", x: 58, y: 17, w: 9, h: 5, door_dir: "NE", scope: "indoor" },
        { id: 5,  type: "living_room",        label: "Living Room",                 x: 42, y: 20, w: 14, h: 15, door_dir: "N",  scope: "indoor" },
        { id: 6,  type: "tv_screen",          label: "Living Room TV (East Wall)",  x: 53, y: 36, w: 9,  h: 5,  door_dir: "E",  wall_side: "E",  scope: "indoor" },
        { id: 7,  type: "photo_gods",         label: "Gods / Deities Photo (NE Wall)", x: 72, y: 34, w: 10, h: 5, door_dir: "E", wall_side: "NE", scope: "indoor" },
        { id: 8,  type: "kitchen",            label: "SE Agni Kitchen",             x: 64, y: 62, w: 18, h: 16, door_dir: "E",  scope: "indoor" },
        { id: 9,  type: "kitchen_stove",      label: "Kitchen Stove (Face East)",   x: 73, y: 68, w: 8,  h: 6,  door_dir: "E",  scope: "indoor" },
        { id: 10, type: "indoor_taps",        label: "Kitchen Sink / Taps (NE)",    x: 64, y: 49, w: 8,  h: 6,  door_dir: "NE", scope: "indoor" },
        { id: 11, type: "grain_pantry",       label: "Food & Grain Pantry",         x: 53, y: 67, w: 10, h: 9,  door_dir: "N",  scope: "indoor" },
        { id: 12, type: "dining_room",        label: "West Dining Room",            x: 18, y: 43, w: 15, h: 13, door_dir: "E",  scope: "indoor" },
        { id: 13, type: "master_bedroom",     label: "SW Master Bedroom",           x: 18, y: 60, w: 21, h: 18, door_dir: "N",  scope: "indoor" },
        { id: 14, type: "photo_living",       label: "Living Family Photo (SW Wall)",x: 20, y: 79, w: 11, h: 5, door_dir: "N",  wall_side: "SW", scope: "indoor" },
        { id: 15, type: "photo_deceased",     label: "Deceased Ancestors Photo (South Wall)", x: 42, y: 78, w: 10, h: 5, door_dir: "N", wall_side: "S", scope: "indoor" },
        { id: 16, type: "safe_locker",        label: "Cash Safe (Opens North)",     x: 40, y: 66, w: 9,  h: 8,  door_dir: "N",  scope: "indoor" },
        { id: 17, type: "storage",            label: "SW Heavy Storage",            x: 34, y: 57, w: 10, h: 8,  door_dir: "N",  scope: "indoor" },
        { id: 18, type: "gym_room",           label: "South Gym / Workout Room",    x: 51, y: 56, w: 11, h: 10, door_dir: "N",  scope: "indoor" },
        { id: 19, type: "study_room",         label: "Study / Home Office",         x: 64, y: 39, w: 14, h: 9,  door_dir: "NE", scope: "indoor" },
        { id: 20, type: "guest_room",         label: "NW Guest Bedroom",            x: 18, y: 18, w: 14, h: 13, door_dir: "E",  scope: "indoor" },
        { id: 21, type: "bathroom",           label: "NW Bathroom",                 x: 33, y: 18, w: 8,  h: 10, door_dir: "E",  scope: "indoor" },
        { id: 22, type: "washer_dryer",       label: "NW Washer & Dryer",           x: 18, y: 32, w: 10, h: 8,  door_dir: "E",  scope: "indoor" },
        { id: 23, type: "wall_mirror",        label: "North Wall Mirror",           x: 43, y: 15, w: 9,  h: 5,  door_dir: "E",  wall_side: "N",  scope: "indoor" },
        // Outdoor Lot Items
        { id: 24, type: "gate",               label: "Main Compound Gate",          x: 68, y: 2,  w: 15, h: 6,  door_dir: "NE", gate_mech: "swing_in_cw", scope: "outdoor" },
        { id: 25, type: "parking_gate",       label: "NW Sliding Parking Gate",     x: 14, y: 2,  w: 17, h: 6,  door_dir: "NW", gate_mech: "slide_ne",    scope: "outdoor" },
        { id: 26, type: "water_hose",         label: "NE Garden Water Hose & Tap",  x: 86, y: 10, w: 10, h: 7,  door_dir: "NE", scope: "outdoor" },
        { id: 27, type: "trench_ditch",       label: "NE Storm Drain Trench",       x: 62, y: 9,  w: 20, h: 5,  door_dir: "NE", flow_dir: "NE",           scope: "outside_boundary" },
        { id: 28, type: "kids_slide",         label: "East Kids Slide & Play Area", x: 86, y: 38, w: 11, h: 11, door_dir: "E",  scope: "outdoor" },
        { id: 29, type: "trees",              label: "SW Heavy Shade Trees",        x: 3,  y: 78, w: 12, h: 14, door_dir: "",   scope: "outdoor" },
        { id: 30, type: "overhead_tank",      label: "SW Overhead Water Tank",      x: 3,  y: 62, w: 11, h: 11, door_dir: "",   scope: "outdoor" },
        { id: 31, type: "fireplace",          label: "SE Outdoor Fire Pit / BBQ",   x: 86, y: 78, w: 11, h: 12, door_dir: "",   scope: "outdoor" },
        { id: 32, type: "flowers",            label: "NE Sacred Flower Bed",        x: 86, y: 20, w: 11, h: 12, door_dir: "",   scope: "outdoor" },
        { id: 33, type: "garden",             label: "North Herb & Veggie Garden",  x: 38, y: 3,  w: 22, h: 7,  door_dir: "",   scope: "outdoor" }
      ],
      walls: [
        { id: 201, label: "SW Master Suite Bearing Wall", x1: 16, y1: 58, x2: 42, y2: 58 },
        { id: 202, label: "SE Kitchen Fire Partition Wall", x1: 62, y1: 58, x2: 84, y2: 58 }
      ],
      fences: [
        {
          id: 301,
          label: "Complete 360° Perimeter Compound Fence (Closed Loop)",
          closed: true,
          open_side: "",
          points: [{ x: 2, y: 2 }, { x: 98, y: 2 }, { x: 98, y: 98 }, { x: 2, y: 98 }]
        }
      ]
    };
  }

  function getDoshaDemoPreset() {
    return {
      preset_title: "Dosha & Zero-Demolition Remedies Demo (Multiple Clashes to Test Fixes)",
      items: [
        { id: 1,  type: "entrance",           label: "SW Entrance (Swing Outward Defect)", x: 20, y: 74, w: 14, h: 7, door_dir: "SW", gate_mech: "swing_out", scope: "indoor" },
        { id: 2,  type: "kitchen_stove",      label: "NE Stove (Fire-in-Water Clash)",     x: 68, y: 20, w: 9,  h: 7, door_dir: "S",  scope: "indoor" },
        { id: 3,  type: "indoor_taps",        label: "Water Tap Touching Stove (Clash)",   x: 70, y: 22, w: 8,  h: 6, door_dir: "S",  scope: "indoor" },
        { id: 4,  type: "medication_cabinet", label: "SW Medicine Cabinet (Chronic Meds)", x: 22, y: 64, w: 10, h: 7, door_dir: "S",  scope: "indoor" },
        { id: 5,  type: "photo_gods",         label: "Gods Photo in NE",                   x: 72, y: 30, w: 10, h: 6, door_dir: "E",  wall_side: "NE", scope: "indoor" },
        { id: 6,  type: "photo_deceased",     label: "Ancestors Photo Next to Gods (Clash)",x: 74, y: 32, w: 10, h: 6, door_dir: "E", wall_side: "NE", scope: "indoor" },
        { id: 7,  type: "master_bedroom",     label: "SE Bedroom (Agni Anxiety)",          x: 62, y: 60, w: 20, h: 17, door_dir: "S", scope: "indoor" },
        { id: 8,  type: "tv_screen",          label: "TV Facing Bed Directly",             x: 65, y: 64, w: 9,  h: 6, door_dir: "S",  wall_side: "S",  scope: "indoor" },
        { id: 9,  type: "trench_ditch",       label: "SW Outside Boundary Ditch (Draining SW)", x: 4, y: 88, w: 24, h: 6, door_dir: "SW", flow_dir: "SW", scope: "outside_boundary" },
        { id: 10, type: "gate",               label: "South Gate Sliding SW",              x: 45, y: 92, w: 15, h: 6, door_dir: "S",  gate_mech: "slide_sw", scope: "outdoor" }
      ],
      walls: [
        { id: 201, label: "Wall Cutting Through Brahmasthan Center", x1: 25, y1: 50, x2: 75, y2: 50 }
      ],
      fences: [
        {
          id: 301,
          label: "Open-Loop Fence (Unprotected SW Gap)",
          closed: false,
          open_side: "SW",
          points: [{ x: 2, y: 2 }, { x: 98, y: 2 }, { x: 98, y: 98 }]
        }
      ]
    };
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

  function buildFencePresetPoints(openSide) {
    // Returns polygon/polyline points around property (2% to 98%)
    if (!openSide || openSide === "closed") {
      return {
        closed: true,
        open_side: "",
        label: "Complete 360° Perimeter Compound Fence (Closed Loop)",
        points: [{ x: 2, y: 2 }, { x: 98, y: 2 }, { x: 98, y: 98 }, { x: 2, y: 98 }]
      };
    }
    const map = {
      N:  { label: "Open-Loop Perimeter Fence (Open on North Side)",      points: [{ x: 35, y: 2 }, { x: 2, y: 2 }, { x: 2, y: 98 }, { x: 98, y: 98 }, { x: 98, y: 2 }, { x: 65, y: 2 }] },
      NE: { label: "Open-Loop Perimeter Fence (Open on North-East Corner)",points: [{ x: 72, y: 2 }, { x: 2, y: 2 }, { x: 2, y: 98 }, { x: 98, y: 98 }, { x: 98, y: 28 }] },
      E:  { label: "Open-Loop Perimeter Fence (Open on East Side)",       points: [{ x: 98, y: 35 }, { x: 98, y: 2 }, { x: 2, y: 2 }, { x: 2, y: 98 }, { x: 98, y: 98 }, { x: 98, y: 65 }] },
      SE: { label: "Open-Loop Perimeter Fence (Open on South-East Corner)",points: [{ x: 98, y: 72 }, { x: 98, y: 2 }, { x: 2, y: 2 }, { x: 2, y: 98 }, { x: 72, y: 98 }] },
      S:  { label: "Open-Loop Perimeter Fence (Open on South Side)",      points: [{ x: 65, y: 98 }, { x: 98, y: 98 }, { x: 98, y: 2 }, { x: 2, y: 2 }, { x: 2, y: 98 }, { x: 35, y: 98 }] },
      SW: { label: "Open-Loop Perimeter Fence (Open on South-West Corner)",points: [{ x: 28, y: 98 }, { x: 98, y: 98 }, { x: 98, y: 2 }, { x: 2, y: 2 }, { x: 2, y: 72 }] },
      W:  { label: "Open-Loop Perimeter Fence (Open on West Side)",       points: [{ x: 2, y: 65 }, { x: 2, y: 98 }, { x: 98, y: 98 }, { x: 98, y: 2 }, { x: 2, y: 2 }, { x: 2, y: 35 }] },
      NW: { label: "Open-Loop Perimeter Fence (Open on North-West Corner)",points: [{ x: 2, y: 28 }, { x: 2, y: 98 }, { x: 98, y: 98 }, { x: 98, y: 2 }, { x: 28, y: 2 }] }
    };
    const chosen = map[openSide] || map.NE;
    return {
      closed: false,
      open_side: openSide,
      label: chosen.label,
      points: chosen.points
    };
  }

  function buildStudioShellHTML() {
    const renderCatBtns = (catKey, isDashed) =>
      Object.entries(CATALOG)
        .filter(([, m]) => m.cat === catKey)
        .map(([k, m]) => `<button type="button" class="btn" data-va-add="${k}" style="background:${m.bg};color:#111827;border:1.5px ${isDashed ? "dashed" : "solid"} ${m.border};padding:4px 9px;font-size:11.5px;font-weight:700;border-radius:6px;cursor:pointer;">${m.icon} + ${m.label}</button>`)
        .join("");

    return `
      <div class="va-studio-wrapper" style="border:2px solid #cbd5e1;border-radius:12px;background:#ffffff;padding:16px;box-shadow:0 4px 14px rgba(15,23,42,0.06);">
        <!-- 1. Top Configuration & Preset Bar -->
        <div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;padding:12px 14px;background:linear-gradient(135deg,#f8fafc 0%,#f1f5f9 100%);border:1px solid #e2e8f0;border-radius:8px;margin-bottom:12px;">
          <div style="display:flex;flex-wrap:wrap;gap:12px;align-items:center;">
            <label style="font-size:12.5px;font-weight:700;color:#1e293b;">
              📐 House Shape:
              <select class="va-shape-select" style="margin-left:4px;padding:5px 8px;border:1px solid #94a3b8;border-radius:6px;font-weight:600;">
                <option value="square">Giant Square House (1:1 Chaturasra)</option>
                <option value="wide_rectangle">Wide Rectangle House (4:3 East-West)</option>
                <option value="deep_rectangle">Deep Rectangle House (3:4 North-South)</option>
              </select>
            </label>
            <label style="font-size:12.5px;font-weight:700;color:#0f766e;display:inline-flex;align-items:center;gap:5px;cursor:pointer;">
              <input type="checkbox" class="va-lot-checkbox" checked style="width:15px;height:15px;">
              🌳 Include Outer Property Lot &amp; Boundary
            </label>
            <label style="font-size:12.5px;font-weight:700;color:#1e293b;">
              🧭 Compass North:
              <select class="va-compass-select" style="margin-left:4px;padding:5px 8px;border:1px solid #94a3b8;border-radius:6px;font-weight:600;">
                <option value="0">0° — North at Top (Standard)</option>
                <option value="45">45° — North-East at Top</option>
                <option value="90">90° — East at Top</option>
                <option value="135">135° — South-East at Top</option>
                <option value="180">180° — South at Top</option>
                <option value="225">225° — South-West at Top</option>
                <option value="270">270° — West at Top</option>
                <option value="315">315° — North-West at Top</option>
              </select>
            </label>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:7px;">
            <button type="button" class="btn va-btn-chart-ideal" style="background:#7c3aed;color:#fff;padding:6px 11px;font-size:12px;font-weight:700;border-radius:6px;">🌟 My Birth-Chart Ideal Vastu Setting</button>
            <button type="button" class="btn va-btn-ideal" style="background:#0f766e;color:#fff;padding:6px 11px;font-size:12px;font-weight:700;border-radius:6px;">✨ Classical Ideal Preset</button>
            <button type="button" class="btn va-btn-dosha-demo" style="background:#b45309;color:#fff;padding:6px 11px;font-size:12px;font-weight:700;border-radius:6px;">🛠️ Dosha &amp; Remedies Demo</button>
            <button type="button" class="btn va-btn-clear" style="background:#475569;color:#fff;padding:6px 11px;font-size:12px;border-radius:6px;">🗑️ Clear All</button>
          </div>
        </div>

        <!-- Active Preset Banner -->
        <div class="va-preset-banner" style="padding:8px 12px;background:#f5f3ff;border:1px solid #ddd6fe;border-radius:7px;margin-bottom:10px;font-size:12.5px;color:#4c1d95;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px;">
          <span class="va-preset-title-text">🌟 Loaded: Ideal Vastu &amp; Feng Shui Setting Calibrated to Your Birth Chart</span>
          <span style="font-size:11.5px;color:#6d28d9;">Customize any room, wall, fence, gate, photo, stove, tap, or trench below, then press <b>🔍 Evaluate</b>!</span>
        </div>

        <!-- Palm + Birth Chart + Vastu Integration Bar -->
        <div class="va-palm-bar" style="padding:10px 12px;background:linear-gradient(135deg,#fff7ed 0%,#ffedd5 100%);border:1.5px solid #fdba74;border-radius:8px;margin-bottom:12px;display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;">
          <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
            <span style="font-size:12.5px;font-weight:800;color:#9a3412;">🖐️ Combine Palm + Birth Chart + Vastu:</span>
            <label class="btn" style="background:#c2410c;color:#fff;padding:5px 10px;font-size:11.5px;font-weight:700;border-radius:6px;cursor:pointer;margin:0;">
              📷 Upload Palm Photo
              <input type="file" class="va-palm-file" accept="image/*" style="display:none;">
            </label>
            <span class="va-palm-status-badge" style="font-size:11.5px;font-weight:700;color:#7c2d12;background:#fed7aa;padding:3px 8px;border-radius:999px;">Palm Profile Active</span>
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:11.5px;color:#7c2d12;">
            <label style="font-weight:700;">Hand:
              <select class="va-palm-shape" style="padding:3px 6px;border:1px solid #fb923c;border-radius:4px;font-size:11px;font-weight:600;">
                <option value="fire">🔥 Fire (Pitta)</option>
                <option value="earth">🌍 Earth (Kapha)</option>
                <option value="air">💨 Air (Vata)</option>
                <option value="water">💧 Water (Luna)</option>
              </select>
            </label>
            <label style="font-weight:700;">Life:
              <select class="va-palm-life" style="padding:3px 6px;border:1px solid #fb923c;border-radius:4px;font-size:11px;">
                <option value="deep">Deep</option>
                <option value="wide">Wide Arc</option>
                <option value="double">Double</option>
                <option value="faint">Delicate/Faint</option>
              </select>
            </label>
            <label style="font-weight:700;">Head:
              <select class="va-palm-head" style="padding:3px 6px;border:1px solid #fb923c;border-radius:4px;font-size:11px;">
                <option value="long">Long/Clear</option>
                <option value="straight">Straight</option>
                <option value="sloping">Sloping/Creative</option>
                <option value="short">Short</option>
              </select>
            </label>
            <label style="font-weight:700;">Heart:
              <select class="va-palm-heart" style="padding:3px 6px;border:1px solid #fb923c;border-radius:4px;font-size:11px;">
                <option value="curved">Curved</option>
                <option value="straight">Straight</option>
                <option value="chained">Chained</option>
              </select>
            </label>
            <label style="font-weight:700;">Fate:
              <select class="va-palm-fate" style="padding:3px 6px;border:1px solid #fb923c;border-radius:4px;font-size:11px;">
                <option value="clear">Clear/Strong</option>
                <option value="late">Late-Rising</option>
                <option value="broken">Multi-Path</option>
              </select>
            </label>
            <label style="font-weight:700;">Thumbprint:
              <select class="va-palm-thumb" style="padding:3px 6px;border:1px solid #fb923c;border-radius:4px;font-size:11px;">
                <option value="chakra_whorl">Chakra (Whorl)</option>
                <option value="shankha_loop">Shankha (Conch Loop)</option>
                <option value="padma_arch">Padma (Lotus Arch)</option>
                <option value="simha_composite">Simha (Twin Loop)</option>
              </select>
            </label>
          </div>
        </div>

        <!-- 2. Categorized Multi-Instance Palettes -->
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:10px;margin-bottom:12px;">
          <div style="padding:9px 11px;background:#fffbeb;border:1px solid #fde68a;border-radius:8px;">
            <div style="font-size:12px;font-weight:800;color:#92400e;margin-bottom:6px;">
              🏠 1. ROOMS, DOORS, TEMPLE / PRAYER HALL, MEDITATION, GYM &amp; STORAGE:
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:5px;">${renderCatBtns("indoor_rooms", false)}</div>
          </div>

          <div style="padding:9px 11px;background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;">
            <div style="font-size:12px;font-weight:800;color:#1e40af;margin-bottom:6px;">
              🔥 2. KITCHEN STOVE, WATER TAPS, WASHER/DRYER, MEDICATION CABINET &amp; UTILITIES:
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:5px;">${renderCatBtns("indoor_fixtures", false)}</div>
          </div>

          <div style="padding:9px 11px;background:#fdf2f8;border:1px solid #fbcfe8;border-radius:8px;">
            <div style="font-size:12px;font-weight:800;color:#9d174d;margin-bottom:6px;">
              🖼️ 3. PHOTO FRAMES (LIVING, DECEASED ANCESTORS, GODS), TV SCREEN, MIRROR &amp; CLOCK:
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:5px;">${renderCatBtns("wall_decor", false)}</div>
          </div>

          <div style="padding:9px 11px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;">
            <div style="font-size:12px;font-weight:800;color:#166534;margin-bottom:6px;">
              🌳 4. OUTDOOR GATES (SLIDING/SWING), TRENCH/DITCH, WATER HOSE, KIDS SLIDE &amp; YARD:
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:5px;">${renderCatBtns("outdoor", true)}</div>
          </div>
        </div>

        <!-- 3. Interactive Wall Line Drawing & Perimeter Fence Loop Toolbar -->
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:10px;margin-bottom:12px;">
          <!-- Wall Line Tool -->
          <div style="padding:10px 12px;background:#f8fafc;border:1.5px solid #cbd5e1;border-radius:8px;display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between;">
            <div>
              <div style="font-size:12px;font-weight:800;color:#1e293b;">🧱 DRAW WALL BY LINE (Interior / Partition Walls)</div>
              <div style="font-size:11px;color:#475569;">Click &amp; drag on the floorplan to draw custom walls. Checked for Brahmasthan &amp; SW/NE balance.</div>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;">
              <button type="button" class="btn va-btn-draw-wall" style="background:#334155;color:#fff;padding:5px 10px;font-size:11.5px;font-weight:700;border-radius:6px;">✏️ Draw Wall Line: OFF</button>
              <label style="font-size:11.5px;font-weight:600;color:#334155;display:inline-flex;align-items:center;gap:4px;">
                <input type="checkbox" class="va-wall-ortho" checked> 90° Snap
              </label>
              <button type="button" class="btn va-btn-undo-wall" style="background:#64748b;color:#fff;padding:5px 8px;font-size:11px;border-radius:5px;" title="Remove Last Drawn Wall">↩️ Undo Wall</button>
              <button type="button" class="btn va-btn-clear-walls" style="background:#94a3b8;color:#fff;padding:5px 8px;font-size:11px;border-radius:5px;">🗑️ Clear Walls</button>
            </div>
          </div>

          <!-- Perimeter Fence Closed / Open Loop Builder -->
          <div style="padding:10px 12px;background:#fefce8;border:1.5px solid #fde047;border-radius:8px;display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between;">
            <div>
              <div style="font-size:12px;font-weight:800;color:#854d0e;">🚧 PERIMETER FENCE ALL AROUND (Closed Loop or Open Loop)</div>
              <div style="font-size:11px;color:#713f12;">Add a full 360° closed fence loop, an open-loop fence with an open side, or draw custom fence points.</div>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;">
              <select class="va-fence-preset-select" style="padding:5px 8px;border:1px solid #ca8a04;border-radius:6px;font-size:11.5px;font-weight:700;background:#fff;">
                <option value="closed">🔒 Closed Loop Fence All Around (360° Enclosure)</option>
                <option value="NE">🔓 Open Loop — Open on North-East (Auspicious Entry)</option>
                <option value="N">🔓 Open Loop — Open on North Side</option>
                <option value="E">🔓 Open Loop — Open on East Side</option>
                <option value="NW">🔓 Open Loop — Open on North-West</option>
                <option value="SE">🔓 Open Loop — Open on South-East</option>
                <option value="S">🔓 Open Loop — Open on South Side (Dosha Warning)</option>
                <option value="SW">🔓 Open Loop — Open on South-West (Severe Leak)</option>
                <option value="W">🔓 Open Loop — Open on West Side</option>
              </select>
              <button type="button" class="btn va-btn-apply-fence" style="background:#b45309;color:#fff;padding:5px 10px;font-size:11.5px;font-weight:700;border-radius:6px;">🚧 Set Fence Loop</button>
              <button type="button" class="btn va-btn-draw-fence" style="background:#78350f;color:#fff;padding:5px 9px;font-size:11.5px;font-weight:700;border-radius:6px;">✏️ Draw Custom Fence</button>
              <button type="button" class="btn va-btn-clear-fence" style="background:#78716c;color:#fff;padding:5px 8px;font-size:11px;border-radius:5px;">🗑️ Clear Fence</button>
            </div>
          </div>
        </div>

        <!-- Custom Fence Drawing Sub-bar (shown only when drawing custom fence points) -->
        <div class="va-custom-fence-bar" style="display:none;padding:9px 12px;background:#fffbeb;border:2px dashed #d97706;border-radius:8px;margin-bottom:12px;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
          <div style="font-size:12.5px;font-weight:700;color:#92400e;">
            ✏️ <b>Custom Fence Loop Mode:</b> Click points around the property on the canvas below to trace your fence path (<span class="va-fence-pt-count">0</span> points placed).
          </div>
          <div style="display:flex;gap:8px;">
            <button type="button" class="btn va-btn-finish-fence-closed" style="background:#15803d;color:#fff;padding:5px 11px;font-size:12px;font-weight:700;border-radius:6px;">🔒 Finish as Closed Loop</button>
            <button type="button" class="btn va-btn-finish-fence-open" style="background:#d97706;color:#fff;padding:5px 11px;font-size:12px;font-weight:700;border-radius:6px;">🔓 Finish as Open Loop</button>
            <button type="button" class="btn va-btn-cancel-fence" style="background:#64748b;color:#fff;padding:5px 11px;font-size:12px;border-radius:6px;">✖ Cancel</button>
          </div>
        </div>

        <!-- 4. Selected Block Inspector (Supports Gate Sliding/Swing, Photo/TV Wall Side, Trench Drainage Flow & Outside-Boundary Scope) -->
        <div class="va-inspector" style="padding:12px 14px;background:#f8fafc;border:1px solid #cbd5e1;border-radius:8px;margin-bottom:14px;"></div>

        <!-- 5. Prominent Evaluate Action Bar (Top of Canvas) -->
        <div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;padding:12px 16px;background:linear-gradient(90deg,#1e1b4b 0%,#312e81 100%);color:#ffffff;border-radius:10px;margin-bottom:14px;box-shadow:0 4px 12px rgba(30,27,75,0.18);">
          <div>
            <div style="font-size:14px;font-weight:800;letter-spacing:0.2px;">🔍 Ready to Generate Full Vastu &amp; Classical Feng Shui Evaluation?</div>
            <div class="va-eval-status" style="font-size:12px;color:#c7d2fe;margin-top:2px;">
              All rooms, walls, fences, gates, photos, stove, taps, and trenches are ready. Press <b>Evaluate</b> whenever you finish making changes!
            </div>
          </div>
          <button type="button" class="btn va-btn-evaluate" style="background:linear-gradient(135deg,#10b981 0%,#059669 100%);color:#ffffff;border:2px solid #a7f3d0;padding:10px 26px;font-size:15px;font-weight:900;border-radius:8px;cursor:pointer;box-shadow:0 4px 14px rgba(16,185,129,0.4);">
            🔍 Evaluate Vastu &amp; Feng Shui Now
          </button>
        </div>

        <!-- 6. Giant Interactive Floorplan & Outer Lot Canvas -->
        <div style="display:flex;justify-content:center;margin-bottom:14px;">
          <div class="va-canvas" style="position:relative;width:100%;max-width:800px;aspect-ratio:1/1;min-height:580px;border:3px solid #166534;border-radius:12px;overflow:hidden;box-shadow:inset 0 0 24px rgba(22,101,52,0.08);">
            <!-- Outer Lot Compass Direction Badges -->
            <div class="va-compass-tag" style="position:absolute;top:6px;left:50%;transform:translateX(-50%);background:#0f172a;color:#f8fafc;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:700;z-index:25;pointer-events:none;">N (Kubera / Career)</div>
            <div class="va-compass-tag" style="position:absolute;top:6px;right:8px;background:#1e3a8a;color:#fff;padding:2px 8px;border-radius:12px;font-size:10.5px;font-weight:700;z-index:25;pointer-events:none;">NE (Ishanya / Wisdom)</div>
            <div class="va-compass-tag" style="position:absolute;top:50%;right:6px;transform:translateY(-50%);background:#0f172a;color:#f8fafc;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;z-index:25;pointer-events:none;">E (Surya / Green Dragon)</div>
            <div class="va-compass-tag" style="position:absolute;bottom:6px;right:8px;background:#9a3412;color:#fff;padding:2px 8px;border-radius:12px;font-size:10.5px;font-weight:700;z-index:25;pointer-events:none;">SE (Agni / Wealth)</div>
            <div class="va-compass-tag" style="position:absolute;bottom:6px;left:50%;transform:translateX(-50%);background:#0f172a;color:#f8fafc;padding:2px 10px;border-radius:12px;font-size:11px;font-weight:700;z-index:25;pointer-events:none;">S (Yama / Fame)</div>
            <div class="va-compass-tag" style="position:absolute;bottom:6px;left:8px;background:#4c1d95;color:#fff;padding:2px 8px;border-radius:12px;font-size:10.5px;font-weight:700;z-index:25;pointer-events:none;">SW (Nairutya / Stability)</div>
            <div class="va-compass-tag" style="position:absolute;top:50%;left:6px;transform:translateY(-50%);background:#0f172a;color:#f8fafc;padding:2px 8px;border-radius:12px;font-size:11px;font-weight:700;z-index:25;pointer-events:none;">W (Varuna / White Tiger)</div>
            <div class="va-compass-tag" style="position:absolute;top:6px;left:8px;background:#334155;color:#fff;padding:2px 8px;border-radius:12px;font-size:10.5px;font-weight:700;z-index:25;pointer-events:none;">NW (Vayu / Mentors)</div>

            <div class="va-lot-watermark" style="position:absolute;top:28px;left:14px;font-size:11px;font-weight:700;color:#15803d;opacity:0.85;pointer-events:none;z-index:3;">
              🌳 OUTER LOT &amp; BOUNDARY (Fence Loop, Sliding/Swing Gates, Trench/Ditch, Water Hose, Kids Slide, Trees)
            </div>

            <!-- Inner Giant Square / Rectangle House Footprint -->
            <div class="va-house-box" style="position:absolute;left:16%;top:16%;width:68%;height:68%;background:#ffffff;border:4px solid #1e293b;border-radius:6px;box-shadow:0 8px 25px rgba(0,0,0,0.12);box-sizing:border-box;display:grid;grid-template-columns:1fr 1fr 1fr;grid-template-rows:1fr 1fr 1fr;pointer-events:none;z-index:2;">
              <div style="border:1px dashed #cbd5e1;display:flex;align-items:center;justify-content:center;font-size:10px;color:#94a3b8;font-weight:700;text-align:center;padding:4px;">NW<br>Vayu (Air)<br>Bagua: Mentors</div>
              <div style="border:1px dashed #cbd5e1;display:flex;align-items:center;justify-content:center;font-size:10px;color:#94a3b8;font-weight:700;text-align:center;padding:4px;">N<br>Kubera (Wealth)<br>Bagua: Career</div>
              <div style="border:1px dashed #cbd5e1;background:rgba(239,246,255,0.45);display:flex;align-items:center;justify-content:center;font-size:10px;color:#3b82f6;font-weight:700;text-align:center;padding:4px;">NE<br>Ishanya (Sacred)<br>Bagua: Wisdom</div>
              <div style="border:1px dashed #cbd5e1;display:flex;align-items:center;justify-content:center;font-size:10px;color:#94a3b8;font-weight:700;text-align:center;padding:4px;">W<br>Varuna (Saturn)<br>Bagua: Children</div>
              <div style="border:1.5px dashed #f59e0b;background:rgba(254,243,199,0.35);display:flex;align-items:center;justify-content:center;font-size:10.5px;color:#b45309;font-weight:800;text-align:center;padding:4px;">CENTER<br>Brahmasthan<br>&amp; Tai Qi Heart</div>
              <div style="border:1px dashed #cbd5e1;display:flex;align-items:center;justify-content:center;font-size:10px;color:#94a3b8;font-weight:700;text-align:center;padding:4px;">E<br>Surya (Sun)<br>Bagua: Health</div>
              <div style="border:1px dashed #cbd5e1;background:rgba(243,232,255,0.35);display:flex;align-items:center;justify-content:center;font-size:10px;color:#6d28d9;font-weight:700;text-align:center;padding:4px;">SW<br>Nairutya (Earth)<br>Bagua: Love/Master</div>
              <div style="border:1px dashed #cbd5e1;display:flex;align-items:center;justify-content:center;font-size:10px;color:#94a3b8;font-weight:700;text-align:center;padding:4px;">S<br>Yama (Mars)<br>Bagua: Fame</div>
              <div style="border:1px dashed #cbd5e1;background:rgba(255,237,213,0.4);display:flex;align-items:center;justify-content:center;font-size:10px;color:#ea580c;font-weight:700;text-align:center;padding:4px;">SE<br>Agni (Fire)<br>Bagua: Prosperity</div>
            </div>

            <!-- SVG Overlay for Drawn Wall Lines & Closed/Open Fence Loops -->
            <svg class="va-svg-layer" viewBox="0 0 100 100" preserveAspectRatio="none" style="position:absolute;inset:0;width:100%;height:100%;z-index:8;pointer-events:none;"></svg>

            <!-- Interactive Draggable & Resizable Blocks Layer -->
            <div class="va-items-layer" style="position:absolute;inset:0;z-index:10;"></div>
          </div>
        </div>

        <!-- Legend & Bottom Evaluate Button -->
        <div style="display:flex;flex-wrap:wrap;gap:14px;justify-content:space-between;align-items:center;font-size:12px;margin-bottom:14px;padding:10px 14px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;color:#334155;">
          <div style="display:flex;flex-wrap:wrap;gap:14px;">
            <span><b style="color:#15803d;">🟢 Green:</b> Ideal Zone</span>
            <span><b style="color:#d97706;">🟠 Amber:</b> Neutral</span>
            <span><b style="color:#dc2626;">🔴 Red:</b> Dosha / Clash</span>
            <span><b>🧱 Dark Brown Line:</b> Drawn Wall Line</span>
            <span><b>🚧 Amber/Green Perimeter:</b> Fence Loop (Closed/Open)</span>
          </div>
          <button type="button" class="btn va-btn-evaluate-bottom" style="background:#059669;color:#fff;padding:8px 20px;font-size:13.5px;font-weight:800;border-radius:7px;cursor:pointer;">
            🔍 Evaluate Layout &amp; Generate Report
          </button>
        </div>

        <!-- 7. Evaluation Report Container -->
        <div class="va-report-container"></div>
      </div>
    `;
  }

  window.initVastuArchitect = function (rootId, birthMeta) {
    const root = document.getElementById(rootId);
    if (!root) return;

    if (!root.querySelector(".va-canvas")) {
      root.innerHTML = buildStudioShellHTML();
    }

    const chartPreset = (birthMeta && birthMeta.personalizedPreset && Array.isArray(birthMeta.personalizedPreset.items))
      ? birthMeta.personalizedPreset
      : getStandardIdealPreset();

    let state = {
      houseShape: "square",
      hasOuterLot: true,
      compassRotation: 0,
      presetTitle: chartPreset.preset_title || "Personalized Birth-Chart Ideal Vastu & Feng Shui Arrangement",
      items: JSON.parse(JSON.stringify(chartPreset.items || [])),
      walls: JSON.parse(JSON.stringify(chartPreset.walls || [])),
      fences: JSON.parse(JSON.stringify(chartPreset.fences || [])),
      selectedId: (chartPreset.items && chartPreset.items[0]) ? chartPreset.items[0].id : null,
      nextId: 500,
      drawWallMode: false,
      wallDraft: null,
      drawFenceMode: false,
      fenceDraftPoints: [],
      dirty: false,
      palmProfile: (function () {
        try {
          const saved = localStorage.getItem("panchang_palm_profile");
          if (saved) return JSON.parse(saved);
        } catch (e) {}
        return {
          has_uploaded_photo: false,
          hand_shape: "fire",
          life_line: "deep",
          head_line: "long",
          heart_line: "curved",
          fate_line: "clear",
          thumbprint_type: "chakra_whorl",
          thumbprint_name: "Chakra Rekha (Concentric Whorl)"
        };
      })()
    };

    const canvasEl = root.querySelector(".va-canvas");
    const houseBoxEl = root.querySelector(".va-house-box");
    const lotWatermarkEl = root.querySelector(".va-lot-watermark");
    const svgLayerEl = root.querySelector(".va-svg-layer");
    const itemsLayerEl = root.querySelector(".va-items-layer");
    const inspectorEl = root.querySelector(".va-inspector");
    const reportEl = root.querySelector(".va-report-container");
    const presetTitleEl = root.querySelector(".va-preset-title-text");
    const evalStatusEl = root.querySelector(".va-eval-status");
    const evalBtnTop = root.querySelector(".va-btn-evaluate");
    const evalBtnBot = root.querySelector(".va-btn-evaluate-bottom");

    const shapeSel = root.querySelector(".va-shape-select");
    const lotChk = root.querySelector(".va-lot-checkbox");
    const rotSel = root.querySelector(".va-compass-select");
    const drawWallBtn = root.querySelector(".va-btn-draw-wall");
    const orthoChk = root.querySelector(".va-wall-ortho");
    const undoWallBtn = root.querySelector(".va-btn-undo-wall");
    const clearWallsBtn = root.querySelector(".va-btn-clear-walls");

    const fencePresetSel = root.querySelector(".va-fence-preset-select");
    const applyFenceBtn = root.querySelector(".va-btn-apply-fence");
    const drawFenceBtn = root.querySelector(".va-btn-draw-fence");
    const clearFenceBtn = root.querySelector(".va-btn-clear-fence");
    const customFenceBar = root.querySelector(".va-custom-fence-bar");
    const fencePtCountEl = root.querySelector(".va-fence-pt-count");
    const finishFenceClosedBtn = root.querySelector(".va-btn-finish-fence-closed");
    const finishFenceOpenBtn = root.querySelector(".va-btn-finish-fence-open");
    const cancelFenceBtn = root.querySelector(".va-btn-cancel-fence");

    function markDirty(msg) {
      state.dirty = true;
      if (evalStatusEl) {
        evalStatusEl.innerHTML = `<span style="color:#fde047;font-weight:700;">✏️ ${msg || "Layout modified"} — Press <b>"🔍 Evaluate Vastu & Feng Shui Now"</b> to update your report!</span>`;
      }
      if (evalBtnTop) {
        evalBtnTop.style.background = "linear-gradient(135deg,#f59e0b 0%,#d97706 100%)";
        evalBtnTop.style.borderColor = "#fef08a";
        evalBtnTop.textContent = "🔍 Evaluate Changes Now";
      }
      if (evalBtnBot) {
        evalBtnBot.style.background = "#d97706";
        evalBtnBot.textContent = "🔍 Evaluate Changes & Refresh Report";
      }
    }

    function markClean() {
      state.dirty = false;
      if (evalStatusEl) {
        evalStatusEl.innerHTML = `✅ Report is up-to-date with your current floorplan (${state.items.length} blocks, ${state.walls.length} wall lines, ${state.fences.length} fence loop).`;
      }
      if (evalBtnTop) {
        evalBtnTop.style.background = "linear-gradient(135deg,#10b981 0%,#059669 100%)";
        evalBtnTop.style.borderColor = "#a7f3d0";
        evalBtnTop.textContent = "🔍 Evaluate Vastu & Feng Shui Now";
      }
      if (evalBtnBot) {
        evalBtnBot.style.background = "#059669";
        evalBtnBot.textContent = "🔍 Evaluate Layout & Generate Report";
      }
    }

    function updatePresetBanner() {
      if (presetTitleEl) {
        presetTitleEl.textContent = "🌟 Active Layout: " + state.presetTitle;
      }
    }

    // Sync Palm UI Controls
    const palmShapeSel = root.querySelector(".va-palm-shape");
    const palmLifeSel = root.querySelector(".va-palm-life");
    const palmHeadSel = root.querySelector(".va-palm-head");
    const palmHeartSel = root.querySelector(".va-palm-heart");
    const palmFateSel = root.querySelector(".va-palm-fate");
    const palmThumbSel = root.querySelector(".va-palm-thumb");
    const palmFileInp = root.querySelector(".va-palm-file");
    const palmStatusBadge = root.querySelector(".va-palm-status-badge");

    function syncPalmControlsFromState() {
      const pp = state.palmProfile || {};
      if (palmShapeSel && pp.hand_shape) palmShapeSel.value = pp.hand_shape;
      if (palmLifeSel && pp.life_line) palmLifeSel.value = pp.life_line;
      if (palmHeadSel && pp.head_line) palmHeadSel.value = pp.head_line;
      if (palmHeartSel && pp.heart_line) palmHeartSel.value = pp.heart_line;
      if (palmFateSel && pp.fate_line) palmFateSel.value = pp.fate_line;
      if (palmThumbSel && pp.thumbprint_type) palmThumbSel.value = pp.thumbprint_type;
      if (palmStatusBadge) {
        palmStatusBadge.textContent = pp.has_uploaded_photo
          ? `✅ Uploaded Palm Photo Active (${(pp.hand_shape || 'fire').toUpperCase()} Hand)`
          : `🖐️ Palm Profile: ${(pp.hand_shape || 'fire').toUpperCase()} Hand`;
        palmStatusBadge.style.background = pp.has_uploaded_photo ? "#dcfce7" : "#fed7aa";
        palmStatusBadge.style.color = pp.has_uploaded_photo ? "#166534" : "#7c2d12";
      }
    }
    syncPalmControlsFromState();

    function onPalmControlChange() {
      state.palmProfile = Object.assign({}, state.palmProfile, {
        hand_shape: palmShapeSel ? palmShapeSel.value : "fire",
        life_line: palmLifeSel ? palmLifeSel.value : "deep",
        head_line: palmHeadSel ? palmHeadSel.value : "long",
        heart_line: palmHeartSel ? palmHeartSel.value : "curved",
        fate_line: palmFateSel ? palmFateSel.value : "clear",
        thumbprint_type: palmThumbSel ? palmThumbSel.value : "chakra_whorl",
        thumbprint_name: palmThumbSel ? palmThumbSel.options[palmThumbSel.selectedIndex].text : "Chakra Rekha"
      });
      try {
        localStorage.setItem("panchang_palm_profile", JSON.stringify(state.palmProfile));
      } catch (e) {}
      syncPalmControlsFromState();
      markDirty("Updated Palm features for Palm + Chart + Vastu synthesis");
    }

    [palmShapeSel, palmLifeSel, palmHeadSel, palmHeartSel, palmFateSel, palmThumbSel].forEach(sel => {
      if (sel) sel.addEventListener("change", onPalmControlChange);
    });

    if (palmFileInp) {
      palmFileInp.addEventListener("change", e => {
        const file = e.target.files && e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = async ev => {
          try {
            const r = await fetch("/api/palmistry/analyze-photo", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                image_base64: ev.target.result,
                birth_date: (birthMeta && birthMeta.date) || "1990-05-15",
                birth_time: (birthMeta && birthMeta.time) || "10:30:00",
                latitude: (birthMeta && birthMeta.lat) || 28.6139,
                longitude: (birthMeta && birthMeta.lon) || 77.2090,
                timezone: (birthMeta && birthMeta.tz) || "Asia/Kolkata"
              })
            });
            if (r.ok) {
              const pData = await r.json();
              if (pData.extracted_palm_profile) {
                state.palmProfile = Object.assign({}, pData.extracted_palm_profile, {
                  has_uploaded_photo: true,
                  saved_at: new Date().toISOString()
                });
                try {
                  localStorage.setItem("panchang_palm_profile", JSON.stringify(state.palmProfile));
                } catch (err) {}
                syncPalmControlsFromState();
                markDirty("Uploaded & analyzed Palm Photo — click Evaluate to combine Palm + Birth Chart + Vastu");
              }
            }
          } catch (err) {}
        };
        reader.readAsDataURL(file);
      });
    }

    // Sync Palm UI Controls
    const palmShapeSel = root.querySelector(".va-palm-shape");
    const palmLifeSel = root.querySelector(".va-palm-life");
    const palmHeadSel = root.querySelector(".va-palm-head");
    const palmHeartSel = root.querySelector(".va-palm-heart");
    const palmFateSel = root.querySelector(".va-palm-fate");
    const palmThumbSel = root.querySelector(".va-palm-thumb");
    const palmFileInp = root.querySelector(".va-palm-file");
    const palmStatusBadge = root.querySelector(".va-palm-status-badge");

    function syncPalmControlsFromState() {
      const pp = state.palmProfile || {};
      if (palmShapeSel && pp.hand_shape) palmShapeSel.value = pp.hand_shape;
      if (palmLifeSel && pp.life_line) palmLifeSel.value = pp.life_line;
      if (palmHeadSel && pp.head_line) palmHeadSel.value = pp.head_line;
      if (palmHeartSel && pp.heart_line) palmHeartSel.value = pp.heart_line;
      if (palmFateSel && pp.fate_line) palmFateSel.value = pp.fate_line;
      if (palmThumbSel && pp.thumbprint_type) palmThumbSel.value = pp.thumbprint_type;
      if (palmStatusBadge) {
        palmStatusBadge.textContent = pp.has_uploaded_photo
          ? `✅ Uploaded Palm Photo Active (${(pp.hand_shape || 'fire').toUpperCase()} Hand)`
          : `🖐️ Palm Profile: ${(pp.hand_shape || 'fire').toUpperCase()} Hand`;
        palmStatusBadge.style.background = pp.has_uploaded_photo ? "#dcfce7" : "#fed7aa";
        palmStatusBadge.style.color = pp.has_uploaded_photo ? "#166534" : "#7c2d12";
      }
    }
    syncPalmControlsFromState();

    function onPalmControlChange() {
      state.palmProfile = Object.assign({}, state.palmProfile, {
        hand_shape: palmShapeSel ? palmShapeSel.value : "fire",
        life_line: palmLifeSel ? palmLifeSel.value : "deep",
        head_line: palmHeadSel ? palmHeadSel.value : "long",
        heart_line: palmHeartSel ? palmHeartSel.value : "curved",
        fate_line: palmFateSel ? palmFateSel.value : "clear",
        thumbprint_type: palmThumbSel ? palmThumbSel.value : "chakra_whorl",
        thumbprint_name: palmThumbSel ? palmThumbSel.options[palmThumbSel.selectedIndex].text : "Chakra Rekha"
      });
      try {
        localStorage.setItem("panchang_palm_profile", JSON.stringify(state.palmProfile));
      } catch (e) {}
      syncPalmControlsFromState();
      markDirty("Updated Palm features for Palm + Chart + Vastu synthesis");
    }

    [palmShapeSel, palmLifeSel, palmHeadSel, palmHeartSel, palmFateSel, palmThumbSel].forEach(sel => {
      if (sel) sel.addEventListener("change", onPalmControlChange);
    });

    if (palmFileInp) {
      palmFileInp.addEventListener("change", e => {
        const file = e.target.files && e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = async ev => {
          try {
            const r = await fetch("/api/palmistry/analyze-photo", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                image_base64: ev.target.result,
                birth_date: (birthMeta && birthMeta.date) || "1990-05-15",
                birth_time: (birthMeta && birthMeta.time) || "10:30:00",
                latitude: (birthMeta && birthMeta.lat) || 28.6139,
                longitude: (birthMeta && birthMeta.lon) || 77.2090,
                timezone: (birthMeta && birthMeta.tz) || "Asia/Kolkata"
              })
            });
            if (r.ok) {
              const pData = await r.json();
              if (pData.extracted_palm_profile) {
                state.palmProfile = Object.assign({}, pData.extracted_palm_profile, {
                  has_uploaded_photo: true,
                  saved_at: new Date().toISOString()
                });
                try {
                  localStorage.setItem("panchang_palm_profile", JSON.stringify(state.palmProfile));
                } catch (err) {}
                syncPalmControlsFromState();
                markDirty("Uploaded & analyzed Palm Photo — click Evaluate to combine Palm + Birth Chart + Vastu");
              }
            }
          } catch (err) {}
        };
        reader.readAsDataURL(file);
      });
    }

    if (evalBtnTop) evalBtnTop.addEventListener("click", () => runAnalyze());
    if (evalBtnBot) evalBtnBot.addEventListener("click", () => {
      runAnalyze();
      reportEl.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    if (shapeSel) {
      shapeSel.addEventListener("change", () => {
        state.houseShape = shapeSel.value;
        renderCanvas();
        markDirty("House shape changed");
      });
    }
    if (lotChk) {
      lotChk.addEventListener("change", () => {
        state.hasOuterLot = lotChk.checked;
        renderCanvas();
        markDirty("Outer lot toggle changed");
      });
    }
    if (rotSel) {
      rotSel.addEventListener("change", () => {
        state.compassRotation = parseFloat(rotSel.value) || 0;
        renderCanvas();
        renderInspector();
        markDirty("Compass orientation rotated");
      });
    }

    // Add item buttons
    root.querySelectorAll("[data-va-add]").forEach(btn => {
      btn.addEventListener("click", () => {
        const type = btn.getAttribute("data-va-add");
        const meta = CATALOG[type] || CATALOG.living_room;
        const countSame = state.items.filter(i => i.type === type).length + 1;
        const label = countSame > 1 ? `${meta.label} #${countSame}` : meta.label;
        const isOut = meta.scope === "outdoor";
        if (isOut && !state.hasOuterLot) {
          state.hasOuterLot = true;
          if (lotChk) lotChk.checked = true;
        }
        const newItem = {
          id: state.nextId++,
          type: type,
          label: label,
          x: isOut ? (8 + (countSame * 9) % 72) : (32 + (countSame * 5) % 26),
          y: isOut ? (4 + (countSame * 7) % 12) : (32 + (countSame * 5) % 26),
          w: meta.w,
          h: meta.h,
          door_dir: meta.defaultDoor || "",
          gate_mech: meta.defaultGateMech || "",
          wall_side: meta.defaultWallSide || "",
          flow_dir: meta.defaultFlowDir || "",
          scope: meta.scope
        };
        state.items.push(newItem);
        state.selectedId = newItem.id;
        renderCanvas();
        renderInspector();
        markDirty(`Added ${newItem.label}`);
      });
    });

    // Preset buttons
    const btnChartIdeal = root.querySelector(".va-btn-chart-ideal");
    if (btnChartIdeal) {
      btnChartIdeal.addEventListener("click", () => {
        const p = (birthMeta && birthMeta.personalizedPreset && Array.isArray(birthMeta.personalizedPreset.items))
          ? birthMeta.personalizedPreset
          : getStandardIdealPreset();
        state.presetTitle = p.preset_title || "Personalized Birth-Chart Ideal Vastu & Feng Shui Setting";
        state.items = JSON.parse(JSON.stringify(p.items || []));
        state.walls = JSON.parse(JSON.stringify(p.walls || []));
        state.fences = JSON.parse(JSON.stringify(p.fences || []));
        state.selectedId = state.items[0]?.id || null;
        updatePresetBanner();
        renderCanvas();
        renderInspector();
        runAnalyze();
      });
    }

    const btnIdeal = root.querySelector(".va-btn-ideal");
    if (btnIdeal) {
      btnIdeal.addEventListener("click", () => {
        const p = getStandardIdealPreset();
        state.presetTitle = p.preset_title;
        state.items = JSON.parse(JSON.stringify(p.items));
        state.walls = JSON.parse(JSON.stringify(p.walls));
        state.fences = JSON.parse(JSON.stringify(p.fences));
        state.selectedId = state.items[0]?.id || null;
        updatePresetBanner();
        renderCanvas();
        renderInspector();
        runAnalyze();
      });
    }

    const btnDosha = root.querySelector(".va-btn-dosha-demo");
    if (btnDosha) {
      btnDosha.addEventListener("click", () => {
        const p = getDoshaDemoPreset();
        state.presetTitle = p.preset_title;
        state.items = JSON.parse(JSON.stringify(p.items));
        state.walls = JSON.parse(JSON.stringify(p.walls));
        state.fences = JSON.parse(JSON.stringify(p.fences));
        state.selectedId = state.items[0]?.id || null;
        updatePresetBanner();
        renderCanvas();
        renderInspector();
        runAnalyze();
      });
    }

    const btnClear = root.querySelector(".va-btn-clear");
    if (btnClear) {
      btnClear.addEventListener("click", () => {
        state.presetTitle = "Custom Blank Floorplan";
        state.items = [];
        state.walls = [];
        state.fences = [];
        state.selectedId = null;
        updatePresetBanner();
        renderCanvas();
        renderInspector();
        markDirty("Cleared all items, walls, and fences");
      });
    }

    // Wall Line Drawing Controls
    if (drawWallBtn) {
      drawWallBtn.addEventListener("click", () => {
        state.drawWallMode = !state.drawWallMode;
        if (state.drawWallMode) {
          state.drawFenceMode = false;
          if (customFenceBar) customFenceBar.style.display = "none";
          drawWallBtn.style.background = "#dc2626";
          drawWallBtn.textContent = "🧱 Drawing Wall Lines: ON (Drag on Canvas)";
          canvasEl.style.cursor = "crosshair";
        } else {
          drawWallBtn.style.background = "#334155";
          drawWallBtn.textContent = "✏️ Draw Wall Line: OFF";
          canvasEl.style.cursor = "default";
        }
      });
    }
    if (undoWallBtn) {
      undoWallBtn.addEventListener("click", () => {
        if (state.walls.length > 0) {
          state.walls.pop();
          renderCanvas();
          markDirty("Removed last drawn wall line");
        }
      });
    }
    if (clearWallsBtn) {
      clearWallsBtn.addEventListener("click", () => {
        state.walls = [];
        renderCanvas();
        markDirty("Cleared all drawn wall lines");
      });
    }

    // Perimeter Fence Loop Controls
    if (applyFenceBtn) {
      applyFenceBtn.addEventListener("click", () => {
        const mode = fencePresetSel ? fencePresetSel.value : "closed";
        const fp = buildFencePresetPoints(mode);
        state.fences = [{
          id: state.nextId++,
          label: fp.label,
          closed: fp.closed,
          open_side: fp.open_side,
          points: fp.points
        }];
        renderCanvas();
        markDirty(`Applied ${fp.label}`);
      });
    }
    if (drawFenceBtn) {
      drawFenceBtn.addEventListener("click", () => {
        state.drawFenceMode = true;
        state.drawWallMode = false;
        state.fenceDraftPoints = [];
        if (drawWallBtn) {
          drawWallBtn.style.background = "#334155";
          drawWallBtn.textContent = "✏️ Draw Wall Line: OFF";
        }
        if (customFenceBar) customFenceBar.style.display = "flex";
        if (fencePtCountEl) fencePtCountEl.textContent = "0";
        canvasEl.style.cursor = "crosshair";
        renderCanvas();
      });
    }
    if (finishFenceClosedBtn) {
      finishFenceClosedBtn.addEventListener("click", () => {
        if (state.fenceDraftPoints.length >= 3) {
          state.fences.push({
            id: state.nextId++,
            label: `Custom Closed-Loop Fence (${state.fenceDraftPoints.length} vertices)`,
            closed: true,
            open_side: "",
            points: state.fenceDraftPoints.slice()
          });
          markDirty("Added custom closed-loop perimeter fence");
        }
        state.drawFenceMode = false;
        state.fenceDraftPoints = [];
        if (customFenceBar) customFenceBar.style.display = "none";
        canvasEl.style.cursor = "default";
        renderCanvas();
      });
    }
    if (finishFenceOpenBtn) {
      finishFenceOpenBtn.addEventListener("click", () => {
        if (state.fenceDraftPoints.length >= 2) {
          const first = state.fenceDraftPoints[0];
          const last = state.fenceDraftPoints[state.fenceDraftPoints.length - 1];
          const gapMidX = (first.x + last.x) / 2;
          const gapMidY = (first.y + last.y) / 2;
          const openZone = detectZone(gapMidX, gapMidY, state.compassRotation);
          state.fences.push({
            id: state.nextId++,
            label: `Custom Open-Loop Fence (Open toward ${openZone})`,
            closed: false,
            open_side: openZone,
            points: state.fenceDraftPoints.slice()
          });
          markDirty(`Added custom open-loop fence (open at ${openZone})`);
        }
        state.drawFenceMode = false;
        state.fenceDraftPoints = [];
        if (customFenceBar) customFenceBar.style.display = "none";
        canvasEl.style.cursor = "default";
        renderCanvas();
      });
    }
    if (cancelFenceBtn) {
      cancelFenceBtn.addEventListener("click", () => {
        state.drawFenceMode = false;
        state.fenceDraftPoints = [];
        if (customFenceBar) customFenceBar.style.display = "none";
        canvasEl.style.cursor = "default";
        renderCanvas();
      });
    }
    if (clearFenceBtn) {
      clearFenceBtn.addEventListener("click", () => {
        state.fences = [];
        state.fenceDraftPoints = [];
        renderCanvas();
        markDirty("Cleared perimeter fence loop");
      });
    }

    // Canvas Mouse Handling for Wall Line Drawing & Custom Fence Loop Clicking
    canvasEl.addEventListener("mousedown", e => {
      const rect = canvasEl.getBoundingClientRect();
      const clickX = Math.max(1, Math.min(99, Math.round(((e.clientX - rect.left) / rect.width) * 100)));
      const clickY = Math.max(1, Math.min(99, Math.round(((e.clientY - rect.top) / rect.height) * 100)));

      if (state.drawFenceMode) {
        e.stopPropagation();
        state.fenceDraftPoints.push({ x: clickX, y: clickY });
        if (fencePtCountEl) fencePtCountEl.textContent = String(state.fenceDraftPoints.length);
        renderCanvas();
        return;
      }

      if (!state.drawWallMode) return;
      e.stopPropagation();
      state.wallDraft = { x1: clickX, y1: clickY, x2: clickX, y2: clickY };

      function onWallMove(ev) {
        let nx = Math.max(1, Math.min(99, Math.round(((ev.clientX - rect.left) / rect.width) * 100)));
        let ny = Math.max(1, Math.min(99, Math.round(((ev.clientY - rect.top) / rect.height) * 100)));
        if (orthoChk && orthoChk.checked) {
          if (Math.abs(nx - state.wallDraft.x1) > Math.abs(ny - state.wallDraft.y1)) {
            ny = state.wallDraft.y1;
          } else {
            nx = state.wallDraft.x1;
          }
        }
        state.wallDraft.x2 = nx;
        state.wallDraft.y2 = ny;
        renderCanvas();
      }

      function onWallUp() {
        window.removeEventListener("mousemove", onWallMove);
        window.removeEventListener("mouseup", onWallUp);
        if (state.wallDraft) {
          const len = Math.hypot(state.wallDraft.x2 - state.wallDraft.x1, state.wallDraft.y2 - state.wallDraft.y1);
          if (len >= 4) {
            const z = detectZone((state.wallDraft.x1 + state.wallDraft.x2) / 2, (state.wallDraft.y1 + state.wallDraft.y2) / 2, state.compassRotation);
            state.walls.push({
              id: state.nextId++,
              label: `Wall #${state.walls.length + 1} (${z})`,
              x1: state.wallDraft.x1,
              y1: state.wallDraft.y1,
              x2: state.wallDraft.x2,
              y2: state.wallDraft.y2
            });
            markDirty(`Drew Wall #${state.walls.length} in ${z}`);
          }
          state.wallDraft = null;
          renderCanvas();
        }
      }

      window.addEventListener("mousemove", onWallMove);
      window.addEventListener("mouseup", onWallUp);
    });

    function getHouseBoundsPercent() {
      if (!state.hasOuterLot) {
        if (state.houseShape === "wide_rectangle") return { left: 4, top: 14, width: 92, height: 72 };
        if (state.houseShape === "deep_rectangle") return { left: 14, top: 4, width: 72, height: 92 };
        return { left: 6, top: 6, width: 88, height: 88 };
      }
      if (state.houseShape === "wide_rectangle") return { left: 12, top: 22, width: 76, height: 56 };
      if (state.houseShape === "deep_rectangle") return { left: 22, top: 12, width: 56, height: 76 };
      return { left: 16, top: 16, width: 68, height: 68 };
    }

    function renderSvgOverlay() {
      if (!svgLayerEl) return;
      let svgHtml = "";

      // 1. Render Perimeter Fence Loops (Closed or Open)
      if (state.hasOuterLot) {
        state.fences.forEach(f => {
          const pts = f.points || [];
          if (pts.length < 2) return;
          const ptStr = pts.map(p => `${p.x},${p.y}`).join(" ");
          const strokeColor = f.closed ? "#15803d" : (["SW", "S", "W", "SE"].includes(f.open_side) ? "#dc2626" : "#d97706");
          if (f.closed) {
            svgHtml += `<polygon points="${ptStr}" fill="none" stroke="${strokeColor}" stroke-width="1.3" stroke-dasharray="2.5,1.2" opacity="0.92"/>`;
          } else {
            svgHtml += `<polyline points="${ptStr}" fill="none" stroke="${strokeColor}" stroke-width="1.5" stroke-dasharray="2.5,1.2" opacity="0.95"/>`;
            const first = pts[0];
            const last = pts[pts.length - 1];
            const gx = (first.x + last.x) / 2;
            const gy = (first.y + last.y) / 2;
            svgHtml += `<text x="${gx}" y="${Math.max(5, Math.min(96, gy))}" fill="#dc2626" font-size="2.7" font-weight="bold" text-anchor="middle">🔓 OPEN FENCE GAP (${f.open_side || "Open"})</text>`;
          }
          pts.forEach(p => {
            svgHtml += `<circle cx="${p.x}" cy="${p.y}" r="1.1" fill="${strokeColor}" stroke="#fff" stroke-width="0.3"/>`;
          });
        });
      }

      // 2. Render Custom Fence Draft
      if (state.drawFenceMode && state.fenceDraftPoints.length > 0) {
        const ptStr = state.fenceDraftPoints.map(p => `${p.x},${p.y}`).join(" ");
        svgHtml += `<polyline points="${ptStr}" fill="none" stroke="#d97706" stroke-width="1.4" stroke-dasharray="1.5,1.5"/>`;
        state.fenceDraftPoints.forEach(p => {
          svgHtml += `<circle cx="${p.x}" cy="${p.y}" r="1.3" fill="#d97706" stroke="#fff" stroke-width="0.4"/>`;
        });
      }

      // 3. Render Drawn Wall Lines
      state.walls.forEach(w => {
        const mx = (w.x1 + w.x2) / 2;
        const my = (w.y1 + w.y2) / 2;
        const crossesCenter = Math.hypot(mx - 50, my - 50) < 10.5;
        const wallColor = crossesCenter ? "#dc2626" : "#44403c";
        svgHtml += `
          <line x1="${w.x1}" y1="${w.y1}" x2="${w.x2}" y2="${w.y2}" stroke="${wallColor}" stroke-width="1.6" stroke-linecap="square"/>
          <circle cx="${w.x1}" cy="${w.y1}" r="0.9" fill="#1c1917"/>
          <circle cx="${w.x2}" cy="${w.y2}" r="0.9" fill="#1c1917"/>
          <text x="${mx}" y="${my - 1.2}" fill="${wallColor}" font-size="2.2" font-weight="bold" text-anchor="middle">🧱 ${w.label}</text>
        `;
      });

      // 4. Render Active Wall Line Draft
      if (state.wallDraft) {
        svgHtml += `<line x1="${state.wallDraft.x1}" y1="${state.wallDraft.y1}" x2="${state.wallDraft.x2}" y2="${state.wallDraft.y2}" stroke="#dc2626" stroke-width="1.6" stroke-dasharray="2,1"/>`;
      }

      svgLayerEl.innerHTML = svgHtml;
    }

    function renderCanvas() {
      const hb = getHouseBoundsPercent();
      houseBoxEl.style.left = hb.left + "%";
      houseBoxEl.style.top = hb.top + "%";
      houseBoxEl.style.width = hb.width + "%";
      houseBoxEl.style.height = hb.height + "%";

      if (lotWatermarkEl) {
        lotWatermarkEl.style.display = state.hasOuterLot ? "block" : "none";
      }

      canvasEl.style.background = state.hasOuterLot
        ? "repeating-linear-gradient(45deg, #f0fdf4, #f0fdf4 14px, #dcfce7 14px, #dcfce7 28px)"
        : "#f8fafc";

      const baseDirs = [
        { code: "N",  label: "N (Kubera / Career)" },
        { code: "NE", label: "NE (Ishanya / Wisdom)" },
        { code: "E",  label: "E (Surya / Green Dragon)" },
        { code: "SE", label: "SE (Agni / Wealth)" },
        { code: "S",  label: "S (Yama / Fame)" },
        { code: "SW", label: "SW (Nairutya / Stability)" },
        { code: "W",  label: "W (Varuna / White Tiger)" },
        { code: "NW", label: "NW (Vayu / Mentors)" }
      ];
      root.querySelectorAll(".va-compass-tag").forEach((el, i) => {
        const shiftIdx = Math.round(state.compassRotation / 45) % 8;
        const dInfo = baseDirs[(i - shiftIdx + 8) % 8];
        el.textContent = dInfo.label;
      });

      renderSvgOverlay();

      itemsLayerEl.innerHTML = "";
      state.items.forEach(item => {
        if (!state.hasOuterLot && (item.scope === "outdoor" || item.scope === "outside_boundary")) return;
        const meta = CATALOG[item.type] || CATALOG.living_room;
        const cx = item.x + item.w / 2;
        const cy = item.y + item.h / 2;
        const zone = detectZone(cx, cy, state.compassRotation);

        const ideals = IDEAL_MAP[item.type] || [];
        const bads = BAD_MAP[item.type] || [];
        let statusColor = "#d97706";
        let statusBg = meta.bg;
        if (ideals.includes(zone)) {
          statusColor = "#15803d";
        } else if (bads.includes(zone)) {
          statusColor = "#dc2626";
          statusBg = "#fee2e2";
        }

        // Check gate_mech or flow_dir or wall_side overrides for visual badge color
        if (item.gate_mech === "swing_out" || item.gate_mech === "slide_sw") {
          statusColor = "#dc2626";
        }
        if (item.type === "trench_ditch" && ["SW", "S", "W", "stagnant"].includes(item.flow_dir)) {
          statusColor = "#dc2626";
          statusBg = "#fee2e2";
        }
        if (item.type === "photo_deceased" && item.wall_side && !["S", "SW"].includes(item.wall_side)) {
          statusColor = "#dc2626";
          statusBg = "#fee2e2";
        }

        const isOutScope = item.scope === "outdoor" || item.scope === "outside_boundary";
        const el = document.createElement("div");
        el.className = "va-block" + (item.id === state.selectedId ? " va-selected" : "");
        el.style.cssText = `
          position: absolute;
          left: ${item.x}%;
          top: ${item.y}%;
          width: ${item.w}%;
          height: ${item.h}%;
          background: ${statusBg};
          border: 2.5px ${isOutScope ? "dashed" : "solid"} ${item.id === state.selectedId ? "#0f172a" : statusColor};
          border-radius: 6px;
          box-sizing: border-box;
          cursor: ${state.drawWallMode || state.drawFenceMode ? "crosshair" : "move"};
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 2px 3px;
          text-align: center;
          user-select: none;
          box-shadow: ${item.id === state.selectedId ? "0 0 0 3px rgba(245,158,11,0.65)" : "0 2px 4px rgba(0,0,0,0.12)"};
          z-index: ${item.id === state.selectedId ? 30 : (isOutScope ? 12 : 20)};
          overflow: hidden;
          pointer-events: ${state.drawWallMode || state.drawFenceMode ? "none" : "auto"};
        `;

        const extraBadges = [];
        if (item.door_dir) {
          extraBadges.push(`Face ${DOOR_ARROWS[item.door_dir] || item.door_dir}`);
        }
        if (item.wall_side) {
          extraBadges.push(`${item.wall_side} Wall`);
        }
        if (item.gate_mech) {
          const shortMech = {
            swing_in_cw: "In-CW",
            swing_in_ccw: "In-CCW",
            double_in: "2-Leaf",
            swing_out: "Outward!",
            slide_ne: "Slide→NE",
            slide_sw: "Slide→SW!",
            rollup: "Roll-Up"
          }[item.gate_mech] || item.gate_mech;
          extraBadges.push(shortMech);
        }
        if (item.flow_dir) {
          extraBadges.push(`Flow→${item.flow_dir}`);
        }
        if (item.scope === "outside_boundary") {
          extraBadges.push("Outside Prop.");
        }

        const badgeLine = extraBadges.length
          ? `<span style="font-size:8.5px;background:#1e293b;color:#fff;padding:0 4px;border-radius:3px;margin-top:1px;white-space:nowrap;max-width:98%;overflow:hidden;text-overflow:ellipsis;">${extraBadges.join(" · ")}</span>`
          : "";

        el.innerHTML = `
          <div style="font-size:10.5px;font-weight:700;line-height:1.12;color:#111827;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%;">
            ${meta.icon} ${item.label}
          </div>
          <div style="font-size:9.5px;font-weight:800;color:${statusColor};line-height:1.05;">
            [${zone}]
          </div>
          ${badgeLine}
          <div class="va-resize-handle" title="Drag corner to resize" style="position:absolute;right:0;bottom:0;width:11px;height:11px;background:${statusColor};cursor:nwse-resize;border-top-left-radius:4px;"></div>
        `;

        el.addEventListener("mousedown", e => {
          if (state.drawWallMode || state.drawFenceMode) return;
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
          let moved = false;

          function onMove(ev) {
            const dxPct = ((ev.clientX - startX) / rect.width) * 100;
            const dyPct = ((ev.clientY - startY) / rect.height) * 100;
            if (Math.abs(dxPct) > 0.4 || Math.abs(dyPct) > 0.4) moved = true;
            if (isResize) {
              item.w = Math.max(5, Math.min(96 - item.x, Math.round(origW + dxPct)));
              item.h = Math.max(4, Math.min(96 - item.y, Math.round(origH + dyPct)));
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
            if (moved) {
              markDirty(`Moved/resized ${item.label}`);
            }
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
        inspectorEl.innerHTML = `<div class="neutral" style="font-size:13px;">👆 Click any room, temple, medication cabinet, stove, tap, photo frame, TV, gate, or trench on the canvas above to customize its direction, wall side, gate swing/slide mechanics, or drainage flow. Then click <b>🔍 Evaluate</b>!</div>`;
        return;
      }
      const meta = CATALOG[item.type] || {};
      const zone = detectZone(item.x + item.w / 2, item.y + item.h / 2, state.compassRotation);
      const dirs = ["", "N", "NE", "E", "SE", "S", "SW", "W", "NW"];
      const dirOpts = dirs.map(d => `<option value="${d}" ${item.door_dir === d ? "selected" : ""}>${d ? "Facing " + d + " (" + DOOR_ARROWS[d] + ")" : "No Direction / N/A"}</option>`).join("");

      const showGateMech = meta.hasGateMech || ["gate", "parking_gate", "side_pedestrian_gate", "entrance", "back_door"].includes(item.type);
      const gateMechHtml = showGateMech ? `
        <div>
          <label style="font-size:11.5px;font-weight:700;display:block;color:#92400e;">🚪 Gate / Door Opening or Sliding Side</label>
          <select class="va-inp-gatemech" style="padding:5px 8px;border:1px solid #f59e0b;border-radius:4px;background:#fffbeb;font-weight:600;">
            ${GATE_MECH_OPTIONS.map(o => `<option value="${o.value}" ${(item.gate_mech || "") === o.value ? "selected" : ""}>${o.label}</option>`).join("")}
          </select>
        </div>
      ` : "";

      const showWallSide = meta.hasWallSide || ["photo_living", "photo_deceased", "photo_gods", "tv_screen", "wall_mirror", "wall_clock"].includes(item.type);
      const wallSideHtml = showWallSide ? `
        <div>
          <label style="font-size:11.5px;font-weight:700;display:block;color:#9d174d;">🖼️ Mounted on Which Wall of Room?</label>
          <select class="va-inp-wallside" style="padding:5px 8px;border:1px solid #f472b6;border-radius:4px;background:#fdf2f8;font-weight:600;">
            ${WALL_SIDE_OPTIONS.map(o => `<option value="${o.value}" ${(item.wall_side || "") === o.value ? "selected" : ""}>${o.label}</option>`).join("")}
          </select>
        </div>
      ` : "";

      const showFlowDir = meta.hasFlowDir || item.type === "trench_ditch";
      const flowDirHtml = showFlowDir ? `
        <div>
          <label style="font-size:11.5px;font-weight:700;display:block;color:#0369a1;">🕳️ Trench / Ditch Water Flow Direction</label>
          <select class="va-inp-flowdir" style="padding:5px 8px;border:1px solid #38bdf8;border-radius:4px;background:#f0f9ff;font-weight:600;">
            ${FLOW_DIR_OPTIONS.map(o => `<option value="${o.value}" ${(item.flow_dir || "") === o.value ? "selected" : ""}>${o.label}</option>`).join("")}
          </select>
        </div>
      ` : "";

      inspectorEl.innerHTML = `
        <div style="display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;justify-content:space-between;">
          <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;">
            <div>
              <label style="font-size:11.5px;font-weight:700;display:block;color:#1e293b;">Selected Item (${zone} Zone)</label>
              <input type="text" class="va-inp-label" value="${item.label}" style="padding:5px 8px;border:1px solid #cbd5e1;border-radius:4px;width:185px;font-weight:600;">
            </div>
            <div>
              <label style="font-size:11.5px;font-weight:700;display:block;color:#1e293b;">Door / Cook / Photo / TV Facing</label>
              <select class="va-inp-door" style="padding:5px 8px;border:1px solid #cbd5e1;border-radius:4px;">${dirOpts}</select>
            </div>
            ${gateMechHtml}
            ${wallSideHtml}
            ${flowDirHtml}
            <div>
              <label style="font-size:11.5px;font-weight:700;display:block;color:#1e293b;">Location Scope (In / Out Property)</label>
              <select class="va-inp-scope" style="padding:5px 8px;border:1px solid #cbd5e1;border-radius:4px;">
                <option value="indoor" ${item.scope === "indoor" ? "selected" : ""}>🏠 Inside House</option>
                <option value="outdoor" ${item.scope === "outdoor" ? "selected" : ""}>🌳 Inside Property Yard / Lot</option>
                <option value="outside_boundary" ${item.scope === "outside_boundary" ? "selected" : ""}>🛣️ Outside Property Boundary (Street/Adjoining)</option>
              </select>
            </div>
            <div>
              <label style="font-size:11.5px;font-weight:700;display:block;color:#1e293b;">W %</label>
              <input type="number" class="va-inp-w" min="5" max="85" value="${item.w}" style="padding:5px 6px;border:1px solid #cbd5e1;border-radius:4px;width:56px;">
            </div>
            <div>
              <label style="font-size:11.5px;font-weight:700;display:block;color:#1e293b;">H %</label>
              <input type="number" class="va-inp-h" min="4" max="85" value="${item.h}" style="padding:5px 6px;border:1px solid #cbd5e1;border-radius:4px;width:56px;">
            </div>
          </div>
          <div style="display:flex;gap:7px;">
            <button type="button" class="btn va-btn-dup" style="background:#0f766e;color:#fff;padding:6px 11px;font-size:11.5px;font-weight:700;">➕ Duplicate</button>
            <button type="button" class="btn va-btn-del" style="background:#dc2626;color:#fff;padding:6px 11px;font-size:11.5px;font-weight:700;">🗑️ Remove</button>
          </div>
        </div>
      `;

      inspectorEl.querySelector(".va-inp-label").addEventListener("input", e => {
        item.label = e.target.value;
        renderCanvas();
        markDirty(`Renamed ${item.label}`);
      });
      inspectorEl.querySelector(".va-inp-door").addEventListener("change", e => {
        item.door_dir = e.target.value;
        renderCanvas();
        markDirty(`Updated facing direction for ${item.label}`);
      });
      const gmSel = inspectorEl.querySelector(".va-inp-gatemech");
      if (gmSel) {
        gmSel.addEventListener("change", e => {
          item.gate_mech = e.target.value;
          renderCanvas();
          markDirty(`Updated gate/door opening mechanics for ${item.label}`);
        });
      }
      const wsSel = inspectorEl.querySelector(".va-inp-wallside");
      if (wsSel) {
        wsSel.addEventListener("change", e => {
          item.wall_side = e.target.value;
          renderCanvas();
          markDirty(`Updated wall mounting side for ${item.label}`);
        });
      }
      const fdSel = inspectorEl.querySelector(".va-inp-flowdir");
      if (fdSel) {
        fdSel.addEventListener("change", e => {
          item.flow_dir = e.target.value;
          renderCanvas();
          markDirty(`Updated trench drainage direction for ${item.label}`);
        });
      }
      inspectorEl.querySelector(".va-inp-scope").addEventListener("change", e => {
        item.scope = e.target.value;
        renderCanvas();
        markDirty(`Updated property scope for ${item.label}`);
      });
      inspectorEl.querySelector(".va-inp-w").addEventListener("change", e => {
        item.w = Math.max(5, Math.min(85, parseInt(e.target.value, 10) || item.w));
        renderCanvas();
        markDirty(`Resized ${item.label}`);
      });
      inspectorEl.querySelector(".va-inp-h").addEventListener("change", e => {
        item.h = Math.max(4, Math.min(85, parseInt(e.target.value, 10) || item.h));
        renderCanvas();
        markDirty(`Resized ${item.label}`);
      });
      inspectorEl.querySelector(".va-btn-dup").addEventListener("click", () => {
        const copy = Object.assign({}, item, {
          id: state.nextId++,
          label: item.label + " #2",
          x: Math.min(84, item.x + 5),
          y: Math.min(84, item.y + 5)
        });
        state.items.push(copy);
        state.selectedId = copy.id;
        renderCanvas();
        renderInspector();
        markDirty(`Duplicated ${item.label}`);
      });
      inspectorEl.querySelector(".va-btn-del").addEventListener("click", () => {
        const removedLabel = item.label;
        state.items = state.items.filter(i => i.id !== item.id);
        state.selectedId = state.items[0]?.id || null;
        renderCanvas();
        renderInspector();
        markDirty(`Removed ${removedLabel}`);
      });
    }

    async function runAnalyze() {
      if (!reportEl) return;
      const visibleItems = state.items.filter(i => state.hasOuterLot || (i.scope !== "outdoor" && i.scope !== "outside_boundary"));
      const payload = Object.assign({
        house_shape: state.houseShape,
        has_outer_lot: state.hasOuterLot,
        compass_rotation: state.compassRotation,
        items: visibleItems,
        walls: state.walls,
        fences: state.hasOuterLot ? state.fences : [],
        palm_data: state.palmProfile
      }, birthMeta || {});

      try {
        const r = await fetch("/api/vastu/analyze-layout", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        if (!r.ok) return;
        const data = await r.json();
        markClean();
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
            <td><b>${it.door_or_gate_facing}</b></td>
            <td><span class="badge" style="${badgeStyle}">${it.status} (${it.score_out_of_10}/10)</span><br><small>Ideal: ${(it.ideal_zones_for_this_item || []).join(", ")}</small></td>
            <td>
              <div>${it.verdict_in_simple_words}</div>
              <div style="margin-top:4px;font-size:12px;color:#475569;"><b>Vastu Rule:</b> ${it.why_this_rule_exists}</div>
              ${it.birth_chart_synergy ? `<div style="margin-top:4px;font-size:12px;color:#0f766e;"><b>🌟 ${it.birth_chart_synergy}</b></div>` : ""}
              ${it.feng_shui_bagua_harmony ? `<div style="margin-top:4px;font-size:12px;color:#6d28d9;"><b>☯️ ${it.feng_shui_bagua_harmony}</b></div>` : ""}
            </td>
            <td><small>${it.zero_demolition_remedy}</small></td>
          </tr>
        `;
      }).join("");

      const crossChecks = data.relational_cross_checks || [];
      const wallEvals = data.wall_line_evaluations || [];
      const fenceEvals = data.fence_loop_evaluations || [];
      const specialRows = [...crossChecks, ...fenceEvals, ...wallEvals].map(sp => {
        const isGood = (sp.status || "").includes("Auspicious") || (sp.status || "").includes("Balanced");
        const isBad = (sp.status || "").includes("Clash") || (sp.status || "").includes("Dosha") || (sp.status || "").includes("Sacrilege") || (sp.status || "").includes("Leak");
        const bStyle = isGood
          ? "background:#dcfce7;color:#15803d;border:1px solid #86efac;"
          : (isBad ? "background:#fee2e2;color:#b91c1c;border:1px solid #fca5a5;" : "background:#fef3c7;color:#b45309;border:1px solid #fde68a;");
        return `
          <tr>
            <td><strong>${sp.check}</strong></td>
            <td><span class="badge" style="${bStyle}">${sp.status}</span></td>
            <td>${sp.verdict}</td>
            <td><small>${sp.remedy}</small></td>
          </tr>
        `;
      }).join("");

      const specialSectionHtml = specialRows ? `
        <h3 style="margin-top:18px;">🔗 Relational Proximity Checks (Stove vs Taps, Ancestor vs Gods Photos, TV vs Bed), Fence Loops &amp; Wall Lines</h3>
        <div class="table-wrap" style="margin-bottom:16px;">
          <table>
            <thead>
              <tr>
                <th>Special Structural / Relational Check</th>
                <th>Status</th>
                <th>Vastu &amp; Classical Feng Shui Analysis</th>
                <th>Zero-Demolition Remedy / Action</th>
              </tr>
            </thead>
            <tbody>${specialRows}</tbody>
          </table>
        </div>
      ` : "";

      const doshasHtml = (data.critical_doshas_and_fixes || []).map(d => `<li style="margin-bottom:4px;">${d}</li>`).join("");
      const strengthsHtml = (data.auspicious_strengths || []).map(s => `<li style="margin-bottom:4px;">${s}</li>`).join("");

      reportEl.innerHTML = `
        <div class="grid-3" style="margin-top:14px;">
          <div class="stat">
            <span class="label">Evaluated Vastu &amp; Feng Shui Score</span>
            <span class="value" style="color:${scoreColor};font-size:1.6rem;">${data.overall_vastu_score_percent}%</span>
            <small><b>${data.overall_grade}</b> (${data.total_items_evaluated} elements evaluated)</small>
          </div>
          <div class="stat">
            <span class="label">House Shape Geometry</span>
            <span class="value" style="font-size:1rem;">${data.house_shape_analysis.name}</span>
            <small>${data.house_shape_analysis.explanation}</small>
          </div>
          <div class="stat">
            <span class="label">Outer Lot, Fence &amp; Walls</span>
            <span class="value" style="font-size:1rem;">${(data.fence_loop_evaluations || []).length} Fence Loop · ${(data.wall_line_evaluations || []).length} Wall Lines</span>
            <small>Compass Rotation: ${data.compass_rotation_degrees}° from True North</small>
          </div>
        </div>

        <div class="grid-2" style="margin-top:16px;">
          <div style="padding:14px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;">
            <h4 style="margin-top:0;color:#15803d;">✅ Auspicious Placements Boosting Your Chart &amp; Qi</h4>
            <ul style="margin:0;padding-left:18px;font-size:13px;">${strengthsHtml}</ul>
          </div>
          <div style="padding:14px;background:#fef2f2;border:1px solid #fecaca;border-radius:8px;">
            <h4 style="margin-top:0;color:#b91c1c;">🛠️ Detected Vastu / Feng Shui Defects &amp; Priority Fixes</h4>
            <ul style="margin:0;padding-left:18px;font-size:13px;">${doshasHtml}</ul>
          </div>
        </div>

        ${data.palm_vastu_chart_synthesis && data.palm_vastu_chart_synthesis.active ? `
        <div style="margin-top:18px;padding:15px;background:linear-gradient(135deg,#fff7ed 0%,#ffedd5 100%);border:1.5px solid #fb923c;border-radius:10px;">
          <h3 style="margin:0 0 6px 0;color:#9a3412;">${data.palm_vastu_chart_synthesis.headline}</h3>
          <p style="margin:0 0 12px 0;font-size:13px;color:#7c2d12;line-height:1.55;">${data.palm_vastu_chart_synthesis.summary}</p>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Palm Feature &amp; Mount</th>
                  <th>Birth-Chart Link</th>
                  <th>Floorplan Alignment</th>
                  <th>Combined Palm + Birth Chart + Vastu &amp; Feng Shui Insight</th>
                  <th>Combined Hasta-Astro-Vastu Remedy</th>
                </tr>
              </thead>
              <tbody>
                ${(data.palm_vastu_chart_synthesis.tri_system_checks || []).map(tc => `
                  <tr>
                    <td><strong>${tc.palm_feature}</strong></td>
                    <td><b>${tc.birth_chart_factor}</b></td>
                    <td><span class="badge" style="background:#dcfce7;color:#15803d;">${tc.floorplan_alignment_status}</span></td>
                    <td>${tc.combined_palm_chart_vastu_insight}</td>
                    <td><small>${tc.actionable_remedy}</small></td>
                  </tr>
                `).join("")}
              </tbody>
            </table>
          </div>
        </div>
        ` : ""}

        ${specialSectionHtml}

        <h3 style="margin-top:18px;">📐 Complete Item-by-Item Vastu + Birth-Chart + Feng Shui Breakdown</h3>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Placed Item &amp; Scope</th>
                <th>Compass Zone &amp; Element</th>
                <th>Facing / Wall / Gate / Flow</th>
                <th>Vastu Verdict &amp; Score</th>
                <th>Plain-English Vastu Rule, Birth-Chart Synergy &amp; Feng Shui Bagua</th>
                <th>Zero-Demolition Fix / Remedy</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      `;
    }

    updatePresetBanner();
    renderCanvas();
    renderInspector();
    // Run initial evaluation once on startup for the loaded Birth-Chart Ideal Preset
    runAnalyze();
  };
})();
