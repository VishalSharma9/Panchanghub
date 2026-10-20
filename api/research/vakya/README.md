# Vakya reconstruction notes

* `decode.py` decodes the first 16 Vararuci Chandravakyas (Sanskrit sentences, public domain; text as quoted on
  hi.wikipedia "चन्द्रवाक्य", CC BY-SA) with the katapayadi rule (right-to-left; 2 digits minutes, 2 digits degrees, rest signs).
* Model: true Moon after i days from zero anomaly = m*i - asin(k*sin(n*i)), n = 9*360/248 deg/day,
  m = (9*360 + 27°44'06")/248. Best fit to the 16 decoded vakyas: k = 0.0874 (≈ 31.5/360, i.e. max equation 5°01'),
  start anomaly 0 -> max residual 0.6' (pure rounding). `chandravakyas_reconstructed.csv` holds all 248.
* Epoch/cycle facts (Madhava, Sphutacandrapti, ed. K.V. Sarma 1973 - consulted for facts only; the scan text was deleted
  afterwards because the edition may still be in copyright): zero-anomaly at sunrise ending Kalidina 1,502,008; cycle
  188611/6845 d; 3°04'06.96" per cycle (7s1°44' per 69 cycles); worked example 12,502 cycles -> 6s13°12'37",
  giving Moon at epoch 349°35'07"; check: 5105-cycle lump -> 5s24°47' (reproduced to 0.4").
* Vakya Sun: Aryabhatiya constants (4,320,000 revs / 1,577,917,500 days, apogee 78°, epicycle 13.5°).

## Validation
* 16/16 decoded vakyas reproduced (≤0.6').
* Tamil New Year 2026 (Parabhava): published Vakya time 08:52 IST, Moon in Sadhayam (Times Now Tamil, Apr 2026) -
  ours 09:01 IST, Moon in Shatabhisha (Sadhayam). 9 min difference.
* Thai 1 / Pongal 2026: Vakya Makara sankranti 18:31 IST Jan 14 (after sunset) -> Thai 1 = Jan 15, matching the
  Tamil Nadu Pongal holiday (Jan 15) while Drik/Thirukanitha gives Jan 14.
* Against modern (Drik) 2026, Chennai: Vakya tithi ends mean +86 min, median |Δ| 111 min, max 7 h; nakshatra similar.
  Residual analysis vs Swiss Ephemeris shows exactly the terms the Vakya Moon omits: evection 1.27°, variation 0.66°,
  annual equation 0.19°, plus ~1° epoch drift - i.e. the expected behaviour of a genuine Vakya almanac.
