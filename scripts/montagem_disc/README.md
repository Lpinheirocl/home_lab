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

## 4. Verificar UUID do SSD

```bash
sudo blkid
```

## 5. Montagem automatica 
incluir o valor do UUID e depois salvar, depois reiniciar a maquina

```bash
sudo nano /etc/fstab
```

## 6. Depois montamos o disco para user usar do SSD
Montagem da pasta e depois passa os arquivos

```bash
mkdir /mnt/ssd/seu_usuario
mv /home/seu_usuario/* /mnt/ssd/seu_usuario/
```
Depois criamos o link simbolico
```bash
ln -s /mnt/ssd/seu_usuario /home/seu_usuario
```

