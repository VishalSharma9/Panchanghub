# Website pages

Each page is a Jinja template in this folder (`website/templates/`). The Python that fills it is `api/app/web/__init__.py`. That Python calls the API functions. It does not redo the astronomy.

Shared chrome is `base.html`: sticky header, live clock, language menu, location search, nav, sidebar. `style.css` and `app.js` are in `website/static/`.

| URL | Template | Filled by | What the person sees |
|---|---|---|---|
| `/` | `home.html` | `RP.panchang`, `RP.choghadiya`, `RC.festivals` | Today. Sunrise strip, Vedic clock (ghati, pala, vipala), panchang glance, day choghadiya, upcoming festivals. |
| `/panchang` | `panchang.html` | `RP.panchang`, `RX.regional` | The full day. Five limbs with end times, both months, samvat, regional solar dates, gate, ghati lengths, muhurtas, Anandadi, Tamil yoga, Disha Shool and the open directions, Homahuti, Agnivasa, Chandra vasa, Shivavasa, Chandrabala, Tarabala, Pancha Pakshi, do-ghati, Mantri Mandala. |
| `/mine` | `mine.html` | panchang, choghadiya, `for_you()` | Personal day for the birth star cookie. Next puja hour, travel hour, money hour. No score. |
| `/week` | `week.html` | seven panchangs | One row a day. Slow on purpose. Do not call it from the home page. |
| `/compare` | `compare.html` | panchang twice | Same civil date, two places. Shows when the sunrise tithi differs. |
| `/names` | `names.html` | `syllable`, `moon_syllable` | Namakarana sound from the Moon’s nakshatra pada. The family still chooses the name. |
| `/sade-sati` | `sade.html` | `kundli.sade_sati` | Saturn in the 12th, 1st, and 2nd from the natal Moon, plus Panoti in the 4th and 8th. |
| `/calendar` | `calendar.html` | `RC.month` | Month grid of the tithi at sunrise. |
| `/choghadiya` | `choghadiya.html` | `RP.choghadiya` | Day and night, eight slots each. |
| `/hora` | `hora.html` | `RP.hora` | Twenty-four planetary hours. |
| `/rahu-kaal` | `rahu.html` | `RP.rahu_kaal` | Rahu table across a span of up to 10 years. |
| `/lagna-table` | `lagna.html` | `RP.lagna`, `RP.gowri` | Lagna changes and Gowri nalla neram. |
| `/festivals` | `festivals.html` | `RC.festivals` | Year list. Filters include ekadashi, purnima, amavasya, sankranti, pradosh, eclipse. |
| `/festivals.ics` | none | `RC.festivals` | Download. Not a template. |
| `/kundli` | `kundli.html` | `RV.kundli` | North, South, or East chart, vargas, dashas, doshas, yogas. PDF is `POST /api/kundli/pdf`. |
| `/matching` | `matching.html` | `RV.matching` | Ashtakoota out of 36 and the 10 poruthams. |
| `/muhurat` | `muhurat.html` | `RC.muhurat` | Marriage, griha pravesh, vehicle, property, naming, mundan, annaprashan, business. |
| `/transits` | `transits.html` | `RC.transits`, planets, moon phases | Sidereal ingresses and stations, plus the planets now. |
| `/western` | `western.html` | `RCore.chart` | Tropical chart. House system query `hs`. |
| `/horoscope` | `horoscope.html` | `RX.horoscope` | Rashifal by period and sign. Template text, not a personal reading. |
| `/numerology` | `numerology.html` | `RX.numerology` | Name and date. |
| `/tarot` | `tarot.html` | `RX.tarot_daily` | Daily draw. |
| `/human-design` | `humandesign.html` | Human Design chart | Type, authority, profile, centers. |
| `/vastu` | `vastu.html` | Vastu guide | Directions and a layout score from the rooms you enter. |
| `/iching` | `iching.html` | I Ching cast | Three-coin hexagram. |
| `/palmistry` | `palmistry.html` | Palmistry reference | A reading from described features. Not a photo reader. |
| `/tools` | `tools.html` | several small routers | Mayan, Chinese year, Kabbalah, dreams, crystals. |
| `/regional` | `regional.html` | regional and vakya routers | Tamil, Malayalam, Bengali, Assamese, Odia, Gujarati, Marathi, Vakya beside Drik, punya kaal. |
| `/widget/panchang` | `widget.html` | `RP.panchang` | Embeddable fragment. `static/embed.js` is the snippet. |

Partials, not pages: `_macros.html` (date bar, birth form), `_place.html` (one column of compare), `error.html`.
