# Ender 3 + Raspberry Pi

An original Creality Ender 3 (V4.2.2 board, CR Touch) driven by a Raspberry Pi 4
running [Klipper](https://www.klipper3d.org/), with **Ender Studio**: a friendly
web UI of our own that slices on the Pi.

Ender Studio (`studio/`) has these tabs:

- **Prepare:** a 3D plate with auto-orient and lay-flat, supports, shapes and text, and filament presets with per-filament first-layer squish. It slices with PrusaSlicer and previews the result.
- **Print:** live first-layer adjust, speed, flow and fan, skipping objects mid-print, colour changes and a print queue.
- **Control:** jogging, preheat, filament load/unload and macros.
- **Files:** sliced prints and models.
- **Maintenance:** software updates, a levelling assistant, Z offset, PID tuning, calibration prints and a config editor.

Other folders:

- `config/`: a mirror of the Klipper/Moonraker config.
- `klipper_extras/z_guard.py`: stops the printer if the spare Z switch clicks while homing or probing.
- `firmware/`: the Klipper MCU build for the V4.2.2 board.
- `PLAN.md`: build history and what's next.

## Install on the Pi

Klipper, Moonraker, nginx and PrusaSlicer must already be installed.

```sh
git clone https://github.com/SnorbWorks/ender3-pi ~/ender3-pi
sh ~/ender3-pi/studio/deploy/install.sh
```

Ender Studio is then at `http://<pi>/` and Mainsail moves to port 8080.

## Updates

The Pi checks this repo every 6 hours and installs new commits on `master` when
the printer is idle. If anything fails to start, it rolls itself back. The
Maintenance page shows the status and has *Check now*, *Install now* and an
auto-update switch. To publish an update, commit and run `sh studio/deploy/push.sh`.

The Pi logs each update to `~/printer_data/logs/studio_update.log`.
