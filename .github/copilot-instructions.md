<!--
  copilot-instructions.md
  Purpose: short, focused guidance to help an AI coding assistant become productive in this repo.
  Keep the file concise (~20–50 lines) and focused on discoverable, actionable patterns.
-->

# Quick onboarding notes for AI coding agents

This repository is a Raspberry Pi Pico (RP2040) C firmware project plus a Python/Pygame USB-Serial monitor.
The firmware (main.c) runs the reactor physics & serial graphics pipeline on the Pico. The Python script (`reactor_monitor.py`) receives simple comma-separated commands over USB and renders the display.

Key files to read first
- `main.c` — core simulation, hardware configuration, protothreads, PIO/DMA and SPI audio code. (big file — search for "PROTOTHREAD" and "PIO" to find major components)
- `reactor_monitor.py` — PC side renderer and serial protocol (baud: 115200). Look for command handlers: 'R', 'C', 'L', 'P', 'T', and 'FRAME_END'.
- `CMakeLists.txt` — project build info (Pico SDK, enable_stdio_usb, linked hardware libs, UF2 output, and expected SDK path under `~/.pico-sdk`)
- `serial_graphics.h` — helper drawing primitives used by `main.c` to stream rendering commands to serial.

High-level architecture (what matters)
- Firmware runs on RP2040 using Pico SDK; it uses PIO state machines and DMA to drive audio/VGA primitives and Protothreads for concurrency.
- Output is forwarded over USB Serial (stdio enabled) to the PC monitor; the renderer is intentionally decoupled from the physics engine.
- The Python monitor assumes a 640x480 virtual frame and a fixed text/graphics command protocol — keep compatibility when changing formats.

Build / run / debug workflows you will use
- Build firmware (from workspace root):
  - Using VS Code + Pico extension: use the provided tasks; "Compile Project" runs ninja on `build/`.
  - CLI: cmake -S . -B build && cmake --build build (or ninja -C build)
- Flashing: drop `build/reactor_sim.uf2` onto the Pico's RPI-RP2 mass-storage or use `picotool`/OpenOCD tasks in the project. See the tasks in the workspace for examples.
- Run monitor: python3 reactor_monitor.py (may require sudo on Linux for serial port access). Default BAUD_RATE = 115200.

Project-specific coding patterns & constraints
- Serial protocol: textual comma-separated commands. Any change to the render format must update `reactor_monitor.py`.
- Graphics primitives live in `serial_graphics.h`; prefer using these helpers instead of ad-hoc print statements for rendering.
- Concurrency: uses protothreads (`pt_cornell_rp2040_v1_3.h`) and fixed point math (fix15) for performance — avoid introducing heavy floating-point work on Core0.
- Hardware assumptions: pins (GPIO, SPI1) and DMA channels are hard-coded in `main.c` and CMake uses `pico_enable_stdio_usb(reactor_sim 1)` to route prints to USB; keep those settings if you intend to preserve the monitor flow.

Integration, external dependencies and environment notes
- Pico SDK expected under `~/.pico-sdk` and version found in `CMakeLists.txt` (2.2.0). Builds will fail without it.
- PC monitor depends on Python packages: `pygame` and `pyserial`.

When modifying code — short checklist
1. Keep the USB serial textual API compatible with `reactor_monitor.py` (or update both sides together).
2. If you change pin/DMA usage, update README and `main.c` comments — hardware wiring is documented in README.
3. For performance-sensitive changes, search `fix15`, protothreads, and PIO/DMA usages in `main.c` to ensure you don't introduce heavy CPU loads.

If anything here is unclear or you need more examples (e.g., typical command lines or expected serial payloads), tell me which parts to expand and I will add concise examples and tests.
