def store_ndvi_profile(conn, lat, lon, profile, mission, year):
    query = """
        INSERT INTO ndvi_profils (geom, ndvi_values, mission, year)
        VALUES (ST_SetSRID(ST_Point(%s, %s), 4326), %s, %s, %s)
    """
    cur = conn.cursor()
    cur.execute(query, (lon, lat, profile, mission, year))
    conn.commit()
    cur.close()
