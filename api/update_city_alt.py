import sqlite3

db_path = "D:/panchanghub-FULL/api/data/places.sqlite"
con = sqlite3.connect(db_path)
cur = con.cursor()

# Check Kathlal row
row = cur.execute("SELECT id, name, ascii, alt FROM places WHERE id = 1267495").fetchone()
print("Original row:", ascii(row))

new_alt = "Kathalal, Kathal, Kathlal, Kathalal Gujarat, Kathlal Gujarat, Kheda, \u0a95\u0aa0\u0ab2\u0abe\u0ab2"

# Update FTS delete old entry
cur.execute("INSERT INTO places_fts(places_fts, rowid, name, ascii, alt) VALUES('delete', 1267495, ?, ?, ?)", (row[1], row[2], row[3]))

# Update main table
cur.execute("UPDATE places SET alt = ? WHERE id = 1267495", (new_alt,))

# Insert into FTS new entry
cur.execute("INSERT INTO places_fts(rowid, name, ascii, alt) VALUES(1267495, ?, ?, ?)", (row[1], row[2], new_alt))

con.commit()
print("Updated successfully!")

# Test search
for q in ["kathal", "kathalal", "kathlal"]:
    match = f'"{q}"*'
    res = cur.execute("""SELECT p.name, p.ascii, p.admin_name, p.country, p.pop 
                         FROM places_fts f JOIN places p ON p.id = f.rowid 
                         WHERE places_fts MATCH ? LIMIT 10""", (match,)).fetchall()
    print(f"\nResults for '{q}':")
    for r in res:
        print(" ", ascii(r))

con.close()
