export PATH=$PATH:/Applications/STMicroelectronics/STM32Cube/STM32CubeProgrammer/STM32CubeProgrammer.app/Contents/MacOs/bin/STM32_Programmer_CLI

export PATH=$PATH:/Applications/STMicroelectronics/STM32Cube/STM32CubeProgrammer/STM32CubeProgrammer.app/Contents/MacOs/bin

echo 'export PATH=$PATH:/Applications/STMicroelectronics/STM32Cube/STM32CubeProgrammer/STM32CubeProgrammer.app/Contents/MacOs/bin' >> ~/.zshrc
source ~/.zshrc


## Check DFU Mode
STM32_Programmer_CLI -l usb

STM32CubeProgrammer CLI -c port=usb1 -w firmware.bin 0x08000000 -v -rst
./STM32_Programmer_CLI -c port=usb1 -w firmware.bin 0x08000000 -v -rst

## Check USB
ls /dev/tty.*

