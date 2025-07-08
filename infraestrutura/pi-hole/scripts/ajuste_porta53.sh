sudo ss -tuln | grep :53
sudo systemctl disable systemd-resolved
sudo systemctl stop systemd-resolved
sudo systemctl disable dnsmasq
sudo systemctl stop dnsmasq