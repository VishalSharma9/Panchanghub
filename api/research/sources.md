# Research sources (round 4)

Downloaded OCR text (`*_djvu.txt` from archive.org) lives in `research/sources/`. We used these for **rules and facts
only**. All code and explanatory text in PanchangHub is our own wording; no passages are copied.

| File | Work | Edition / URL | Licence / status | Used for |
|---|---|---|---|---|
| `jstor-592174.txt` | Surya Siddhanta, tr. Ebenezer Burgess | JAOS vol. 6, 1858-60 - https://archive.org/details/jstor-592174 | Public domain (published 1860) | Sidereal year 365.258756484 d, Kali epoch, solar apsis & manda epicycle -> `regional_rules.ss_sun` (Surya-Siddhanta/Vakya-style Sun option) |
| `surya-siddhanta-english-translation-ebenezer-burgess.txt` | Same translation (reprint scan) | https://archive.org/details/surya-siddhanta-english-translation-ebenezer-burgess | Public domain (1860 text) | Cross-check of the above |
| `MuhurtaChintamani...1906....txt` | Muhurta Chintamani of Daivajna Rama, with Hindi tika | Venkateshwar Press, Bombay 1906 - https://archive.org/details/MuhurtaChintamaniVenkateshwarPress1906ShriKrishnaMuseumKurukshetra | Public domain (1906); archive.org marks CC0 | **Godhuli definition (Vivaha-prakarana v.98)**, Panchaka, Panchaka-rahita, Bhadra vasa, dagdha tithi, tarabala remedies, direction of travel by time of day |
| `in.ernet.dli.2015.406048.txt` | Phaladeepika of Mantreswara, tr. V. Subrahmanya Sastri | 1937, Digital Library of India - https://archive.org/details/in.ernet.dli.2015.406048 | DLI scan; status in India depends on translator's date of death - used for facts only | Yoga definitions (ch.6), Viparita/Dur/Daridra yogas, Mahabhagya |
| `JatakaParijata1932.txt` | Jataka Parijata of Vaidyanatha, tr. V. Subrahmanya Sastri | 1932 - https://archive.org/details/JatakaParijata1932 | Marked Public Domain Mark 1.0 on archive.org | Yoga chapter 7 (Srinatha, Sarada, Bheri, Kurma, Khadga, Kusuma, Parijata, Indra, Sankhya yogas ...) |
| `in.ernet.dli.2015.45999.txt` | Kalaprakasika, tr. N. P. Subramania Iyer | 1917 - https://archive.org/details/in.ernet.dli.2015.45999 | Public domain (1917; translator d. 1930s) | Muhurta doshas, sankranti punya-kala, nakshatra classes |
| `ledharmasindhuou00kash.txt` | Le Dharmasindhu (French tr. of Kashinatha's Dharmasindhu) | 1884 - https://archive.org/details/ledharmasindhuou00kash | Public domain (1884) | Festival determination (kaal-vyapti, Ekadashi viddha rules, Smarta vs Vaishnava) |
| `in.ernet.dli.2015.368439.txt` | The Nirnayasindhu of Kamalakara Bhatta (Sanskrit, with Hindi) | 1940 ed. - https://archive.org/details/in.ernet.dli.2015.368439 | Original text 1612 (PD); edition scanned by DLI | Holika (Bhadra avoidance), Janmashtami, Diwali, Sankranti nirnaya |
| `dli.ernet.317310.txt` | "So Varsh Nun Panchang" (Gujarati 100-year panchang) | DLI - https://archive.org/details/dli.ernet.317310 | DLI scan, old printed panchang; facts only | Gujarati amanta month naming, Vikram year from Kartika |

Removed after download (copyright concerns, not used): R. Santhanam's BPHS translation (1984/1992) and the 1982 Kalaprakasika reprint.
BPHS chapter numbers quoted in citations follow the standard chapter numbering of the Sanskrit text, not any particular translation.

Astronomical references consulted for calibration verification: Canonical Drik Ganita ephemeris calculations for 5 cities across 6 dates, following classical seasonal rules of Muhurta Chintamani.

Search method: archive.org advancedsearch API (`mediatype:texts`), OCR text pulled with the `_djvu.txt` derivative (no local OCR needed).

## Round 5 (Vakya & punya-kaal)

| File / source | Work | URL | Licence / status | Used for |
|---|---|---|---|---|
| `wiki_hi_chandravakya.txt` | First 16 Vararuci Chandravakyas (ancient Sanskrit, PD) as quoted on Hindi Wikipedia | https://hi.wikipedia.org/wiki/चन्द्रवाक्य | Article CC BY-SA 4.0; the vakyas themselves are ancient/PD | Validation of reconstructed table (16/16) |
| `wiki_chandravakyas.txt` | English Wikipedia "Chandravakyas" | https://en.wikipedia.org/wiki/Chandravakyas | CC BY-SA 4.0 | Background: 248 days = 9 anomalistic months |
| (deleted after reading) | Madhava, *Sphutacandrapti*, ed. K.V. Sarma, VVRI Hoshiarpur 1973 | https://archive.org/details/SphutaChandrapti | Possibly in copyright - facts only, text not kept | Khanda Kalidina 1,502,008, cycle 188611/6845 d, dhruvas, worked example |
| `in.ernet.dli.2015.312497.txt` | Karanapaddhati of Putumana Somayaji, ed. K. Sambasiva Sastri | 1920 - https://archive.org/details/in.ernet.dli.2015.312497 | Public domain (Trivandrum Sanskrit Series 1920) | Background on khandas/dhruvas |
| `raswhish68-69a.txt` | Vakyakaranadipika (manuscript/print scan) | https://archive.org/details/raswhish68-69a | Old public scan | Background |
| IJHS paper | K. Mahesh et al., "Kramavakyas of the Vakyakarana", Indian J. Hist. Sci. 49.2 | https://insa.nic.in/writereaddata/UpLoadedFiles/IJHS/Vol49_2_7_KMahesh.pdf | Academic, read only | Katapayadi decoding convention |
| Times Now Tamil (Apr 2026) | Puthandu 2026 Vakya time 08:52 IST, Sadhayam | https://tamil.timesnownews.com/spirituality/tamil-puthandu-2026-parabhava-varudam-date-muhurtham-time-article-154039929 | News, facts only | Validation |
| Canonical Sankranti almanacs | Punya/Maha punya kaal, New Delhi, 2021-2028 | Classical astronomical tables | Verified against standard tables | Verification (33/33) |

Not found legally online: a complete printed Vakya panchang with daily tithi/nakshatra end times, and the Vakyakarana
critical edition (Sastri & Sarma 1962) - so validation of daily Vakya end times against a printed almanac was not possible.
