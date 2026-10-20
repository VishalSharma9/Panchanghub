# Classical Vedic Astronomical & Calculation Engines

## 1. Astronomical Principles & Time Reckoning

Vedic astrology (Jyotisha) relies on sidereal (Nirayana) planetary longitudes, which account for the precession of the equinoxes (*Ayanamsha*). 

### 1.1 Time Coordinates & Conversions
1. **Julian Day Number (JDN)**:
   All planetary calculations begin by converting civil datetime $(Y, M, D, h, m, s)$ with timezone offset $\Delta t_{\text{tz}}$ into Universal Time (UT1/UTC) and then into Julian Day ($JD$):
   $$JD = \text{julday}(Y, M, D, h_{\text{UT}}, \text{Gregorian})$$
2. **Delta T ($\Delta T$)**:
   The difference between Terrestrial Time (TT) and Universal Time (UT):
   $$\Delta T = TT - UT$$
   Planetary ephemerides evaluate orbital positions at Ephemeris Time / Terrestrial Dynamic Time ($JD_{ET} = JD_{UT} + \Delta T / 86400$).
3. **Local Sidereal Time (LST) & Ascendant (Lagna)**:
   The Ascendant is the degree of the zodiac rising on the eastern horizon at the local geographic latitude $\phi$ and longitude $\lambda$:
   $$\theta_0 = \text{GMST}(JD_{UT})$$
   $$\text{LST} = \theta_0 + \lambda / 15$$
   $$\tan(\text{Ascendant}_{\text{tropical}}) = \frac{-\cos(\text{LST})}{\sin(\text{LST})\cos(\epsilon) + \tan(\phi)\sin(\epsilon)}$$
   where $\epsilon$ is the true obliquity of the ecliptic.
4. **Sidereal Reduction**:
   $$\lambda_{\text{sidereal}} = (\lambda_{\text{tropical}} - \text{Ayanamsha}) \pmod{360^\circ}$$

---

## 2. Comprehensive Ayanamsha Systems

Ayanamsha represents the angular distance between the vernal equinox (0° tropical Aries) and the fixed sidereal zodiac (0° sidereal Mesha).

| System | Standard / Authority | Description & Zero Epoch |
|---|---|---|
| **Lahiri (Chitra Paksha)** | Indian Calendar Reform Committee | Star Chitra (Spica, $\alpha$ Virginis) fixed at exactly 180°00'00" (opposite 0° Aries). Zero year $\approx 285$ CE. |
| **Krishnamurti (KP Standard)** | Prof. K.S. Krishnamurti | Chitra Paksha aligned with 0°00' offset at 291 CE. Used universally in KP System. |
| **Krishnamurti New (New KP)** | Modern KP Research Foundation | Refined modern equinox motion with second-order precession correction. |
| **B.V. Raman** | Prof. B.V. Raman | Zero year fixed at 397 CE based on the Revati star system ($359^\circ 50'$). Rate of precession = 50.26" per year. |
| **Sri Yukteshwar** | Swami Sri Yukteshwar Giri (*The Holy Science*) | Zero year fixed at 499 CE based on astronomical alignment with Galactic Centre. |
| **Fagan-Bradley** | Cyril Fagan & Donald Bradley | Western Sidereal standard. Star Aldebaran fixed at 15°00'00" Taurus. |
| **J.N. Bhasin** | Pandit J.N. Bhasin | Northern Indian traditional ephemeris calibration with small empirical offset. |
| **Sayana (Tropical)** | Western / Ptolemaic | Zero Ayanamsha ($0^\circ00'00"$). Tropical zodiac measured directly from vernal equinox. |
| **Custom Offset** | User Arbitrary | Any manual angular shift $(\pm \Delta\theta)$ specified in degrees, minutes, and seconds. |

---

## 3. The 16 Divisional Charts (Shodashavargas)

Divisional charts map planetary longitudes into microscopic segments of zodiacal signs to reveal specific life domains.

Let:
- $L$ be the Nirayana longitude of a celestial body ($0^\circ \le L < 360^\circ$).
- $S = \lfloor L / 30^\circ \rfloor$ be the zero-indexed zodiac sign ($0 = \text{Aries}, \dots, 11 = \text{Pisces}$).
- $D = L \pmod{30^\circ}$ be the degree within the sign ($0^\circ \le D < 30^\circ$).
- $\text{IsOdd} = (S \pmod 2 == 0)$ (Aries = index 0 is odd, Taurus = index 1 is even).
- $\text{Modality} = S \pmod 3$ (0 = Movable / Chara, 1 = Fixed / Sthira, 2 = Dual / Dwisvabhava).

### 3.1 Mathematical Mapping Formulas for All 16 Vargas

1. **D1: Rashi Chart (Physical Body & Overall Destiny)**
   $$\text{Sign}_{D1} = S$$

2. **D2: Hora (Wealth, Prosperity & Speech - 15° halves)**
   - If sign is odd:
     $$\text{Sign}_{D2} = \begin{cases} 4 \ (\text{Leo / Sun}) & \text{if } D < 15^\circ \\ 3 \ (\text{Cancer / Moon}) & \text{if } D \ge 15^\circ \end{cases}$$
   - If sign is even:
     $$\text{Sign}_{D2} = \begin{cases} 3 \ (\text{Cancer / Moon}) & \text{if } D < 15^\circ \\ 4 \ (\text{Leo / Sun}) & \text{if } D \ge 15^\circ \end{cases}$$

3. **D3: Drekkana (Siblings, Courage & Energy - 10° thirds)**
   - Segment index: $k = \lfloor D / 10^\circ \rfloor \in \{0, 1, 2\}$.
   $$\text{Sign}_{D3} = (S + 4k) \pmod{12}$$

4. **D4: Chaturthamsa / Turyamsa (Property, Vehicles & Fixed Assets - 7°30' quarters)**
   - Segment index: $k = \lfloor D / 7.5^\circ \rfloor \in \{0, 1, 2, 3\}$.
   $$\text{Sign}_{D4} = (S + 3k) \pmod{12}$$

5. **D7: Saptamsa (Children, Progeny & Creative Lineage - 4°17'08.57" sevenths)**
   - Segment index: $k = \lfloor D / (30^\circ / 7) \rfloor \in \{0, \dots, 6\}$.
   $$\text{Sign}_{D7} = \begin{cases} (S + k) \pmod{12} & \text{if } \text{IsOdd} \\ (S + 6 + k) \pmod{12} & \text{if even} \end{cases}$$

6. **D9: Navamsa (Marriage, Dharma & Soul Purpose - 3°20' ninths)**
   - Total navamsa index in zodiac: $N = \lfloor L / (30^\circ / 9) \rfloor = \lfloor L / 3.333333^\circ \rfloor \in \{0, \dots, 107\}$.
   $$\text{Sign}_{D9} = N \pmod{12}$$
   *(Note: Fire signs start from Aries, Earth from Capricorn, Air from Libra, Water from Cancer).*

7. **D10: Dasamsa (Career, Profession & Social Status - 3° tenths)**
   - Segment index: $k = \lfloor D / 3.0^\circ \rfloor \in \{0, \dots, 9\}$.
   $$\text{Sign}_{D10} = \begin{cases} (S + k) \pmod{12} & \text{if } \text{IsOdd} \\ (S + 8 + k) \pmod{12} & \text{if even} \end{cases}$$

8. **D12: Dwadasamsa (Parents, Ancestors & Past Karma - 2°30' twelfths)**
   - Segment index: $k = \lfloor D / 2.5^\circ \rfloor \in \{0, \dots, 11\}$.
   $$\text{Sign}_{D12} = (S + k) \pmod{12}$$

9. **D16: Shodasamsa / Kalamsa (Vehicles, Luxuries & Happiness - 1°52'30" sixteenths)**
   - Segment index: $k = \lfloor D / 1.875^\circ \rfloor \in \{0, \dots, 15\}$.
   $$\text{StartSign} = \begin{cases} 0 \ (\text{Aries}) & \text{if Movable} \\ 4 \ (\text{Leo}) & \text{if Fixed} \\ 8 \ (\text{Sagittarius}) & \text{if Dual} \end{cases}$$
   $$\text{Sign}_{D16} = (\text{StartSign} + k) \pmod{12}$$

10. **D20: Vimsamsa (Spiritual Progress, Meditation & Devotion - 1°30' twentieths)**
    - Segment index: $k = \lfloor D / 1.5^\circ \rfloor \in \{0, \dots, 19\}$.
    $$\text{StartSign} = \begin{cases} 0 \ (\text{Aries}) & \text{if Movable} \\ 8 \ (\text{Sagittarius}) & \text{if Fixed} \\ 4 \ (\text{Leo}) & \text{if Dual} \end{cases}$$
    $$\text{Sign}_{D20} = (\text{StartSign} + k) \pmod{12}$$

11. **D24: Chaturvimsamsa / Siddhamsa (Higher Learning, Knowledge & Skills - 1°15' twenty-fourths)**
    - Segment index: $k = \lfloor D / 1.25^\circ \rfloor \in \{0, \dots, 23\}$.
    $$\text{StartSign} = \begin{cases} 4 \ (\text{Leo}) & \text{if } \text{IsOdd} \\ 3 \ (\text{Cancer}) & \text{if even} \end{cases}$$
    $$\text{Sign}_{D24} = (\text{StartSign} + k) \pmod{12}$$

12. **D27: Saptavimsamsa / Bhamsa (Subconscious Strengths & Vulnerabilities - 1°06'40" twenty-sevenths)**
    - Segment index: $k = \lfloor D / (30^\circ / 27) \rfloor \in \{0, \dots, 26\}$.
    $$\text{StartSign} = [0, 3, 6, 9][S \pmod 4]$$
    $$\text{Sign}_{D27} = (\text{StartSign} + k) \pmod{12}$$

13. **D30: Trimsamsa (Misfortunes, Evils & Health Afflictions - Unequal Portions)**
    - **In Odd Signs**:
      - $0^\circ \le D < 5^\circ$: Mars $\to$ Aries ($S=0$)
      - $5^\circ \le D < 10^\circ$: Saturn $\to$ Aquarius ($S=10$)
      - $10^\circ \le D < 18^\circ$: Jupiter $\to$ Sagittarius ($S=8$)
      - $18^\circ \le D < 25^\circ$: Mercury $\to$ Gemini ($S=2$)
      - $25^\circ \le D < 30^\circ$: Venus $\to$ Taurus ($S=1$)
    - **In Even Signs**:
      - $0^\circ \le D < 5^\circ$: Venus $\to$ Taurus ($S=1$)
      - $5^\circ \le D < 12^\circ$: Mercury $\to$ Virgo ($S=5$)
      - $12^\circ \le D < 20^\circ$: Jupiter $\to$ Pisces ($S=11$)
      - $20^\circ \le D < 25^\circ$: Saturn $\to$ Capricorn ($S=9$)
      - $25^\circ \le D < 30^\circ$: Mars $\to$ Scorpio ($S=7$)

14. **D40: Khavedamsa / Swavedamsa (Maternal Lineage & Auspicious Auspices - 45' fortieths)**
    - Segment index: $k = \lfloor D / 0.75^\circ \rfloor \in \{0, \dots, 39\}$.
    $$\text{StartSign} = \begin{cases} 0 \ (\text{Aries}) & \text{if } \text{IsOdd} \\ 6 \ (\text{Libra}) & \text{if even} \end{cases}$$
    $$\text{Sign}_{D40} = (\text{StartSign} + k) \pmod{12}$$

15. **D45: Akshavedamsa (All General Indications & Moral Purity - 40' forty-fifths)**
    - Segment index: $k = \lfloor D / (30^\circ / 45) \rfloor \in \{0, \dots, 44\}$.
    $$\text{StartSign} = \begin{cases} 0 \ (\text{Aries}) & \text{if Movable} \\ 4 \ (\text{Leo}) & \text{if Fixed} \\ 8 \ (\text{Sagittarius}) & \text{if Dual} \end{cases}$$
    $$\text{Sign}_{D45} = (\text{StartSign} + k) \pmod{12}$$

16. **D60: Shastiamsa (Past Life Karma & Micro-Destiny - 30' sixtieths)**
    - Segment index: $k = \lfloor D / 0.5^\circ \rfloor \in \{0, \dots, 59\}$.
    $$\text{Sign}_{D60} = (S + k) \pmod{12}$$

---

## 4. House Systems & Bhava Chalit

1. **Sripati (Porphyry-Vedic Hybrid)**:
   - Evaluates the Midheaven ($MC$) and Ascendant ($Asc$).
   - Calculates the four quadrant arcs and divides each quadrant into three equal parts.
   - House cusps represent the *midpoints* (Madhya) of the Bhavas, with Sandhis (junction points) halfway between adjacent cusps.
2. **Placidus (Semi-Arc Time Proportionate)**:
   - House cusps determined by the intersection of the ecliptic with diurnal and nocturnal semi-arcs.
3. **Equal House System**:
   - 1st house cusp begins at Ascendant degree. Each house spans exactly 30° from $Asc + 30^\circ \times (h - 1)$.
4. **Whole Sign (Vedic Rashi-Chakra Default)**:
   - The entire zodiac sign containing the Ascendant is House 1. House $h$ is $(S_{\text{Asc}} + h - 1) \pmod{12}$.

---

## 5. Planetary Strengths (Shadbala & Ashtakavarga)

### 5.1 Sixfold Strength (Shadbala)
1. **Sthana Bala (Positional Strength)**:
   - Uccha Bala (Exaltation strength): Distance from deep debilitation point.
   - Saptavargaja Bala: Dignity across 7 principal divisional charts.
   - Ojhayugmarashi Bala: Placement in odd vs even signs for male/female planets.
   - Kendra Bala: Strength in Angles (60 virupas), Succedent (30), Cadent (15).
   - Drekkana Bala: Division ruler strength.
2. **Dig Bala (Directional Strength)**:
   - Jupiter/Mercury strongest in 1st house (East).
   - Sun/Mars strongest in 10th house (South).
   - Saturn strongest in 7th house (West).
   - Moon/Venus strongest in 4th house (North).
3. **Kala Bala (Temporal Strength)**:
   - Natonnata Bala (Day/Night strength).
   - Paksha Bala (Fortnight strength for Moon and benefics).
   - Tribhaga Bala (Three parts of day and night).
   - Varsha/Masa/Dina/Hora Patis (Lord of Year, Month, Day, Hour).
   - Ayana Bala (Equinoctial declination strength).
   - Yuddha Bala (Planetary war adjustment).
4. **Chesta Bala (Motional Strength)**:
   - Direct fast, direct normal, slow, stationary, retrograde speed evaluations.
5. **Naisargika Bala (Natural Inherent Strength)**:
   - Fixed values in Virupas: Sun (60.0), Moon (51.43), Venus (42.86), Jupiter (34.29), Mercury (25.71), Mars (17.14), Saturn (8.57).
6. **Drik Bala (Aspect Strength)**:
   - Sum of benefic aspects minus malefic aspects on each planet.

### 5.2 Ashtakavarga Reductions
1. **Prastarashtakavarga**: 8x12 individual benefic bindu distribution for each planet and Lagna.
2. **Bhinnashtakavarga**: Combined score (0 to 8 bindus per sign) for each planet.
3. **Sarvashtakavarga (SAV)**: Sum of all 7 planetary bindus per sign (total = 337 bindus across 12 signs; average = 28 bindus).
4. **Trikona Shodhana (Triad Reduction)**:
   - Compares trines: (Aries, Leo, Sagittarius), (Taurus, Virgo, Capricorn), (Gemini, Libra, Aquarius), (Cancer, Scorpio, Pisces).
   - If values are unequal, the minimum is subtracted from all three; if one is zero, specific retention rules apply.
5. **Ekadhipatya Shodhana (Dual Ownership Reduction)**:
   - Evaluates signs ruled by the same planet (Mars, Mercury, Jupiter, Venus, Saturn) when not occupied by planets.
