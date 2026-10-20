# Global Atlas & Geolocation Systems Architecture

## 1. High-Performance Geolocation Storage & Indexing

Vedic astrology computations require exact local geographic coordinates (latitude, longitude, and elevation) and precise historical local time zone offsets for birth moment calculations.

---

## 2. 24-Byte Compact Record Architecture

For embedded systems and zero-overhead memory footprints, city databases are packed into fixed 24-byte binary records:

```c
#pragma pack(push, 1)
typedef struct {
    char     city_name[14];     // Null-terminated ASCII/Latin-1 string (padded with 0x00/0xCC)
    int16_t  latitude;          // Degrees * 100 + Minutes (Positive = North, Negative = South)
    int16_t  longitude;         // Degrees * 100 + Minutes (Positive = East, Negative = West)
    uint16_t state_index;       // Pointer into administrative division/state table
    uint16_t timezone_index;    // Pointer into Time Zone / DST rules table
    uint16_t county_code;       // Location/district administrative identifier
} CityRecord; // sizeof = 24 bytes
#pragma pack(pop)
```

### 2.1 Disk-Based Binary Search $O(\log N)$
- By sorting the binary file alphabetically by `[CountryCode, CityName]`, binary searches can be performed directly against disk storage without loading millions of records into memory:
  ```python
  def find_city_on_disk(file_handle, start_record, end_record, target_name):
      low = start_record
      high = end_record - 1
      while low <= high:
          mid = (low + high) // 2
          file_handle.seek(mid * 24)
          record_bytes = file_handle.read(24)
          city_name = record_bytes[:14].split(b'\x00')[0].decode('latin-1').lower()
          if city_name == target_name.lower():
              return unpack_city_record(record_bytes)
          elif city_name < target_name.lower():
              low = mid + 1
          else:
              high = mid - 1
      return None
  ```

---

## 3. SQLite Full-Text Search (FTS5) Modern Architecture

For production web APIs (as implemented in `PanchangHub`):
- `places.sqlite` contains over 5.17 million GeoNames populated places.
- Incorporates SQLite `FTS5` virtual table (`places_fts`) indexing `name`, `asciiname`, `country`, and `admin1`.
- Ranks matches with prefix matching (`q*`), exact name preference, and population tie-breaking.

---

## 4. Time Zone & Daylight Saving Time (DST) Resolution

1. **IANA Time Zone Database (`tzdata`)**:
   Standardized Olson time zone identifiers (e.g. `Asia/Kolkata`, `America/New_York`, `Europe/London`).
2. **Historical War Time & DST Shifts**:
   - India: Indian Standard Time (IST, UTC+5:30) was adopted in 1906. War Time (UTC+6:30) was observed between 1942 and 1945.
   - United States: War Time (UTC-4 for EDT) during WWII (1942-1945).
   - Python's standard `zoneinfo.ZoneInfo` combined with `tzdata` ensures sub-second accuracy across all historical dates.
3. **Fallback Resolution Pipeline**:
   1. Explicit `lat, lon, tz` query parameters.
   2. GPS reverse geocoding to nearest populated place (`/api/cities/nearest`).
   3. Browser IANA timezone fallback to largest city in zone (`/api/cities/timezone`).
   4. Cookie/local storage persistence (`ph_loc`).
