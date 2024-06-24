---
layout: default
title: Samba
parent: Tutoriais
nav_order: 6
---
1. TOC
{:toc}
---

# Configurando downloads automáticos de driver de impressora para clientes windows 

## 0. ATENÇÃO

Esse tutorial é baseado nas seguintes documentações:

- <https://wiki.samba.org/index.php/Setting_up_Automatic_Printer_Driver_Downloads_for_Windows_Clients>
- <https://wiki.samba.org/index.php/Configuring_Winbindd_on_a_Samba_AD_DC>

## 1. CRIAÇÃO DA GPO PARA CONFIAR NO SERVIDOR DE IMPRESSÃO

- Uma vez executados todos os comandos no terminal, precisamos criar uma GPO usando a interface de uma maquina windows.

- A versão do windows utilizada para esse tutorial foi o windows 11 versão 22h2.

- Você deve abrir o windows e instalar um programa chamado RSAT (Remote Server Administration Tools) Ferramentas de administração de servidor remoto. Tal como na imagem abaixo:

![imagem5.1](/assets/images/sambaimages/f5.1.png)

- Seleciona a versão desejada, que vai ser a de 64 bits:

![imagem5.2](/assets/images/sambaimages/f5.2.png)

- E após baixar o arquivo execute o programa. E selecione a opção para atualizar versão do windows como na imagem abaixo:

![imagem5.3](/assets/images/sambaimages/f5.3.png)

- E então basta concordar com os termos clicando em aceitar e reiniciar a maquina.

- Após reiniciar a maquina windows você precionar a tecla windows + r e então executar a seguinte linha:

```
secpol.msc
```
![imagem5.4](/assets/images/sambaimages/f5.4.png)

- Após clicar em OK vocẽ vai se deparar com as diversas politicas de segurança local configuradas na sua maquina windows. Você precisará ir até **Politicas Locais** depois em **Opções de segurança** e depois clique em **Controle de Conta de Usuário: Modo de Aprovação de Administrador interno** e marque a opção **Habilitado** tal como no exemplo abaixo:

![imagem5.5](/assets/images/sambaimages/f5.5.png)

- Após ter clicado em em OK você pode fechar a aba com as politicas de segurança da sua maquina.

- Em seguida você vai precisar adicionar o as ferramentas de gerenciamento de politica de grupo baixadas junto com o RSAT. E para isso você vai precisar ir até **Configurações**, depois em **Aplicativos**, logo em seguida **Recursos Opcionais** e em **Adicionar recurso opcional** você deve clicar eR exibir recursos.

- Você deve procurar por **RSAT: Ferramentas de Gerenciamento de Política de Grupo** e clicar em **Avançar** e depois instalar.

![imagem6](/assets/images/sambaimages/f6.png)

- Após isso você deve pesquisar, na barra de pesquisa do windows, pelo programa **Gerenciamento de politica de grupo**

- E em seguida você deve expandir: **Floresta: smbdomain.local.br**, **Domínios** e clicar com o botão direito em **smbdomain.local.br** e selecionar a opção **Criar um GPO neste domínio e fornecer um link para ele aqui...** tal como na imagem abaixo:

![imagem7](/assets/images/sambaimages/f7.png)

- Vocẽ agora deve nomear a GPO como **IMPRESSORAS** e clicar em OK tal como na imagem abaixo:

![imagem8](/assets/images/sambaimages/f8.png)

- Após isso clique com o botão direito na GPO criada e selecione a opção **Editar...**

![imagem9](/assets/images/sambaimages/f9.png)

- Depois disso vai abrir uma janela com o editor de gerenciamento de politica de grupo. E expandindo as opções **Configurações do Computador**, **Políticas**, **Modelos Administrativos** você deve chegar até a aba **Impressoras** tal como na imagem abaixo:

![imagem10](/assets/images/sambaimages/f10.png)

- Agora é necessário que você dê um duplo clique na opção **Restrições ao recurso apontar e imprimir** e selecionar a opção de **Habilitado** e marcar que **os usuários só podem apontar e imprimir nesse servidor**.

- É necessário também adicionar o nome do servidor na opção **inserir os nomes de servidor…**, no caso o nome a ser inserido é: vagrantfirstdc.smbdomain.local.br.

- Após isso também é necessário na opção **Prompts de Segurança** selecionar para as duas opções **Não mostrar aviso ou solicitação de elevação**

- A tela deve ficar como no exemplo abaixo:

![imagem11](/assets/images/sambaimages/f11.png)

- Após clicar em aplicar e depois em OK é necessário que se abra a janela de **Recurso apontar e imprimir - servidores aprovados**.

- E depois você precisa selecionar a opção habilitado e clicar na opção **Mostrar...** tal como na imagem abaixo:

![imagem12](/assets/images/sambaimages/f12.png)

- Depois de clicar em **Mostrar...** aparecerá uma janela onde você precisa inserir o nome do servidor que no caso é o mesmo que foi inserido anteriormente e que está na imagem abaixo:

![imagem13](/assets/images/sambaimages/f13.png)

- Após inserir o indereço do servidor, basta clicar em OK e depois em OK novamente.

- Você deverá habilitar um novo template administrativo chamado **Limita a instalação do driver de impressão aos administradores**. E após isso selecionar a opção de **Desabilitado** tal como na imagem abaixo. E clicar em **Aplicar** e finalmente em **OK**.

![imagem13.1](/assets/images/sambaimages/f13.1.png)

- Após isso você deve esperar até que os membros do domínio do Windows apliquem a politica de grupo automáticamente.

- Caso você precise aplicar essa politica manualmente basta reiniciar o membro do domínio e executar o seguinte comando com as permissões de administrador local:
```
gpupdate /force /target:computer
```
## 1.1 CRIAÇÃO DE OUTRA GPO GPO PARA CONSEGUIR FAZER VIZUALIZAR AS IMPRESSORAS DO SERVIDOR

- Agora será necessário criar uma nova gpo e habilitar apenas uma politica.

- Então repita o mesmo processo dos passos anteriores para a criação da GPO **IMPRESSORAS**. Contudo ao invés de **IMPRESSORAS** adicione o nome **FIXRPX** como no exemplo.

![imagem13.2](/assets/images/sambaimages/f13.2.png)

- Após isso você deve Editar a politica habilitando o template de **Definir configurações de conexão RPC** e selecionando a opção de **RPC sobre pipes nomeados** em **Protocolo a ser usado para conexões RPC de saída:** e a opção **Padrão** em **Use a autenticação para conexões RPC de saída**. E após isso clique em **Aplicar** e depois em **OK**.

## 2. CONECTAR AO SERVIDOR DE IMPRESSÃO USANDO O CONSOLE DE GERENCIAMENTO DE IMPRESSÃO

- Vocẽ precisa agora abrir a ferramenta **gerenciamento de impressão** e para fazer isso basta pesquisar o nome da ferramenta na barra de pesquisa do windows.

- Uma vez aberta a ferramenta você pode agora clicar com o botão direito em **Servidores de Impressão** e selecionar a opção **Adicionar ou Remover Servidores** tal como na imagem abaixo:

![imagem14](/assets/images/sambaimages/f14.png)

- Após isso nas configurações do gerenciamento de impressão você vai adicionar o servidor samba: vagrantfirstdc.smbdomain.local.br e depois clicar em **adicionar a lista** como na imagem abaixo:

![imagem15](/assets/images/sambaimages/f15.png)

- Na mesma janela, remova os servidores previamente existentes, como na imagem abaixo:

![imagem16](/assets/images/sambaimages/f16.png)

- Após isso basta clicar em OK.

## 3. CARREGAR UM DRIVER DE IMPRESSORA PARA UM SERVIDOR DE IMPRESSÃO SAMBA

- Agora você deve expandir a aba de **gerenciamento de impressão**, **Servidores de impressão**, **vagrantfirstdc.smbdomain.local.br** e depois clicar com o botão direito em **Driver** e selecionar a opção **Adicionar Driver...** tal como na imagem abaixo:

![imagem17](/assets/images/sambaimages/f17.png)

- Na janela **Assistente para se adicionar Driver** é necessário clicar em avançar, certificar-se de marcar a opção X64, clicar em avançar e clicar em **Com Disco**.

- Após isso é necessário localizar o arquivo .inf da impressora e clicar em OK.

- E finalmente selecionar o modelo e clicar em avançar e em concluir.

## 4. ATRIBUIR UM DRIVER A UMA IMPRESSORA

- Ainda em **Gerenciamento de Impressão**, expandindo **Servidores**, **vagrantfirstdc.smbdomain.local.br**. Clique em **Impressoras** e com o botão direito clique novamente na impressora a qual será atribuído o driver previamente carregado selecionando a opção **propriedades**:

![imagem18](/assets/images/sambaimages/f18.png)

- No PopUp que se abre em seguida clique em não como no exemplo abaixo:

![imagem19](/assets/images/sambaimages/f19.png)

- Agora nas propriedades da impressora selecionada, navegue até  a aba **Avançado** e em **Driver**, selecione o driver que foi anteriormente carregado e clique em ok.

![imagem20](/assets/images/sambaimages/f20.png)

- Aparecerá a seguinte mensagem a qual você deve clicar em ok:

![imagem21](/assets/images/sambaimages/f21.png)

- Após isso o windows vai renomear automaticamente a sua impressora. Mas é importante que o nome dela seja o mesmo que apareça no arquivo /etc/samba/smb.conf: 

![imagem21.1](/assets/images/sambaimages/f21.1.png)

- Para isso você precisará apenas renomear o nome da impressora na ferramenta de gerenciamento de impressão e após renomear aparecerá a seguinte mensagem ao qual você precisar selecionar sim tal como no exemplo abaixo:

![imagem22](/assets/images/sambaimages/f22.png)

## 5. IMPLANTAÇÃO AUTOMÁTICA DE IMPRESSORAS:

- No **editor de Gerenciamento de Política de grupo** você precisa clicar em **configurações do Windows** como na imagem abaixo:

![imagem23](/assets/images/sambaimages/f23.png)

- E após clicar em **configurações do windows**, uma série de opções ficarão disponíveis e você deve clicar com o botão direito na **impressoras implantadas** e selecionar a opção **implantar impressora**. Tal como na foto abaixo:

![imagem24](/assets/images/sambaimages/f24.png)

- Logo em seguida aparecerá a seguinte tela, na qual você deve adicionar o endereço da impressora que você deseja que seja disponibilizada automaticamente, após entrar como membro do domínio.

![imagem25](/assets/images/sambaimages/f25.png)

- Após isso basta clicar em **adicionar** e depois clicar em **OK**. E Após isso a tela vai ficar dessa maneira:

![imagem26](/assets/images/sambaimages/f26.png)

- Agora, basta reiniciar o computador e após isso quando pesquisadas na aba de impressoras do windows por **Impressoras e Scanners** irão aparecer todas as impressoras que você implantou.