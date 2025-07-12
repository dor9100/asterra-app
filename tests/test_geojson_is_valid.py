#CHECKING IF is_valid function is working properly , small example using number of points
import geojson

def test_valid_geojson():
    # Create a valid FeatureCollection using geojson objects
    feature = geojson.Feature(
        geometry=geojson.Point((102.0, 0.5)),
        properties={"prop0": "value0"}
    )
    fc = geojson.FeatureCollection([feature])
    assert fc.is_valid is True

def test_invalid_geojson():
    # Create an invalid Point (too many coordinates)
    bad_point = geojson.Point((-3.68, 40.41, 25.14, 10.34))  # 4D point is not valid
    assert bad_point.is_valid is False
