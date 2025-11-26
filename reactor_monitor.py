import pygame
import serial
import serial.tools.list_ports
import threading
import queue

# --- CONFIGURATION ---
# We keep the internal resolution at 640x480 so your Pico coordinates match.
# Pygame will automatically scale this up to fit your monitor.
INTERNAL_WIDTH = 640
INTERNAL_HEIGHT = 480
BAUD_RATE = 115200 

# Queue to hold incoming commands (buffer to prevent lag)
data_queue = queue.Queue()

# Color Map (Matches your C code defines)
COLORS = {
    0: (0, 0, 0),       # BLACK
    1: (255, 255, 255), # WHITE
    2: (255, 0, 0),     # RED
    3: (0, 255, 0),     # GREEN
    4: (0, 0, 255),     # BLUE
    5: (255, 255, 0),   # YELLOW
    6: (0, 255, 255),   # CYAN
    7: (255, 0, 255),   # MAGENTA
    20: (0, 0, 139),    # DARK_BLUE
    30: (0, 0, 255),    # BLUE
    40: (173, 216, 230),# LIGHT_BLUE
    50: (0, 100, 0),    # DARK_GREEN
    250:(255, 182, 193) # LIGHT_PINK
}

def read_from_serial(ser):
    """Runs in a separate thread to keep reading USB data fast"""
    while True:
        try:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                data_queue.put(line)
        except:
            break

def find_pico():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        # Linux usually names the Pico ttyACM0 or similar
        if "ACM" in p.device or "USB" in p.description:
            return p.device
    return None

def main():
    print("Looking for Reactor...")
    port = find_pico()
    
    if not port:
        # Fallback for Linux if auto-detection fails
        port = input("Pico not found. Enter port manually (e.g., /dev/ttyACM0): ")
    
    print(f"Connecting to {port}...")
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
    except Exception as e:
        print(f"Error: {e}")
        print("Try running with 'sudo' if you have permission errors.")
        return

    # Start the serial reader thread
    t = threading.Thread(target=read_from_serial, args=(ser,), daemon=True)
    t.start()

    pygame.init()
    
    # --- FULL SCREEN SETUP ---
    # We set the mode to 640x480 but add SCALED and FULLSCREEN flags.
    # This makes Pygame stretch the 640x480 image to fill your monitor.
    flags = pygame.FULLSCREEN | pygame.SCALED
    screen = pygame.display.set_mode((INTERNAL_WIDTH, INTERNAL_HEIGHT), flags)
    
    pygame.display.set_caption("RP2040 RBMK Monitor (FULL SCREEN)")
    
    # Hide the mouse cursor for better immersion
    pygame.mouse.set_visible(False)
    
    font = pygame.font.SysFont("Courier New", 12, bold=True)

    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Add ESC key to exit full screen safely
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

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

        clock.tick(60)

    ser.close()
    pygame.quit()

if __name__ == "__main__":
    main()
