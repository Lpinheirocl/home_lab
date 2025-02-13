![alt text](image.png)
# PI-Hole
O Pi-Hole serve com um AD block, para Youtube, Twitch e anuncios não desejados.

# configurações

Para configuração do PI-Hole no servidor e bem simples, rode o script [ajuste_porta](./scripts/ajuste_porta53.sh) para configurar a Porta 53 para PI-Hole ter as informações.
Apois isso subo o container do PI-Holee.
Para acessar o PI-Hole basta informa o IP da maquina com "/admin".
> Para alteração da senha do PI-Hole basta executar seguintes comandos
> ```bash 
> docker exec -it pihole sudo pihole -a -p
> ```

