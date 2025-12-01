# ☢️ RP2040 RBMK Nuclear Reactor Simulator

![Reactor Simulation Preview](reactor_preview.png)

A real-time, dual-core particle physics simulation of a Chernobyl-style RBMK nuclear reactor running on a Raspberry Pi Pico (RP2040).

Unlike standard simulations that run entirely on a PC, this project uses the **RP2040 microcontroller as a dedicated physics engine**. It calculates neutron diffusion, uranium fission events, xenon poisoning, and thermal dynamics in real-time. The visual state is transmitted over **high-speed USB Serial** to a host PC, where a Python/Pygame monitor renders the display.

## 🚀 Features

* **Particle Physics Engine:** Simulates ~2,000 individual neutrons interacting with fuel, moderators, and control rods.
* **Multithreaded Architecture:**
    * **Core 0:** Physics calculations, Thermal dynamics, Serial Telemetry.
    * **Core 0 (Threaded):** Real-time Input polling (Encoders/Buttons).
    * **DMA/SPI:** Background Audio Synthesis (Geiger clicks & Reactor Hum).
* **Physical Control Console:** Use physical rotary encoders and buttons to operate the reactor rods and cooling pumps.
* **Audio Feedback:** Generates authentic Geiger-counter clicking and low-frequency reactor hum based on flux levels.

---

## 🛠️ Hardware Bill of Materials

### **Core Components**
* **1x** Raspberry Pi Pico (RP2040)
* **1x** Breadboard & Jumper Wires (Male-to-Male & Female-to-Male)

### **Control Panel**
* **4x** Rotary Encoders (KY-040 or standard)
* **4x** Push Buttons (4-pin Tactile Switches)

### **Audio System (Optional but Recommended)**
* **1x** MCP4822 DAC Chip (12-bit, SPI, DIP-8)
* **1x** TRRS 3.5mm Breakout Board (or PCB Mount Socket)
* **1x** Set of Active Computer Speakers (USB Powered)
    * *(Alternatively: PAM8403 Amp Module + 8Ω 1W Raw Speaker)*

---

## 🔌 Wiring Guide & Pinout

### **1. Power Distribution**
Connect the Pico to the breadboard power rails to share power with all components.
* **Red Rail (+):** Connect to **Pico Pin 36 (3V3_OUT)**.
* **Blue Rail (-):** Connect to **Pico Pin 38 (GND)**.

### **2. Rotary Encoders (Controls)**
Connect **+** to Red Rail and **GND** to Blue Rail. Wire signals as follows:

| Encoder | Function | CLK (Pin A) | DT (Pin B) |
| :--- | :--- | :--- | :--- |
| **Encoder 1** | **Control Rods** (Manual) | GP27 (Pin 32) | GP26 (Pin 31) |
| **Encoder 2** | **Water Flow Pump** | GP6 (Pin 9) | GP7 (Pin 10) |
| **Encoder 3** | **Target Flux Set** | GP28 (Pin 34) | GP22 (Pin 29) |
| **Encoder 4** | **Spawn Rate** (Multiplier)| GP8 (Pin 11) | GP9 (Pin 12) |

### **3. Push Buttons (Triggers)**
Connect one leg to the Pico GPIO and the diagonal leg to **GND** (Blue Rail).

| Button | Function | Pico GPIO | Physical Pin |
| :--- | :--- | :--- | :--- |
| **Button 1** | 🔴 **SCRAM** (Emergency) | **GP2** | Pin 4 |
| **Button 2** | 🔄 **Auto/Manual** Toggle | **GP4** | Pin 6 |
| **Button 3** | ⚓ **Sync Position** | **GP5** | Pin 7 |
| **Button 4** | ⏩ **Sim Speed** (50/100%) | **GP3** | Pin 5 |

### **4. Audio System (DAC)**
Connect the **MCP4822 DAC** to the Pico SPI bus.

| DAC Pin | Name | Connect To |
| :--- | :--- | :--- |
| **1** | VDD | **3.3V** (Red Rail) |
| **2** | CS | **GP13** (Pin 17) |
| **3** | SCK | **GP10** (Pin 14) |
| **4** | SDI | **GP11** (Pin 15) |
| **5** | LDAC | **GND** (Blue Rail) |
| **7** | VSS | **GND** (Blue Rail) |
| **8** | **VOUTA**| **Audio Jack Tip/Ring** |

> **Audio Jack Wiring:** Connect DAC Pin 8 to the `TIP` and `RING` pins of your audio socket. Connect `SLEEVE` to GND.

---

## 💻 Software Installation

### **Prerequisites**
* **On PC:** Python 3.x installed.
* **On Pico:** Raspberry Pi Pico C/C++ SDK (VS Code Recommended).

### **Step 1: Build & Flash Firmware**
1.  Open this project in **VS Code** with the *Raspberry Pi Pico* extension.
2.  Click **"Compile Project"** (or run `cmake` build).
3.  Hold the **BOOTSEL** button on the Pico and plug it into USB.
4.  Drag and drop the generated `build/reactor_sim.uf2` file onto the **RPI-RP2** drive.
5.  The Pico will reboot and immediately begin the physics simulation.

### **Step 2: Run the Display Monitor**
Open your terminal in the project folder.

**On Linux (Ubuntu/Debian):**
```bash
# Install dependencies
pip install pygame pyserial

# Run the monitor (sudo needed for serial port access)
sudo python3 reactor_monitor.py
```
## 🎛️ Operator's Manual

### Operating Modes
* **AUTO Mode:** The computer automatically moves Control Rods to maintain the "Target Neutron" count.
* **MANUAL Mode:** The operator has full control over the rods via Encoder 1.

### Controls

| Control | Action | Description |
| :--- | :--- | :--- |
| **Button 2** | **Toggle Mode** | Switch between **AUTO** and **MANUAL** mode. |
| **Encoder 1** | **Rod Height** | Manually raise/lower Graphite Control Rods (Only works in Manual Mode). |
| **Encoder 2** | **Water Flow** | Adjust cooling pumps. High flow = Blue (Water). Low flow/High heat = Cyan (Steam). |
| **Encoder 3** | **Target Flux** | Sets the blue target line on the graph. The Auto-pilot chases this value. |
| **Encoder 4** | **Reactivity** | Adjusts neutron multiplication factor (1-6). **WARNING:** High values cause exponential runaway! |
| **Button 1** | **SCRAM** | **EMERGENCY SHUTDOWN.** Instantly drops all rods to 100% insertion. Kills reaction immediately. |

---

## 📚 References & Credits
This project was built based on the course material and Protothreads libraries developed by:

* **Hunter Adams** (Cornell University) - *RP2040 Protothreads & Physics Architectures*
* **Bruce Land** (Cornell University) - *Real-time Embedded Systems Course*

The simulation logic has been adapted to run over Serial/USB for modern display support while maintaining the original physics calculations.
