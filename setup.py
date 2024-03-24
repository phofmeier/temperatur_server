#!/usr/bin/env python3

import sys

import setuptools

# from submodule.temperature_proto.setup import build

if __name__ == "__main__":
    sys.path.append("./submodule/")
    from temperature_proto.install_helper import build

    print("Build Protobuf")
    build("./submodule/temperature_proto/proto")
    setuptools.setup()
