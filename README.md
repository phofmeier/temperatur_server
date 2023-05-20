![Pre Commit](https://github.com/phofmeier/temperatur_server/actions/workflows/pre-commit.yml/badge.svg)
![Unit Tests](https://github.com/phofmeier/temperatur_server/actions/workflows/unittests.yml/badge.svg)
![Docs](https://github.com/phofmeier/temperatur_server/actions/workflows/docs.yml/badge.svg)

# Temperature Server

## Overview

This Server receives measurements from a cooking thermometer with two probes. One measures the temperature of the oven and the other one the core temperature of the meat. The measurements are shown on a webpage and the remaining time is predicted until the core reaches a specified temperature.

## Documentation

The documentation can be found [here](https://phofmeier.github.io/temperatur_server/).

## Install

### Development

To install the Server clone the repository and run the server in python virtual environment.

```sh
python3 -m venv ./venv/
source venv/bin/activate
pip install . # or use pip install -e .[dev] for development
temperatur_server
```

### Docker

Pull the Docker container from the registry and run it.
Currently the Network is exposed on port 5000.

```sh
docker run -d -p5000:5000 ghcr.io/phofmeier/temperatur_server:latest
```
