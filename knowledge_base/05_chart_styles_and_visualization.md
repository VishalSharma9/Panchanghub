# Classical Chart Styles & Visualization Architecture

## 1. The Four Classical Astrological Chart Formats

Vedic and Western astrology use four distinct visual representations to render celestial coordinates. Each visual format provides unique advantages for pattern recognition.

---

## 2. North Indian Chart (Diamond / Fixed-House Format)

### 2.1 Geometry & Cell Mapping
The North Indian chart is a square divided into 12 triangular and diamond-shaped houses. 
- **The houses remain strictly stationary**:
  - The top central diamond is ALWAYS House 1 (Ascendant / Lagna).
  - The other houses follow counter-clockwise:
    - House 2 (Top Left Triangle)
    - House 3 (Left Upper Triangle)
    - House 4 (Left Central Diamond)
    - House 5 (Left Lower Triangle)
    - House 6 (Bottom Left Triangle)
    - House 7 (Bottom Central Diamond)
    - House 8 (Bottom Right Triangle)
    - House 9 (Right Lower Triangle)
    - House 10 (Right Central Diamond)
    - House 11 (Right Upper Triangle)
    - House 12 (Top Right Triangle)
- **Sign placement**: The zodiac signs are written as numbers ($1 = \text{Aries}, \dots, 12 = \text{Pisces}$) inside the house cells.

### 2.2 Analytical Advantage
Provides instantaneous visual recognition of:
- **Kendra Houses** (1, 4, 7, 10 forms the central diamond cloverleaf).
- **Trikona Houses** (1, 5, 9 forms the auspicious triangular pillars).
- **Dusthanas** (6, 8, 12 located in the perimeter corners).

---

## 3. South Indian Chart (Box / Fixed-Sign Format)

### 3.1 Geometry & Cell Mapping
The South Indian chart is a $4 \times 4$ grid where the 4 central cells are empty (forming a central courtyard), leaving 12 outer perimeter cells.
- **The zodiac signs remain strictly stationary (Clockwise from top left)**:
  - Cell [0, 1] : Pisces (12)
  - Cell [0, 2] : Aries (1)
  - Cell [0, 3] : Taurus (2)
  - Cell [1, 3] : Gemini (3)
  - Cell [2, 3] : Cancer (4)
  - Cell [3, 3] : Leo (5)
  - Cell [3, 2] : Virgo (6)
  - Cell [3, 1] : Libra (7)
  - Cell [3, 0] : Scorpio (8)
  - Cell [2, 0] : Sagittarius (9)
  - Cell [1, 0] : Capricorn (10)
  - Cell [0, 0] : Aquarius (11)
- **Ascendant & Houses**: The Ascendant is marked with two diagonal slashes or the label "ASC" / "Lagna". Houses are counted clockwise from that cell.

### 3.2 Analytical Advantage
Provides instantaneous visual recognition of:
- Fixed planetary aspects (e.g. opposite signs are always diametrically opposed).
- Cross-divisional comparisons (Vargottama planets remain in the exact same physical grid cell across D1, D9, D10, etc.).

---

## 4. East Indian Chart (Bengali / Odia / Maithili Format)

### 4.1 Geometry & Cell Mapping
Similar to the North Indian square format with diagonal dividers, but:
- Zodiac signs remain fixed with Aries at the top central quadrant.
- Counting progresses in a counter-clockwise or reflective order.
- The Ascendant is marked explicitly across the corresponding sign cell.

---

## 5. Western Circular Wheel (Tropical / Aspect Arc Format)

### 5.1 Geometry & Cell Mapping
- A 360-degree circle divided into 12 pie wedges.
- The Ascendant is anchored on the eastern horizon (leftmost 9 o'clock position).
- Houses proceed counter-clockwise around the wheel.
- Planets are placed at their exact degree on the ecliptic circle.
- Exact geometric aspect chords are drawn across the interior circle:
  - Conjunction ($0^\circ$)
  - Sextile ($60^\circ$ - Blue)
  - Square ($90^\circ$ - Red)
  - Trine ($120^\circ$ - Green)
  - Opposition ($180^\circ$ - Red)

---

## 6. Color Palettes & Visual Accessibility

### 6.1 Traditional Vedic Palette
- **Primary / Background**: Deep Cream (`#FFFDF7`) or Saffron/Haldi Tint (`#FFF9E6`).
- **Borders & Grid Lines**: Kumkum Crimson (`#8B1E1E`) or Warm Terracotta (`#A04000`).
- **Benefic Planets (Jupiter, Venus, Moon, Mercury)**: Deep Green (`#1E7E34`) or Royal Azure (`#0B5ED7`).
- **Malefic Planets (Saturn, Mars, Rahu, Ketu, Sun)**: Deep Ruby (`#C82333`) or Charcoal Amber (`#495057`).

### 6.2 High-Contrast Modern Theme
- **Card Background**: Pure White (`#FFFFFF`).
- **Line Stroke**: Slate Navy (`#1E293B`).
- **Accents**: Gold (`#F59E0B`) and Indigo (`#4F46E5`).
