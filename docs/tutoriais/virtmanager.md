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

## ATENÇÃO

Esse tutorial é baseado nas seguintes documentações:

- <https://getlabsdone.com/how-to-enable-tpm-and-secure-boot-on-kvm/>
- <https://getlabsdone.com/how-to-install-windows-11-on-kvm/>

 Para esse tutorial é necessário ter baixado os dois arquivos que se encontram na mesma pasta que esse documento, sendo eles: A imagem do disco (ISO) do windows 11 e os drivers do windows 11 (que podem ser respectivamente baixados nos seguintes links:

- <https://www.microsoft.com/pt-br/software-download/windows11> 
- <https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/virtio-win-0.1.215-2/virtio-win-0.1.215.iso>

### PARTE 1: EXECUÇÃO DE LINHAS DE CÓDIGO NO TERMINAL

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
- E caso você não tenha essas linhas adicionadas é necessário adicionar elas e dentro do diretório /etc/apt executar a seguinte comando:
```
apt update
```
- Após isso será necessário executar o comando:
```
sudo apt install -t bullseye-backports qemu-kvm bridge-utils virt-manager libosinfo-bin swtpm-tools -y
```
- E depois disso você deve executar o comando:
```
sudo apt install ovmf
```
### PARTE 2: PROCESSO COM A USANDO A INTERFACE DO GERENCIADOR DE MAQUINAS VIRTUAIS

- Agora iremos criar a máquina virtual no gerenciador de máquinas virtuais! Para começar a criar a sua máquina virtual você deve clicar em “criar uma nova máquina virtual” tal como na imagem abaixo:

![imagem1](/assets/images/virtmanagerImages/f1.png)

- Após isso você deve selecionar a opçãi de midia de instalação local (imagem ISO ou CDROM)

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

- Após isso, você deve clicar em iniciar instalação.

![imagem15](/assets/images/virtmanagerImages/f15.png)

- Depois que você inicializar a sua máquina windows 11, basta que você vá até a configuração da sua máquina virtual e exclua o ISO do windows 11 e clicar em aplicar, como demonstrado abaixo.

![imagem16](/assets/images/virtmanagerImages/f16.png)