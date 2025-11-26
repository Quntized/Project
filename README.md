# RP2040 RBMK Nuclear Reactor Simulator

![Reactor Simulation Preview](reactor_preview.png)

A real-time particle physics simulation of a Chernobyl-style RBMK nuclear reactor running on a Raspberry Pi Pico (RP2040).

The Pico handles the heavy lifting: it calculates neutron diffusion, uranium fission events, xenon poisoning, and thermal dynamics in real-time. Instead of driving a VGA display directly, it sends high-speed telemetry data over USB Serial to a PC, where a Python/Pygame script renders the display in full screen.

## 🚀 Features
* **Particle Physics Engine:** Simulates individual neutrons interacting with fuel, moderators, and control rods.
* **Multithreaded Architecture:** Uses Protothreads to handle physics calculations, serial communication, and user inputs simultaneously.
* **Real-time Telemetry:** Live graphing of neutron flux, thermal capacity, and reaction history.
* **Physical Control Console:** Uses rotary encoders and buttons to manually operate control rods and cooling pumps.

## 🛠️ Hardware Required
* **1x Raspberry Pi Pico** (RP2040)
* **4x Rotary Encoders** (KY-040 or standard)
* **2x Push Buttons** (Tactile switches)
* **1x Breadboard**
* **Jumper Wires** (Male-to-Male)

## 🔌 Wiring Guide / Pinout

Connect the components to the Pico using the pins defined below.
* **Power:** Connect the **3.3V (Pin 36)** to the Red Rail and **GND (Pin 38)** to the Blue Rail of your breadboard.
* **Encoders:** Connect all Encoder `+` to 3.3V and `GND` to the Ground Rail.

| Component | Function | CLK / Pin 1 | DT / Pin 2 | Pico GPIO | Physical Pins |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Encoder 1** | Manual Rod Control | CLK | DT | **GP27, GP26** | 32, 31 |
| **Encoder 2** | Water Flow Pump | CLK | DT | **GP6, GP7** | 9, 10 |
| **Encoder 3** | Neutron Target Set | CLK | DT | **GP28, GP22** | 34, 29 |
| **Encoder 4** | Reaction Multiplier | CLK | DT | **GP8, GP9** | 11, 12 |
| **Button 1** | **SCRAM** (Emergency) | Pin 1 | GND | **GP2** | 4 |
| **Button 2** | Auto/Manual Toggle | Pin 1 | GND | **GP4** | 6 |

> **Note:** Buttons connect directly between the GPIO pin and Ground. The code uses internal pull-up resistors.

## 💻 Software Prerequisites

### 1. On your PC (Display)
You need Python installed to run the monitor script.
```bash
pip install pygame pyserial
