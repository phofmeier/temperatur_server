import pytest


def test_import():
    try:
        import database.database  # noqa: F401
        import input.measurement_parser  # noqa: F401
        import models.fourier_series_model  # noqa: F401
        import models.meat_estimator  # noqa: F401
        import models.meat_model  # noqa: F401
        import models.oven_estimator  # noqa: F401
        import models.oven_model  # noqa: F401
        import models.predictor  # noqa: F401
        import simulator.main  # noqa: F401
        import temperatur_server.api.api_manager  # noqa: F401
        import temperatur_server.api.js_api  # noqa: F401
        import temperatur_server.main  # noqa: F401
        import temperatur_server.server_state  # noqa: F401
    except ImportError:
        pytest.fail("Import Error occurred. Check dependencies.")
