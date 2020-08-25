The repo contains file for the C64 Mini Commodore computer.

CPU: All Winner A20 ARM7 (sun7i) running 2 cores at ~900mhz
Ram: ~100MB
Storage: Nanda devices (~16MB and ~100MB)

Uses uboot (accessable via onboard UART) (press 's' while booting the device to stop the boot)

Boot sequence:

Load kernel from nanda:boot to 0x40007800
Then boot off this address (using boota)
