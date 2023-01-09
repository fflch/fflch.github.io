---
layout: default
title: Virt Manager
parent: Tutoriais
nav_order: 6
---
1. TOC
{:toc}
---

# Instalação do windows 11 no virtmanager

## 0. ATENÇÃO

Esse tutorial é baseado nas seguintes documentações:

- <https://getlabsdone.com/how-to-enable-tpm-and-secure-boot-on-kvm/>
- <https://getlabsdone.com/how-to-install-windows-11-on-kvm/>

Para esse tutorial é necessário ter baixado os dois arquivos: A imagem do disco (ISO) do windows 11 e os drivers do windows 11 (que podem ser respectivamente baixados nos seguintes links:

- <https://www.microsoft.com/pt-br/software-download/windows11> 
- <https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/virtio-win-0.1.215-2/virtio-win-0.1.215.iso>

Para a realização desse tutorial será necessário instalar o virt manager (gerenciador de maquinas virtuais) no seu debian.

## 1. EXECUÇÃO DE LINHAS DE CÓDIGO NO TERMINAL

- Para criar a máquina virtual do windows 11 é necessário, primeiramente executar as seguintes linhas de código no terminal do computador:

```
sudo apt install qemu-kvm bridge-utils virt-manager libosinfo-bin -y
```
- Após isso você precisa se certificar de que as seguintes linhas de código estão presentes no arquivo /etc/apt/sources.list pelo terminal:
```
deb http://deb.debian.org/debian/ bullseye main non-free
```
```
deb http://deb.debian.org/debian bullseye-backports main
```
- E caso você não tenha essas linhas adicionadas é necessário adicionar elas e dentro do diretório /etc/apt executar os seguintes comandos:
```
apt update
```
```
apt upgrade
```
- Após isso será necessário executar o comando:
```
sudo apt install -t bullseye-backports qemu-kvm bridge-utils virt-manager libosinfo-bin swtpm-tools -y
```
- E depois disso você deve executar o comando:
```
sudo apt install ovmf
```
## 2. PROCESSO COM A USANDO A INTERFACE DO GERENCIADOR DE MAQUINAS VIRTUAIS

- Agora iremos criar a máquina virtual no gerenciador de máquinas virtuais! Para começar a criar a sua máquina virtual você deve clicar em “criar uma nova máquina virtual” tal como na imagem abaixo:

![imagem1](/assets/images/virtmanagerImages/f1.png)

- Após isso você deve selecionar a opção de midia de instalação local (imagem ISO ou CDROM)

![imagem2](/assets/images/virtmanagerImages/f2.png)

- Após isso será necessário selecionar as opções tal como na imagem abaixo:

![imagem3](/assets/images/virtmanagerImages/f3.png)

- Você será levado para uma outra tela com configurações de cpu e memória e basta deixar como na imagem abaixo e clicar em avançar.

![imagem4](/assets/images/virtmanagerImages/f4.png)

- O próximo passo após isso será alterar a quantidade de GB da máquina virtual que será criada. Você pode selecionar a quantidade que desejar, mas recomendamos o mínimo de 60. Após selecionar a quantidade de GB de sua máquina você deve clicar em avançar.

![imagem5](/assets/images/virtmanagerImages/f5.png)

- Após isso você precisará selecionar o nome, a opção de personalizar a configuração da instalação e selecionar a rede virtual ‘fflch’ : NAT. E depois disso você deve clicar em avançar

![imagem6](/assets/images/virtmanagerImages/f6.png)

- Após avançar para a tela de personalização da máquina virtual você deve clicar na opção de SATA Disk 1 e no barramento do disco você deve selecionar VirtIO e após isso clicar em aplicar. Observe que o arquivo do ISO selecionado agora deve possuir qcow2 em sua extensão.

![imagem7](/assets/images/virtmanagerImages/f7.png)

- Após isso, você deve clicar em adicionar um novo hardware. O hardware em específico são os gráficos que você deve configurar da maneira como se encontra na imagem abaixo:

![imagem8](/assets/images/virtmanagerImages/f8.png)

- Agora você precisa adicionar um novo hardware, e selecionar a opção de armazenamento e após isso clicar em gerenciar e procurar os drivers do windows 11 previamente instalados no seu computador. E no tipo de dispositivo você precisa selecionar a opção de Dispositivo CDROM e após isso basta clicar em concluir, tal como na imagem abaixo:

![imagem17](/assets/images/virtmanagerImages/f17.png)

- Então agora você deve selecionar nas opções de inicialização e ordenada da seguinte maneira para a inicialização:

![imagem9](/assets/images/virtmanagerImages/f9.png)

- Após isso você deve ir até a opção de CPUs e selecionar na vCPU allocation e selecionar 4. Ainda na mesma tela você deve clicar em topologia e definir manualmente a topologia da CPU configurando um total de 1 soquete, 2 núcleos e 2 threads.

![imagem10](/assets/images/virtmanagerImages/f10.png)

- Agora você deve adicionar um hardware novo chamado TPM com as seguintes configurações:

![imagem11](/assets/images/virtmanagerImages/f11.png)

- Agora você deve clicar em visão geral e selecionar as respectivas opções de chipset e firmware: i440FX e UEFI x86_64: /usr/share/OVMF/OVMF_CODE_4M.fd. E após isso clique em aplicar tal como na imagem abaixo:

![imagem12](/assets/images/virtmanagerImages/f12.png)

- Após isso, você deve clicar em iniciar instalação.

![imagem13](/assets/images/virtmanagerImages/f13.png)

- Depois que você inicializar a sua máquina windows 11, basta que você vá até a configuração da sua máquina virtual e exclua o ISO do windows 11 e clicar em aplicar, como demonstrado abaixo:

![imagem14](/assets/images/virtmanagerImages/f14.png)

- Clicando na opção de mostrar console gráfico, no gerenciador de maquinas virtuais, você será capaz de visualizar a seguinte tela:

![imagem18](/assets/images/virtmanagerImages/f18.png)

- E após clicar em avançar você deve clicar na opção de instalar agora tal como indicado na imagem abaixo:

![imagem19](/assets/images/virtmanagerImages/f19.png)

- Depois de clicar em instalar agora, você será direcionado para a tela de ativação do windows e você precisará selecionar a opção Não tenho a chave do produto e depois clicar em avançar, tal como na imagem abaixo:

![imagem20](/assets/images/virtmanagerImages/f20.png)

- Após clicar em avançar você deve clicar na opção de windows que deseja instalar (no caso desse tutorial foi utilizado o Windows 11 pro) e após isso clicar em avançar:

![imagem21](/assets/images/virtmanagerImages/f21.png)

- Você deve, também, aceitar as condições do contrato e após isso clicar em avançar tal como no exemplo abaixo:

![imagem22](/assets/images/virtmanagerImages/f22.png)

- Após isso você vai se deparar com a seguinte tela e deve, como no exemplo abaixo, selecionar a opção personalizada de instalação:

![imagem23](/assets/images/virtmanagerImages/f23.png)

- Com isso você será levado até a tela onde você precisa selecionar o local onde você irá instalar o windows. Com nenhuma opção de disco disponível você deve clicar em Carregar driver, tal como no exemplo abaixo:

![imagem24](/assets/images/virtmanagerImages/f24.png)

- Após isso você vai se deparar com a seguinte imagem, você precisa clicar em OK para que apareçam a mídias de instalação disponíveis:

![imagem25](/assets/images/virtmanagerImages/f25.png)

- Logo em seguida você precisa selecionar a opção abaixo e clicar em avançar:

![imagem26](/assets/images/virtmanagerImages/f26.png)

- E finalmente basta clicar na opção de "Espaço Não Alocado da Unidade 0" e após isso clicar em avanaçar para concluir o processo de instalação do sistema na maquina virtual.

![imagem27](/assets/images/virtmanagerImages/f27.png)