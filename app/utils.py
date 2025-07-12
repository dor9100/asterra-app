import geojson


def is_valid_geojson(data):
    try:
        gj = geojson.loads(data)
        return gj.is_valid
    except Exception:
        return False
