# Ender 3 + Raspberry Pi

An original Creality Ender 3 (V4.2.2 board, CR Touch) driven by a Raspberry Pi 4
running [Klipper](https://www.klipper3d.org/).

The web app that runs it, **SnorbStudio** (with the SnorbCAD designer), now has
its own repo: **https://github.com/SnorbWorks/snorbstudio**. The Pi updates from
there. It was the `studio/` folder here until 2026-11-09, and its history moved
along with it.

This repo keeps what's specific to this printer:

- `config/`: a mirror of the Klipper/Moonraker config.
- `firmware/`: the Klipper MCU build for the V4.2.2 board.
- `backup/`: the stock Marlin settings.
- `models/`: parts we print for it (Pi 5 case, gears, ...).
- `PLAN.md`: build history and what's next.

