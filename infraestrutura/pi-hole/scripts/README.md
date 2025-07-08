# Identificar o processo que está usando a porta 53
```bash
sudo ss -tuln | grep :53
```

# Para systemd-resolved
```bash
sudo systemctl stop systemd-resolved
```

# Para dnsmasq
```bash
sudo systemctl stop dnsmasq
```