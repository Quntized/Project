import pygame
import serial
import serial.tools.list_ports
import threading
import queue
import time
import os
import random

# --- CONFIGURATION ---
INTERNAL_WIDTH = 640
INTERNAL_HEIGHT = 480
BAUD_RATE = 115200 
ALARM_THRESHOLD = 400 

data_queue = queue.Queue()
connection_status = "Searching..."

# Color Map
COLORS = {
    0: (0, 0, 0),       1: (255, 255, 255), 2: (255, 0, 0),
    3: (0, 255, 0),     4: (0, 0, 255),     5: (255, 255, 0),
    6: (0, 255, 255),   7: (255, 0, 255),   20: (0, 0, 139),
    30: (0, 0, 255),    40: (173, 216, 230), 50: (0, 100, 0),
    250:(255, 182, 193)
}

def find_pico():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "ACM" in p.device or "USB" in p.description:
            return p.device
    return None

def serial_worker():
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
                            break 
            except (OSError, serial.SerialException):
                connection_status = "Connection Lost"
                time.sleep(1)
        else:
            connection_status = "Searching..."
            time.sleep(1)

def main():
    t = threading.Thread(target=serial_worker, daemon=True)
    t.start()

    pygame.init()
    
    # --- AUDIO SETUP ---
    click_sound = None
    alarm_sound = None
    
    try:
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        # Load Click
        if os.path.exists("click.wav"):
            click_sound = pygame.mixer.Sound("click.wav")
            click_sound.set_volume(0.5)
        else:
            print("Warning: 'click.wav' not found.")

        # Load Alarm
        if os.path.exists("alarm.wav"):
            alarm_sound = pygame.mixer.Sound("alarm.wav")
    except pygame.error:
        print("Audio system unavailable.")

    # Display
    flags = pygame.FULLSCREEN | pygame.SCALED
    screen = pygame.display.set_mode((INTERNAL_WIDTH, INTERNAL_HEIGHT), flags)
    pygame.display.set_caption("RP2040 Reactor Monitor")
    pygame.mouse.set_visible(False)
    
    font = pygame.font.SysFont("Courier New", 12, bold=True)
    big_font = pygame.font.SysFont("Courier New", 24, bold=True)

    running = True
    clock = pygame.time.Clock()
    was_connected = False
    alarm_active = False
    
    current_neutrons = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        if connection_status == "Connected":
            if not was_connected:
                screen.fill((0,0,0))
                pygame.display.flip()
                was_connected = True

            # --- GEIGER COUNTER LOGIC ---
            # We play clicks based on probability. 
            # More neutrons = Higher chance to click this frame.
            if click_sound and current_neutrons > 0:
                # Adjust '2000' to change sensitivity. Lower number = More clicks.
                if random.randint(0, 2000) < current_neutrons:
                    click_sound.play()

            commands_processed = 0
            while not data_queue.empty() and commands_processed < 5000:
                cmd_line = data_queue.get()
                parts = cmd_line.split(',')
                commands_processed += 1
                
                try:
                    cmd = parts[0]
                    
                    if cmd == 'T':
                        t_x = int(parts[1])
                        t_y = int(parts[2])
                        
                        # Capture Neutron Count for Audio
                        if t_y == 260 and 60 <= t_x <= 70:
                            current_neutrons = int(parts[4])
                            
                            # Alarm Logic
                            if current_neutrons > ALARM_THRESHOLD:
                                if not alarm_active and alarm_sound:
                                    alarm_sound.play(-1)
                                    alarm_active = True
                            else:
                                if alarm_active and alarm_sound:
                                    alarm_sound.stop()
                                    alarm_active = False

                        col = COLORS.get(int(parts[3]), (255,255,255))
                        text_surface = font.render(parts[4], True, col)
                        screen.blit(text_surface, (int(parts[1]), int(parts[2])))

                    elif cmd == 'R': 
                        col = COLORS.get(int(parts[5]), (255,255,255))
                        pygame.draw.rect(screen, col, (int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])))
                    elif cmd == 'C': 
                        col = COLORS.get(int(parts[4]), (255,255,255))
                        pygame.draw.circle(screen, col, (int(parts[1]), int(parts[2])), int(parts[3]))
                    elif cmd == 'L': 
                        col = COLORS.get(int(parts[5]), (255,255,255))
                        pygame.draw.line(screen, col, (int(parts[1]), int(parts[2])), (int(parts[3]), int(parts[4])))
                    elif cmd == 'P': 
                        col = COLORS.get(int(parts[3]), (255,255,255))
                        screen.set_at((int(parts[1]), int(parts[2])), col)
                    elif cmd == 'FRAME_END':
                        pygame.display.flip()
                        
                except (ValueError, IndexError):
                    pass
        else:
            was_connected = False
            if alarm_active and alarm_sound:
                alarm_sound.stop()
                alarm_active = False
            
            screen.fill((0,0,0))
            text = big_font.render(f"{connection_status}...", True, (255, 0, 0))
            text_rect = text.get_rect(center=(INTERNAL_WIDTH/2, INTERNAL_HEIGHT/2))
            screen.blit(text, text_rect)
            pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
