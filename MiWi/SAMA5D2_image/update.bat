Echo SAMA5D2 firmware update
sam-ba_3.2.1\sam-ba.exe --version
pause
pause
sam-ba_3.2.1\sam-ba.exe -x emmc-usb.qml
pause
sam-ba_3.2.1\sam-ba.exe -p usb -b sama5d2-xplained -a bootconfig -c writecfg:bscr:valid,bureg0
pause
sam-ba_3.2.1\sam-ba.exe -p usb -b sama5d2-xplained -a bootconfig -c writecfg:bureg0:ext_mem_boot,sdmmc1_disabled,sdmmc0,spi1_disabled,spi0_disabled,qspi1_disabled,qspi0_disabled