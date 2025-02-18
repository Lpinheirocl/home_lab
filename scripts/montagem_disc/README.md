# Montagem de Disco

## 1. Verifique se o SSD é Detectado

```bash
lsblk
```

## 2. Primeiro precisamos deixar o sdd acessivel

```bash
sudo mkdir /mnt/ssd
```

## 3. Depois montamos o SSD

```bash
sudo mount /dev/sda1 /mnt/ssd
```

