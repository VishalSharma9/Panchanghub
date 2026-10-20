# Planetary Period & Dasha Systems Architecture

## 1. Classical Dasha Framework

Vedic astrology uses timing systems called *Dashas* (planetary operating periods) to forecast when the natal promises of planets and houses will manifest.

---

## 2. Vimshottari Dasha (120-Year Cycle)

Vimshottari is the primary universal dasha system expounded by Maharishi Parashara for the Kali Yuga.

### 2.1 Planetary Years and Sequence
The 120-year cycle follows an invariable ninefold planetary sequence mapped to the 27 Nakshatras:

| Order | Planetary Ruler | Span in Years | Nakshatras Ruled |
|---|---|---|---|
| 1 | **Ketu** | 7 | Ashwini (1), Magha (10), Mula (19) |
| 2 | **Venus (Shukra)** | 20 | Bharani (2), Purva Phalguni (11), Purva Ashadha (20) |
| 3 | **Sun (Surya)** | 6 | Krittika (3), Uttara Phalguni (12), Uttara Ashadha (21) |
| 4 | **Moon (Chandra)** | 10 | Rohini (4), Hasta (13), Shravana (22) |
| 5 | **Mars (Mangala)** | 7 | Mrigashira (5), Chitra (14), Dhanishta (23) |
| 6 | **Rahu** | 18 | Ardra (6), Swati (15), Shatabhisha (24) |
| 7 | **Jupiter (Guru)** | 16 | Punarvasu (7), Vishakha (16), Purva Bhadrapada (25) |
| 8 | **Saturn (Shani)** | 19 | Pushya (8), Anuradha (17), Uttara Bhadrapada (26) |
| 9 | **Mercury (Budha)** | 17 | Ashlesha (9), Jyeshtha (18), Revati (27) |
| **Total** | | **120 Years** | |

### 2.2 Mathematical Balance of Dasha at Birth
Let $\lambda_{\text{Moon}}$ be the sidereal longitude of the Moon in degrees ($0^\circ \le \lambda_{\text{Moon}} < 360^\circ$):
1. **Nakshatra Index**:
   $$N = \lfloor \lambda_{\text{Moon}} / 13.333333^\circ \rfloor \in \{0, \dots, 26\}$$
2. **Elapsed Fraction within Nakshatra**:
   $$f = \frac{\lambda_{\text{Moon}} - N \times 13.333333^\circ}{13.333333^\circ} \quad (0 \le f < 1)$$
3. **Birth Ruler**: $R_0 = \text{VimshottariSequence}[N \pmod 9]$
4. **Balance Remaining at Birth**:
   $$\text{BalanceYears} = (1.0 - f) \times \text{RulerYears}[R_0]$$
5. **Birth Dasha Start Date**:
   $$JD_{\text{start}} = JD_{\text{birth}} - (f \times \text{RulerYears}[R_0] \times 365.2425)$$

### 2.3 Hierarchical Sub-Period Decompositions
The Vimshottari cycle decomposes into 5 levels of precision:
1. **Mahadasha (Major Period)**: $Y_{\text{maha}} = \text{VIM\_YEARS}[R_1]$
2. **Antardasha (Sub-Period)**:
   $$Y_{\text{antar}} = Y_{\text{maha}} \times \frac{\text{VIM\_YEARS}[R_2]}{120}$$
3. **Pratyantardasha (Sub-Sub-Period)**:
   $$Y_{\text{prat}} = Y_{\text{antar}} \times \frac{\text{VIM\_YEARS}[R_3]}{120}$$
4. **Sookshmadasha (Sub-Sub-Sub-Period)**:
   $$Y_{\text{sook}} = Y_{\text{prat}} \times \frac{\text{VIM\_YEARS}[R_4]}{120}$$
5. **Pranadasha (Life Breath Moment)**:
   $$Y_{\text{prana}} = Y_{\text{sook}} \times \frac{\text{VIM\_YEARS}[R_5]}{120}$$

---

## 3. Yogini Dasha (36-Year Cycle)

Yogini Dasha is an 8-fold period system especially effective for transit cross-verification and health predictions.

### 3.1 Planetary Rulers and Period Durations
The 36-year cycle is governed by 8 Yoginis:
$$\sum_{i=1}^8 i = 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 = 36 \text{ Years}$$

| Index | Yogini Name | Associated Planet | Nature / Effect | Period Duration |
|---|---|---|---|---|
| 1 | **Mangala** | Moon (Chandra) | Benefic / Auspicious | 1 Year |
| 2 | **Pingala** | Sun (Surya) | Malefic / Agitation | 2 Years |
| 3 | **Dhanya** | Jupiter (Guru) | Benefic / Wealth & Prosperity | 3 Years |
| 4 | **Bhramari** | Mars (Mangala) | Malefic / Travel & Displacement | 4 Years |
| 5 | **Bhadrika** | Mercury (Budha) | Benefic / Learning & Career | 5 Years |
| 6 | **Ulka** | Saturn (Shani) | Malefic / Obstacles & Delays | 6 Years |
| 7 | **Siddha** | Venus (Shukra) | Benefic / Fulfillment & Comforts | 7 Years |
| 8 | **Sankata** | Rahu | Malefic / Turmoil & Karmic Debt | 8 Years |

### 3.2 Calculation Algorithm
1. Compute Moon's Nakshatra index $N \in \{1, \dots, 27\}$ (1-indexed: Ashwini = 1).
2. Add offset 3:
   $$Y_{\text{idx}} = ((N + 3 - 1) \pmod 8) + 1 \in \{1, \dots, 8\}$$
3. Elapsed fraction $f$ within the Nakshatra determines the balance of the initial Yogini period.
4. Each Major Yogini period divides into 8 Antar-Yoginis proportionally:
   $$Y_{\text{sub}} = Y_{\text{major}} \times \frac{\text{YoginiYears}[\text{sub}]}{36}$$

---

## 4. Jaimini Chara Dasha

Chara Dasha is a sign-based dasha system from Maharishi Jaimini's *Upadesha Sutras*.

### 4.1 Direction of Reckoning (Footedness)
1. **Savya (Forward Counting)**: Aries, Taurus, Gemini, Libra, Scorpio, Sagittarius.
2. **Apasavya (Reverse Counting)**: Cancer, Leo, Virgo, Capricorn, Aquarius, Pisces.
3. The starting sign is the Ascendant (Lagna). The direction of the 9th house from Lagna determines the primary direction of progression.

### 4.2 Sign Period Durations
The duration of each sign (1 to 12 years) is determined by the distance of the sign lord from the sign:
- If sign is direct: count from sign to its lord forward.
- If sign is indirect: count from sign to its lord backward.
- Deduct 1 year; if distance is 0, duration is 12 years.
- Add 1 year if lord is exalted; subtract 1 year if debilitated.

---

## 5. Kalachakra Dasha

Considered the most intricate dasha system in Jyotish, based on the wheel of time (*Kala Chakra*):
- Divides the 27 Nakshatras into **Savya** (clockwise) and **Apasavya** (counter-clockwise) groups.
- Each Nakshatra Pada (quarter) has a specific non-linear sequence of zodiac signs spanning 83 to 100 years.
- Features *Gatis* (special leaps):
  - **Manduki Gati** (Frog leap across signs).
  - **Markati Gati** (Monkey leap backward).
  - **Simhavalokana** (Lion's backward glance).
- Identifies **Deha** (body) and **Jeeva** (soul) signs; afflictions to these signs during their operative sub-periods indicate severe bodily or spiritual crises.

---

## 6. Classical Conditional Nakshatra Dashas

| Dasha System | Span | Primary Applicability Condition |
|---|---|---|
| **Ashtottari** | 108 Years | Applicable when Rahu is placed in a Kendra or Trikona from the Lagna Lord, especially in Shukla Paksha day birth or Krishna Paksha night birth. |
| **Shodashottari** | 116 Years | Applicable when Lagna falls in Moon's hora in Krishna Paksha or Sun's hora in Shukla Paksha. |
| **Dwadashottari** | 112 Years | Applicable when Lagna is posited in a Navamsa ruled by Venus. |
| **Panchottari** | 105 Years | Applicable when Lagna is Cancer and in Cancer Dwadasamsa. |
| **Shatabdika** | 100 Years | Applicable when Lagna is Vargottama (same sign in D1 and D9). |
| **Chaturashiti-sama** | 84 Years | Applicable when the 10th lord is posited in the 10th house. |
| **Dwisaptati-sama** | 72 Years | Applicable when the Lagna lord is in the 7th house or the 7th lord is in Lagna. |
| **Shashtihayani** | 60 Years | Applicable when the Sun is placed in the Ascendant (Lagna). |
| **Shattrimsha-sama** | 36 Years | Applicable for day birth with Lagna in Sun's hora or night birth in Moon's hora. |
