# Ender 3 + Pi — Plan

Started 2026-10-27. A Raspberry Pi 4 (1 GB, `raspberrypi-1`, 10.0.0.139) runs the
printer over USB with Klipper, and a web UI of our own controls it over Wi-Fi.

## What we have

| | |
|---|---|
| Printer | Reports "Ender-3 E", Creality Marlin 2.0.8.2 (Sep 2022) |
| Link | CH340 USB serial → `/dev/ttyUSB0` on the Pi, 115200 baud |
| Probe | ABL probe (CR Touch style), offset X-43 Y-10, 4×4 mesh |
| Extruder | 93 steps/mm (Creality metal extruder, as on the Neo line) |
| Bed | Mesh spread ≈ 0.46 mm (-0.19 → +0.27): low front left, high at the back |
| Stock tuning | Accel 500, jerk 6, hotend PID 12.53/0.68/47.63, bed PID 198.96/38.80/680.25 |
| Backup | `backup/marlin-M503-2026-10-27.txt`, `backup/marlin-M115-2026-10-27.txt` |

| Mainboard | Creality **V4.2.2**, chip **STM32F103 RCT6** (genuine ST; photo 2026-10-27) |

Klipper build for it (`firmware/klipper-20261027.config`): STM32F103, 28 KiB
bootloader (0x8007000), 8 MHz crystal, serial on USART1 (PA10/PA9) at 250000.

## The firmware answer

Klipper splits the work: the Pi does the thinking (motion planning, macros,
input shaping) and the printer's board only runs a small Klipper program that
moves motors and reads sensors. So **yes, the printer's Marlin gets replaced**
with Klipper's MCU firmware, flashed from the SD card. It's reversible: the
stock Creality `.bin` can be flashed back the same way, and the backup above
has its settings.

## Phases

### 1. Ground work (the Pi)
- Update the OS, set a fixed address (DHCP reservation or `raspberrypi-1.local`).
- Install Klipper + Moonraker (Moonraker is the API our UI talks to).
- Install **Mainsail** too, as a known-good reference/fallback while our UI grows.
- Keep it light for 1 GB: no slicing or building on the Pi; the UI is built on
  the Mac and served as static files by nginx.

### 2. Klipper on the printer
- Identify the board/chip (above), build the matching Klipper firmware.
- Download and keep Creality's stock firmware for this model (way back).
- Flash from the SD card; confirm Klipper connects over `/dev/serial/by-id/…`.
- Write `printer.cfg` from Klipper's sample for the board, with the probe
  offset, `safe_z_home`, bed mesh, runout sensor and thermal protection.

### 3. Calibrate (first prints)
Order matters; each builds on the last.
1. Endstops, motor directions, probe accuracy (`PROBE_ACCURACY`), Z offset.
2. PID for hotend and bed (`PID_CALIBRATE`).
3. Extruder rotation distance (100 mm extrude test).
4. Bed mesh (e.g. 7×7, adaptive meshing per print).
5. Flow / extrusion multiplier, first layer.
6. Pressure advance (tower).
7. **Input shaper** (needs an ADXL345 accelerometer, ~$10): the biggest
   quality-at-speed jump Klipper offers; then raise accel/speed.
8. Retraction, max volumetric flow, skew correction.

### 4. Our web UI (the big one)
Runs in any browser on the network; talks to Moonraker's WebSocket API.
- **Dashboard:** state, temps with graph, progress/ETA, live toolhead position,
  current layer, fan/speed/flow sliders, pause/resume/cancel, emergency stop.
- **Files:** upload G-code (drag & drop), thumbnails, metadata (time, filament),
  print history, start/queue.
- **Modify prints:** G-code viewer with layer preview; edits applied on the Pi
  before printing: pause at layer (filament swap), temperature/speed changes
  at a height, swap start/end G-code, cancel single objects mid-print
  (Klipper `exclude_object`).
- **Control:** jog/home, bed mesh view (3D heatmap), macros as buttons,
  calibration wizards (PID, pressure advance, input shaper) with guided steps.
- **Monitoring:** webcam, timelapse, notifications when a print ends or fails.
- Later: slicing from STL (a slicer CLI, likely on the Mac/another machine,
  not the 1 GB Pi).

### 5. Hardware upgrades (pick as we go)
By payoff for print quality:
1. ADXL345 accelerometer (input shaping) — needed in phase 3.
2. USB webcam (monitoring, timelapse).
3. PEI spring-steel sheet (adhesion, easy removal) if not fitted.
4. Belt tension check, eccentric nuts, silicone bed spacers (holds level).
5. Later: better hotend / direct-drive, part-cooling fan duct.

## Safety rules
- Never open the USB serial port mid-print (it resets the board).
- Keep Klipper's heater checks on; watch the first prints in person.
- Flashing is done by the owner with the printer powered and attended.

## Status
- 2026-10-27 phase 1 done: OS updated; Klipper v0.13.0-818, Moonraker v0.11.0,
  Mainsail v2.19.0 behind nginx at http://raspberrypi-1.local. `printer.cfg` is a
  placeholder (no [mcu]) until the board is flashed.
- Klipper firmware built: `firmware/klipper-20261027.bin`.

## Next
Flash the board from the SD card, then write the real `printer.cfg`.
