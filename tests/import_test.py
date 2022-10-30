def test_import():
    import simulator.main  # noqa: F401
    import temperatur_server.main  # noqa: F401
    from temperatur_server.database import MeasurementDB  # noqa: F401
