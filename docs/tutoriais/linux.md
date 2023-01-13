---
layout: default
title: Linux
parent: Tutoriais
nav_order: 6
---
1. TOC
{:toc}
---

*Escrito por Yasmin*

![logo do linux](/assets/images/linux.jpg)

# COMANDOS BÁSICOS DO LINUX


## O que é o Linux?
O Linux é um Sistema Operacional, assim como o Windows e o Mac OS, que possibilita a execução de programas em um computador e outros dispositivos. Um dos seus principais diferenciais em relação aos outros sistemas é que o Linux pode ser livremente modificado e distribuído. Um **comando** Linux é uma interface que aceita linhas de texto e as processa em instruções para o seu computador. Neste tutorial vamos aprender os comandos mais básicos deste sistema operacional e suas respectivas funções. 

## Comandos básicos

- **pwd**

Este comando informa qual em qual diretório o usuário está localizado 

```bash
~ pwd
~ /home/yas
```

- **cd**

Este comando direciona o usuário a algum diretorio. É necessário utilizar *cd* + o nome do direório que deseja entrar

```bash
~ cd Documentos
-> Documentos
```
- **cd ..**

Este comando direciona o usuário para o diretório anterior (*voltar*)

```bash
-> Documentos cd ..
~ 
```

- **mkdir**

Este comando cria um novo diretório. O usuario deve usar *mkdir* + o nome do diretório desejado

```bash
~ mkdir Imagens
```

- **cp**

Este comando copia arquivos e diretórios. Para copiar **arquivos** é necessário utilizar *cp* + arquivo de origem + arquivo de destino:

```bash
~ cp arq_origem.txt arq_destino.txt
```

Para copiar **diretórios inteiros**:

```bash
~ cp -r dir_origem/ dir_destino/
```

- **rm** 

Este comando é utilizado para excluir arquivos e diretórios. Para excluir um **arquivo**:

```bash
~ rm arquivo.txt
```

Para excluir um **diretório vazio**:

```bash
rm -r dir_vazio
```

Para excluir um **diretório com conteúdo**:

```bash
~ rm -rf dir_conteudo
```

- **exit**

Este comando termina uma sessão e sai do terminal

```bash
~ exit
```

- **ls**

Este comando mostra os arquivos e diretórios presentes no diretório em que o usuário está localizado.

```bash
~ ls 
'Área de trabalho' Documentos   Imagens   Música   Downloads
```

- **mv**

Este comando move arquivos

```bash
~ mv linux.jpg Imagens
```

- **passwd**

Este comando altera a senha do usuário

```bash
~ passwd 
Mudando senha para usuário.
Atual senha:
Nova senha:
Redigite a nova senha:
passwd: senha atualizada com sucesso 
```

- **history**

Este comando mostra o histórico de comandos utilizados 

```bash
~ history
1 php -- version
2 cd github
3 ls 
```

- **echo**

Este comando printa no terminal a palavra ou sentença desejada

```bash
~ echo Bom dia!
Bom dia!
```

- **sudo**

Este comando permite que o usuário execute comandos como um superusuário.

```bash
~ sudo apt install debian
```

- **shutdown**

Este comando desliga a sua máquina

```bash
shutdown
```

- **ping**

Este comando testa a conectividade de rede

```bash
ping 127.0.0.0.1
```

- **man**

Este comando exibe um manual do comando desejado. Pode ser utilizado quando o usuário deseja saber o que determinado comando realiza 

```bash
~ man mkdir 
```

- **grep** 

Este comando imprime linhas que combinam padrões, filtra palavras de um documenro de texto, por exemplo

```bash
~ grep "história" relatório.txt
```

- **whoami**

Este comando exibe o nome de usuário em uso

```bash
~ whoami
yas
```

- **whatis**

Este comando exibe uma descrição de uma única linha de qualquer outro comando 

```bash
~ whatis php
php (1)              - PHP Command Line Interface 'CLI'
```

- **wc**

Este comando retorna o número de palavras de algum arquivo de texto

```bash
~ wc linux.txt
  1893  10921 524322 linux.txt
```

- **cat**

Este comando imprime o conteúdo de um arquivo

```bash
cat arquivo.pdf
```

- **vi**

Este comando é um editor de textos no terminal

```bash
~ vi exemplo.txt
```

Para **inserir texto** no documento clique na tecla **insert** do teclado e adicione o texto desejado 
Clique em **esc** no teclado quando as adições estiverem finalizadas
Para **sair e salvar** clique em dois pontos **:** e **wq** 
Para **sair sem salvar** clique em dois pontos **:** e **q!**

## Por fim... 


Este é apenas um tutorial breve dos comando mais básicos do linux, mas que facilitam enormemente a vida de quem utiliza esse sistema operacional. Inicialmente pode parecer difícil lembrar de tantos comandos, mas pratique (ter anotado também facilita muito)! Com a prática constante é apenas uma questão de tempo para que você comece a utilizá-los de forma natural. DICA: tente associar os comandos com a ideia da sua função, por exemplo:

```
wc | word count | comando que conta palavras 
cp | copy | comando que copia diretórios e arquivos 
mkdir | make directory | comando que cria diretórios 
rm | remove | comando que remove arquivos e diretórios 

etc.
```

:)


