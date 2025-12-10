import pygame
import serial
import serial.tools.list_ports
import threading
import queue
import time
import os

# --- CONFIGURATION ---
INTERNAL_WIDTH = 640
INTERNAL_HEIGHT = 480
BAUD_RATE = 115200 
ALARM_THRESHOLD = 400  # Trigger alarm if neutrons > 400

# Queue to hold incoming commands
data_queue = queue.Queue()
connection_status = "Searching..."

# Color Map (Matches Pico C definitions)
COLORS = {
    0: (0, 0, 0),       1: (255, 255, 255), 2: (255, 0, 0),
    3: (0, 255, 0),     4: (0, 0, 255),     5: (255, 255, 0),
    6: (0, 255, 255),   7: (255, 0, 255),   20: (0, 0, 139),
    30: (0, 0, 255),    40: (173, 216, 230), 50: (0, 100, 0),
    250:(255, 182, 193)
}

def find_pico():
    """Auto-detects the Pico serial port"""
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        # Linux usually names it ttyACM0, Windows COMx
        if "ACM" in p.device or "USB" in p.description:
            return p.device
    return None

def serial_worker():
    """Background thread to read USB data without freezing the screen"""
    global connection_status
    while True:
        port = find_pico()
        if port:
            try:
                connection_status = "Connected"
                with serial.Serial(port, BAUD_RATE, timeout=1) as ser:
                    ser.reset_input_buffer()
                    while True:
                        try:
                            line = ser.readline().decode('utf-8', errors='ignore').strip()
                            if line:
                                data_queue.put(line)
                        except serial.SerialException:
                            break # Device disconnected, break loop to search again
            except (OSError, serial.SerialException):
                connection_status = "Connection Lost"
                time.sleep(1)
        else:
            connection_status = "Searching..."
            time.sleep(1)

def main():
    # Start the Serial Thread
    t = threading.Thread(target=serial_worker, daemon=True)
    t.start()

    pygame.init()
    
    # --- SAFE AUDIO INIT ---
    # Attempts to load audio, but won't crash if sudo blocks access
    alarm_sound = None
    try:
        pygame.mixer.init()
        if os.path.exists("alarm.wav"):
            try:
                alarm_sound = pygame.mixer.Sound("alarm.wav")
                print("Audio: Alarm sound loaded successfully.")
            except:
                print("Audio: Error loading alarm.wav file.")
        else:
            print("Audio: 'alarm.wav' not found. Running silent mode.")
    except pygame.error:
        print("Warning: Audio system unavailable (Sudo restriction?). Running without alarm.")
        alarm_sound = None
    # -----------------------

    # Display Setup
    flags = pygame.FULLSCREEN | pygame.SCALED
    screen = pygame.display.set_mode((INTERNAL_WIDTH, INTERNAL_HEIGHT), flags)
    pygame.display.set_caption("RP2040 Reactor Monitor")
    pygame.mouse.set_visible(False)
    
    # Fonts
    font = pygame.font.SysFont("Courier New", 12, bold=True)
    big_font = pygame.font.SysFont("Courier New", 24, bold=True)

    running = True
    clock = pygame.time.Clock()
    was_connected = False
    alarm_active = False

    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Logic Logic
        if connection_status == "Connected":
            
            # If we just came back online, wipe the "Connection Lost" text
            if not was_connected:
                screen.fill((0,0,0))
                pygame.display.flip()
                was_connected = True

            # Process Data
            commands_processed = 0
            while not data_queue.empty() and commands_processed < 5000:
                cmd_line = data_queue.get()
                parts = cmd_line.split(',')
                commands_processed += 1
                
                try:
                    cmd = parts[0]
                    
                    # --- CHECK FOR NEUTRON COUNT (For Alarm) ---
                    if cmd == 'T':
                        t_x = int(parts[1])
                        t_y = int(parts[2])
                        
                        # Look for text near X=65, Y=260 (Neutron Count location)
                        if t_y == 260 and 60 <= t_x <= 70:
                            neutron_count = int(parts[4])
                            
                            # Alarm Trigger
                            if neutron_count > ALARM_THRESHOLD:
                                if not alarm_active and alarm_sound:
                                    alarm_sound.play(-1) # Loop sound
                                    alarm_active = True
                            else:
                                if alarm_active and alarm_sound:
                                    alarm_sound.stop()
                                    alarm_active = False

                        # Draw the text
                        col = COLORS.get(int(parts[3]), (255,255,255))
                        text_surface = font.render(parts[4], True, col)
                        screen.blit(text_surface, (int(parts[1]), int(parts[2])))

                    # --- STANDARD GRAPHICS COMMANDS ---
                    elif cmd == 'R': # Rectangle
                        col = COLORS.get(int(parts[5]), (255,255,255))
                        pygame.draw.rect(screen, col, (int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])))
                    elif cmd == 'C': # Circle
                        col = COLORS.get(int(parts[4]), (255,255,255))
                        pygame.draw.circle(screen, col, (int(parts[1]), int(parts[2])), int(parts[3]))
                    elif cmd == 'L': # Line
                        col = COLORS.get(int(parts[5]), (255,255,255))
                        pygame.draw.line(screen, col, (int(parts[1]), int(parts[2])), (int(parts[3]), int(parts[4])))
                    elif cmd == 'P': # Pixel
                        col = COLORS.get(int(parts[3]), (255,255,255))
                        screen.set_at((int(parts[1]), int(parts[2])), col)
                    elif cmd == 'FRAME_END':
                        pygame.display.flip()
                        
                except (ValueError, IndexError):
                    pass # Ignore garbled data
        else:
            # Connection Lost State
            was_connected = False
            if alarm_active and alarm_sound: 
                alarm_sound.stop()
                alarm_active = False
            
            # Draw Red Error Screen
            screen.fill((0,0,0))
            text = big_font.render(f"{connection_status}...", True, (255, 0, 0))
            text_rect = text.get_rect(center=(INTERNAL_WIDTH/2, INTERNAL_HEIGHT/2))
            screen.blit(text, text_rect)
            pygame.display.flip()

        clock.tick(60) # Limit to 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()
