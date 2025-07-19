def insert_fertilisation(conn, lat, lon, npk, crop, year, source="auto"):
    query = """
        INSERT INTO fertilisation_recommandee (geom, crop, year, n, p, k, source)
        VALUES (ST_SetSRID(ST_Point(%s, %s), 4326), %s, %s, %s, %s, %s, %s)
    """
    cur = conn.cursor()
    cur.execute(query, (lon, lat, crop, year, npk["N"], npk["P"], npk["K"], source))
    conn.commit()
    cur.close()
