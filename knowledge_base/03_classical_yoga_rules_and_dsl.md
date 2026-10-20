# Astrological Combinations (Yogas) & Rule Evaluation Grammar

## 1. Domain-Specific Language (DSL) Specification

To evaluate thousands of classical astrological combinations deterministically against any birth chart, an expressive rule grammar is formalized:

### 1.1 Lexical Tokens
- **Planets (`Graha`)**:
  - `Su` / `1` : Sun (Surya)
  - `Mo` / `2` : Moon (Chandra)
  - `Ma` / `3` : Mars (Mangala)
  - `Me` / `4` : Mercury (Budha)
  - `Ju` / `5` : Jupiter (Guru)
  - `Ve` / `6` : Venus (Shukra)
  - `Sa` / `7` : Saturn (Shani)
  - `Ra` / `8` : Rahu (North Node)
  - `Ke` / `9` : Ketu (South Node)
  - `La` : Ascendant (Lagna)
- **Houses (`Bhava`)**:
  - `H1` to `H12` : Houses 1 through 12.
  - `L1` to `L12` : Lords of Houses 1 through 12.
  - `Kendra` : Houses {1, 4, 7, 10}.
  - `Trikona` : Houses {1, 5, 9}.
  - `Dusthana` / `Trika` : Houses {6, 8, 12}.
  - `Upachaya` : Houses {3, 6, 10, 11}.
- **Signs (`Rashi`)**:
  - `IR1` to `IR12` : In Sign 1 (Aries) through 12 (Pisces).
- **Dignities & States (`Avastha`)**:
  - `O` : Own Sign (Swakshetra).
  - `E` : Exalted (Uchcha).
  - `D` : Debilitated (Neecha).
  - `M` : Moolatrikona.
  - `F` : Friendly Sign (Mitra).
  - `En` : Inimical Sign (Shatru).
- **Connectors & Operators**:
  - `*` : Logical AND (conjunction of conditions).
  - `+` : Logical OR (alternative conditions).
  - `Y` : Yuti (Conjunction in same sign) — e.g., `Ju Y Mo` (Gaja Kesari).
  - `D` : Drishti (Aspect) — e.g., `Sa D Ma` (Saturn aspects Mars).
  - `I` : In House — e.g., `L1 I 10` (Ascendant lord in 10th house).
  - `@sun`, `@mon`, ..., `@sat` : Day of birth (Vara).
  - `@bD` : Day birth (Sunrise to Sunset).
  - `@bN` : Night birth (Sunset to Sunrise).
  - `@SB(P > V)` : Shadbala Virupas threshold.

---

## 2. Major Classical Yoga Categories

### 2.1 Pancha Mahapurusha Yogas (Five Great Person Yogas)
Formed when non-luminaries occupy their own or exaltation sign in a Kendra (houses 1, 4, 7, 10) from Lagna:

1. **Ruchaka Yoga (Mars)**:
   - *Condition*: Mars in Aries, Scorpio, or Capricorn in a Kendra.
   - *Effects*: Fearless, commanding leadership, military or athletic distinction, victor in battles, energetic constitution.
2. **Bhadra Yoga (Mercury)**:
   - *Condition*: Mercury in Gemini or Virgo in a Kendra.
   - *Effects*: Sharp analytical intellect, eloquence in speech, literary and scholarly excellence, longevity, diplomatic acumen.
3. **Hamsa Yoga (Jupiter)**:
   - *Condition*: Jupiter in Sagittarius, Pisces, or Cancer in a Kendra.
   - *Effects*: Virtuous character, spiritual wisdom, respected by leaders, righteous wealth, high moral authority.
4. **Malavya Yoga (Venus)**:
   - *Condition*: Venus in Taurus, Libra, or Pisces in a Kendra.
   - *Effects*: Aesthetic beauty, artistic mastery, wealth, marital happiness, luxurious vehicles and sensory pleasures.
5. **Sasa Yoga (Saturn)**:
   - *Condition*: Saturn in Capricorn, Aquarius, or Libra in a Kendra.
   - *Effects*: Authority over assemblies, organizational stamina, enduring power, mass appeal, disciplined longevity.

---

### 2.2 Principal Raja Yogas (Royal Combinations of Power & Authority)
1. **Dharma-Karmadhipati Yoga**:
   - *Condition*: Conjunction, mutual aspect, or exchange of signs between the 9th lord (Dharma) and 10th lord (Karma).
   - *Effects*: Highest career prominence, ethical leadership, lasting legacy and government or corporate power.
2. **Kendra-Trikona Sambandha**:
   - *Condition*: Association between any Kendra lord (1, 4, 7, 10) and any Trikona lord (1, 5, 9).
   - *Effects*: Success with minimal friction, fortunate advancements, broad public support.
3. **Gaja Kesari Yoga**:
   - *Condition*: Jupiter in a Kendra (1, 4, 7, 10) from the Moon, free from deep combustion.
   - *Effects*: Inviolable reputation, intellectual fortitude, wealth, protection from hidden adversaries.
4. **Neechabhanga Raja Yoga (Cancellation of Debilitation)**:
   - Formed through one of four classical cancellations:
     1. Lord of debilitation sign is in a Kendra from Lagna or Moon.
     2. Exaltation lord of the debilitated sign is in a Kendra from Lagna or Moon.
     3. Planet that gets exalted in the sign occupied by the debilitated planet is in a Kendra.
     4. Debilitated planet aspects its own sign or is conjunct an exalted planet.
   - *Effects*: Initial hardship followed by extraordinary rise to eminence and triumph over limitations.
5. **Viparita Raja Yoga (Inverted Royal Combinations)**:
   - **Harsha Yoga**: 6th lord in 6th, 8th, or 12th house. Victory over diseases and competitors.
   - **Sarala Yoga**: 8th lord in 6th, 8th, or 12th house. Longevity, scholarly depth, fearlessness.
   - **Vimala Yoga**: 12th lord in 6th, 8th, or 12th house. Spiritual independence, noble spending, autonomy.

---

### 2.3 Dhana Yogas (Wealth Combinations)
1. **Lakshmi Yoga**: 9th lord and Venus in exaltation or own house in Kendras/Trikonas.
2. **Kalanidhi Yoga**: Jupiter in the 2nd or 5th house conjunct or aspected by Mercury and Venus.
3. **Vasumati Yoga**: Benefics (Jupiter, Venus, Mercury) in Upachaya houses (3, 6, 10, 11) from Lagna or Moon.
4. **Dhana Bhavadhipati Sambandha**: Interconnection between the 2nd lord (accumulated wealth) and 11th lord (gains).
5. **Chandra-Mangala Yoga**: Conjunction of Moon and Mars. Financial enterprise, business accumulative instincts.

---

### 2.4 Solar & Lunar Auxiliary Yogas
1. **Sunapha Yoga**: Planets (other than Sun, Rahu, Ketu) in 2nd from Moon. Self-made fortune.
2. **Anapha Yoga**: Planets in 12th from Moon. Generosity, polished manners, stable health.
3. **Durdhura Yoga**: Planets in both 2nd and 12th from Moon. High balance of prosperity, virtue, and vehicular comforts.
4. **Kemadruma Yoga**: No planets in 2nd or 12th from Moon (cancelled if Kendra from Lagna/Moon has planets).
5. **Budhaditya Yoga**: Sun conjunct Mercury. Quick intellect, administrative capability, analytical skill.
6. **Amala Yoga**: Tenth house from Lagna or Moon occupied exclusively by natural benefics. Stainless reputation.
7. **Parvata Yoga**: Benefics in Kendras and 6th/8th houses free of planets or occupied only by benefics.
8. **Kahala Yoga**: Lords of 4th and 9th in mutual Kendras with Lagna lord strong. Dynamic drive.
9. **Shankha Yoga**: 5th and 6th lords in mutual Kendras with strong Lagna lord. Philanthropic nature.
10. **Chhatra Yoga**: All planets positioned continuously from 7th to 12th houses. Protective umbrella of fortune.
