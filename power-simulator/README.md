# Power Simulator

An interactive, mobile-friendly electrical power-system simulator in the Corvus Workshop.

## Run the simulator

Open [the current stable version](./index.html) in a browser, or download `index.html` and open the downloaded file locally. No build tools or server required.

## Current version

**Bench 02.1: Electrothermal** is our first published workshop version.

It explores battery and capacitor behavior under intermittent electrical loads using simplified models for:

- Battery internal resistance and state-of-charge-dependent behavior
- Capacitor buffering and equivalent series resistance (ESR)
- Wiring losses and converter efficiency
- Battery, capacitor, and converter temperatures
- Battery discharge and converter current limits
- Undervoltage shutdown and recovery
- Temperatures shown in °F or °C
- Simulation charts, diagnostic results, and CSV export

## Files and updates

- [`index.html`](./index.html): the **latest stable** simulator, updated as new versions are released.
- [`versions/`](./versions/): named snapshots of older releases, retained for reference.

The filename `index.html` remains constant, so people can always find the latest stable version at the same repository path.

## Important limitations

**Educational simulation only.** The model uses approximate electrical, electrochemical, and thermal behavior. It is not a substitute for component datasheets, circuit protection analysis, validation testing, or professional review. Do not use its output alone to size a real battery pack or decide whether a physical design is safe.

## Licensing

No software license has been assigned to this project yet. Do not assume that public source availability grants permission to redistribute, modify, or commercially reuse it. Contact the repository owner to discuss permissions. GitHub's terms still govern use of the GitHub platform.

---
Part of the [Corvus Workshop](../README.md).
