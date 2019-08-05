insmod /root/mchp/wilc-sdio.ko
sleep 5
wpa_supplicant -i wlan0 -D nl80211 -c /etc/wilc_wpa_supplicant.conf &
sleep 2

wpa_cli add_network 0
wpa_cli -p /var/run/wpa_supplicant ap_scan 1
wpa_cli set_network 0 ssid '"wsn"'
wpa_cli set_network 0 key_mgmt WPA-PSK
wpa_cli set_network 0 psk '"brucenegley"'
wpa_cli select_network 0 &
sleep 5
udhcpc -i wlan0 &
sleep 5
dmesg -n1
wpa_cli status
devmem2 0xf8048008 w 0xa5000000
sleep 1
devmem2 0xf8048008
python /root/miwi_network_client_test9.py &

