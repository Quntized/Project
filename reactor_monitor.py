import pygame
import serial
import serial.tools.list_ports
import threading
import queue
import time

# --- CONFIGURATION ---
INTERNAL_WIDTH = 640
INTERNAL_HEIGHT = 480
BAUD_RATE = 115200 

# Queue to hold incoming commands
data_queue = queue.Queue()
connection_status = "Searching..."
last_connection_status = "Searching..." # Track history to detect state changes

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
                # print(f"Connecting to {port}...")
                
                with serial.Serial(port, BAUD_RATE, timeout=1) as ser:
                    ser.reset_input_buffer()
                    
                    while True:
                        try:
                            line = ser.readline().decode('utf-8', errors='ignore').strip()
                            if line:
                                data_queue.put(line)
                        except serial.SerialException:
                            break # Break inner loop to trigger reconnect
                            
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
    flags = pygame.FULLSCREEN | pygame.SCALED
    screen = pygame.display.set_mode((INTERNAL_WIDTH, INTERNAL_HEIGHT), flags)
    pygame.display.set_caption("RP2040 Reactor Monitor")
    pygame.mouse.set_visible(False)
    
    # Fonts
    font = pygame.font.SysFont("Courier New", 12, bold=True)
    big_font = pygame.font.SysFont("Courier New", 24, bold=True)

    running = True
    clock = pygame.time.Clock()
    
    # State tracking
    was_connected = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # --- DRAWING LOOP ---
        if connection_status == "Connected":
            
            # FIX: If we JUST reconnected, wipe the screen once!
            if not was_connected:
                screen.fill((0,0,0))
                pygame.display.flip()
                was_connected = True

            # Process commands
            commands_processed = 0
            while not data_queue.empty() and commands_processed < 5000:
                cmd_line = data_queue.get()
                parts = cmd_line.split(',')
                commands_processed += 1
                
                try:
                    cmd = parts[0]
                    if cmd == 'R': # Rect
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
                    elif cmd == 'T': # Text
                        col = COLORS.get(int(parts[3]), (255,255,255))
                        text_surface = font.render(parts[4], True, col)
                        screen.blit(text_surface, (int(parts[1]), int(parts[2])))
                    elif cmd == 'FRAME_END':
                        pygame.display.flip()
                except (ValueError, IndexError):
                    pass
        else:
            # Connection is LOST
            was_connected = False # Reset flag so we wipe screen next time we connect
            
            # Draw the Red Warning Screen
            screen.fill((0,0,0))
            text = big_font.render(f"{connection_status}...", True, (255, 0, 0))
            
            # Center the text
            text_rect = text.get_rect(center=(INTERNAL_WIDTH/2, INTERNAL_HEIGHT/2))
            screen.blit(text, text_rect)
            pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
