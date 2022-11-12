# Temperature Server

## Overview

This Server receives measurements from a cooking thermometer with two probes. One measures the temperature of the oven and the other one the core temperature of the meat. The measurements are shown on a webpage and the remaining time is predicted until the core reaches a specified temperature.

## Data Flow

```mermaid
flowchart LR
meas[Measurement Device]
sim[Simulator]
inputs[Inputs]
database[(Database)]
server[Server]
predictor[Predictor]
gui[Web Client]

meas --> inputs
sim --> inputs
inputs --> server
database <--> server
server <--> predictor
server <---> gui
```
