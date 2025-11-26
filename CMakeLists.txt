# == DO NOT EDIT THE FOLLOWING LINES for the Raspberry Pi Pico VS Code Extension to work ==
if(WIN32)
    set(USERHOME $ENV{USERPROFILE})
else()
    set(USERHOME $ENV{HOME})
endif()
set(sdkVersion 2.2.0)
set(toolchainVersion 14_2_Rel1)
set(picotoolVersion 2.2.0-a4)
set(picoVscode ${USERHOME}/.pico-sdk/cmake/pico-vscode.cmake)
if (EXISTS ${picoVscode})
    include(${picoVscode})
endif()
# ====================================================================================
set(PICO_BOARD pico CACHE STRING "Board type")

cmake_minimum_required(VERSION 3.13)

# Initialize the SDK
include(pico_sdk_import.cmake)

project(reactor_sim C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Initialize the Raspberry Pi Pico SDK
pico_sdk_init()

# Add your executable
add_executable(reactor_sim
    main.c
)

# Link the necessary libraries
target_link_libraries(reactor_sim 
    pico_stdlib
    pico_multicore
    hardware_dma
    hardware_spi
    hardware_pio
    hardware_interp
    hardware_clocks
    hardware_uart
    m              # <--- ADD THIS (Math Library)
)

# Enable USB Output (Crucial for your Python script!)
pico_enable_stdio_usb(reactor_sim 1)
pico_enable_stdio_uart(reactor_sim 0)

# Create the .uf2 file for drag-and-drop
pico_add_extra_outputs(reactor_sim)