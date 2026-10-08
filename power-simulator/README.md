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

**PolyForm Strict License 1.0.0** applies to the Power Simulator files in this directory, including the latest stable simulator and archived versions, to the extent the repository owner has rights to license them.

- **Permitted:** noncommercial use, including personal experimentation and eligible educational/research use, as defined in the license.
- **Not licensed:** distributing copies, making modified or derivative versions, or commercial use.
- **For permission outside these terms:** contact [@ThatAnarchyDude](https://github.com/ThatAnarchyDude) to discuss a separate agreement.

Read the [full, unmodified license](./LICENSE.md) or the [official license text](https://polyformproject.org/licenses/strict/1.0.0). Applicable law (including fair use) and GitHub's platform terms may provide separate rights. A license cannot establish copyright protection in material that is not protected by copyright.

**Project attribution:** A Corvus Workshop experiment maintained by **ThatAnarchyDude**, developed with AI assistance through the **Zander Corvus** collaboration.

---
Part of the [Corvus Workshop](../README.md).
