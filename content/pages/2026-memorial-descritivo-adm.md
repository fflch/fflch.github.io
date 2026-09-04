---
title: Contratação de serviços especializados de engenharia de telecomunicações e cabeamento estruturado
---

**Órgão/Entidade:** Faculdade de Filosofia, Letras e Ciências Humanas – FFLCH/USP  
**CNPJ da FFLCH:** 63.025.530/0016-90  
**Objeto:** Contratação de empresa especializada para remoção de cabeamento estruturado legado, lançamento de novo cabeamento para 386 pontos de rede, conectorização, identificação, organização e certificação técnica de pontos de rede lógica.  
**Escopo do fornecimento:** Prestação de serviço com fornecimento de mão de obra especializada, ferramentas e equipamentos de certificação.  
**Agendamento para vistoria:** Neli Maximino <ti.fflch@usp.br>

---

## 1. Objetivo do serviço

1.1. O presente documento estabelece as especificações técnicas, exigências operacionais e diretrizes para a contratação de empresa especializada na execução dos serviços de **desinstalação/remoção de cabeamento antigo** e **lançamento de novo cabeamento estruturado para 386 pontos de rede lógica**, incluindo conectorização em ambas as extremidades, identificação, organização em racks e certificação técnica de desempenho ponto a ponto no modelo **link permanente (*permanent link*)**.

1.2. **Caracterização da edificação e mapeamento dos pontos:**
* O prédio da administração possui 2 (dois) pavimentos: térreo e 1º pavimento.
* A sala técnica de telecomunicações (TR - *telecommunications room*) está localizada na área central do pavimento térreo.
* Todo o cabeamento vindo do 1º pavimento desce para a sala TR no térreo por meio de eletrocalhas e tubulações pré-existentes.
* **Pontos mapeados em planta:** Estão oficialmente identificados nas plantas baixas 386 pontos de rede (123 no térreo e 263 no 1º pavimento).
* **Comprimento e metragens aproximadas:** As metragens descritas neste documento e nas plantas oficiais representam **valores aproximados**, servindo como estimativa inicial para o dimensionamento do lançamento de cabos.

| Pavimento / Categoria | Quantidade de pontos | Metragem estimada/aproximada de cabeamento |
| :--- | :---: | :---: |
| **Térreo (mapeado)** | 123 pontos | ~ 3.435,00 m |
| **1º Pavimento (mapeado)** | 263 pontos | ~ 16.225,00 m |
| **Total contratado** | **386 pontos** | **~ 19.660,00 m** |

1.3. A localização e a indicação espacial dos 386 pontos de rede mapeados estão detalhadas nas plantas baixas oficiais do órgão:
* **Plantas e mapeamento técnico:** Térreo [https://rede.fflch.usp.br/plantas/public/15](https://rede.fflch.usp.br/plantas/public/15) e 1º Pavimento [https://rede.fflch.usp.br/plantas/public/14](https://rede.fflch.usp.br/plantas/public/14)

1.4. **Restrição absoluta de escopo e manutenção da infraestrutura existente:**
* O objeto compreende **exclusivamente a substituição do cabeamento estruturado**.
* **Uso exclusivo de caminhos existentes:** Todos os 386 pontos mapeados deverão utilizar **estritamente a infraestrutura física já existente** (eletrodutos, canaletas, eletrocalhas, perfilados e caixas de passagem).
* **Não haverá qualquer alteração, ampliação ou instalação civil/física**: não serão instaladas novas infraestruturas nem realizadas obras civis ou de serralheria. Todos os caminhos físicos existentes serão **100% reaproveitados**.

---

## 2. Escopo dos serviços e divisão de responsabilidades

### 2.1. Dinâmica operacional e faseamento da obra
Tendo em vista que o edifício possui geometria horizontal proeminente e a eletrocalha principal atravessa a edificação de ponta a ponta, a execução da obra será realizada obrigatoriamente de forma **faseada**:

1. **Fase 1:** Interdição de metade do prédio para a remoção dos cabos legados, lançamento e conectorização da nova rede.
2. **Fase 2:** Liberada a primeira metade, a segunda metade do prédio será interditada para a execução dos mesmos procedimentos.

> **Importante:** A contratada deverá adequar seu planejamento operacional a essa dinâmica por etapas, garantindo a proteção das áreas não interditadas e a continuidade parcial do expediente do órgão.

### 2.2. Atribuições e obrigações da contratada
1. **Desinstalação e remoção do cabeamento legado:** Remoção criteriosa do cabeamento antigo situado nas tubulações, canaletas, eletrocalhas e caixas de tomada, preservando a integridade das vias físicas. Os cabos recolhidos deverão ser organizados e entregues ao setor de patrimônio/manutenção da contratante.
2. **Reaproveitamento parcial de conectores:** Durante a fase de desmontagem/montagem, **alguns conectores Cat6 existentes deverão ser preservados e reaproveitados**, conforme orientação prévia da equipe técnica da contratante.
3. **Lançamento do novo cabeamento:** Passagem do novo cabeamento pelas rotas existentes para os 386 pontos, respeitando as taxas de ocupação, tração máxima e raios mínimos de curvatura estabelecidos pelas normas brasileiras da ABNT.
4. **Conectorização e montagem:**
   * Conectorização das tomadas fêmeas RJ-45 (módulos keystone) nas caixas e espelhos dos usuários (ponta remota).
   * Crimpagem e organização dos cabos nos patch panels situados nos racks da sala TR (ponta central).
5. **Identificação e etiquetagem bidirecional detalhada:**
   * **Na extremidade central (Rack / TR):** A contratada é obrigatoriamente responsável por afixar uma etiqueta **atrás do patch panel** (na traseira do painel/cabo), identificando claramente a **SALA/AMBIENTE DE DESTINO** atendido por aquele ponto.
   * **Na extremidade remota (Tomada / Usuário):** A contratada é obrigatoriamente responsável por afixar uma etiqueta **na tomada/espelho da sala**, identificando explicitamente a **SALA TÉCNICA (TR)** de origem e o **PATCH PANEL / PORTA** correspondente no rack.
6. **Certificação técnica e carga no sistema local:**
   * Execução dos testes de certificação ponto a ponto no modo **link permanente (*permanent link*)** em **100% dos pontos executados (386 pontos)**, utilizando equipamento certificador de alta precisão (ex.: Fluke Networks DSX Series ou equivalente) com certificado de calibração válido e atualizado.
   * **Lançamento dos resultados:** A contratada deverá **carregar/alimentar individualmente os dados do resultado da certificação de cada ponto em um sistema local**. Para isso, a contratante fornecerá login, senha e o treinamento básico para acesso ao sistema.

### 2.3. Divisão do fornecimento de materiais e insumos

> **Responsabilidade exclusiva da contratante (fornecimento de materiais):**  
> Todo o material principal de infraestrutura passiva será fornecido integralmente pela FFLCH/USP, incluindo:
> * Cabos de rede UTP novos;
> * Conectores e módulos keystone (RJ-45 fêmea) novos;
> * Patch panels para rack de 19";
> * Caixas de tomada, espelhos e suportes de fixação.

> **Responsabilidade exclusiva da contratada (ferramental, equipamentos e consumíveis):**  
> Caberá à contratada fornecer toda a infraestrutura operacional para execução, incluindo:
> * Equipamento certificador de rede calibrado e acessórios de teste;
> * Ferramental completo (alicates de crimpagem/punch-down, guias passa-cabo, etiquetadoras industriais);
> * Equipamentos para trabalho em altura (escadas industriais, plataformas, andaimes);
> * Insumos secundários de fixação e organização (braçadeiras de nylon/velcro, etiquetas industriais adesivas duráveis e fitas de sinalização).

---

## 3. Segurança e saúde no trabalho (SST)

Devido ao acesso a infraestruturas suspensas e eletrocalhas fixadas no teto, a contratada deverá cumprir rigorosamente a legislação brasileira de segurança do trabalho do Ministério do Trabalho e Emprego (MTE).

> **Aviso de responsabilidade:**  
> A gestão, supervisão e integral responsabilidade civil, trabalhista, acidentária e previdenciária referentes à segurança e saúde no trabalho (SST) de seus colaboradores cabem **exclusivamente à empresa contratada**.

### 3.1. Requisitos obrigatórios de segurança
* **Trabalho em altura (NR-35):** Os profissionais que atuarem em alturas superiores a 2,00 metros (uso de escadas, andaimes ou plataformas) deverão apresentar certificado de treinamento na norma **NR-35** e Atestado de Saúde Ocupacional (ASO) atualizado com aptidão para trabalho em altura.
* **Equipamentos de proteção (EPI/EPC):** Fornecimento e uso obrigatório de EPIs adequados (capacete com jugular, calçado de segurança com biqueira, cinto de segurança tipo paraquedista com talabarte duplo, óculos e luvas). Isolamento e sinalização visual das frentes de trabalho sob as eletrocalhas.
* **Uso de escadas e acessos:** Utilização de escadas industriais com sapatas antiderrapantes e amarração. **É expressamente vedado o uso de improvisos ou apoios inadequados.**
* **Segurança em instalações elétricas (NR-10):** Adoção de procedimentos preventivos em vias compartilhadas ou próximas a circuitos elétricos, em atendimento à **NR-10**.

---

## 4. Certificação da rede e critérios de aceite (entregáveis)

O aceite definitivo dos serviços prestados e a liberação do pagamento ficam condicionados ao atendimento de 100% dos seguintes requisitos:

1. **Certificação em link permanente (*permanent link*):** Todos os **386 pontos de rede executados** deverão ser testados sob o parâmetro de **link permanente**, garantindo a qualidade do lance de cabo e das conexões de fêmea a fêmea sem a interferência dos cordões de manobra.
2. **Alimentação do sistema local:** Inserção/upload dos relatórios de certificação de cada ponto no **sistema local da contratante**, utilizando credenciais de acesso disponibilizadas pela equipe de TI do órgão.
3. **Padrão de etiquetagem verificado:** Validação da correta afixação das etiquetas de identificação cruzada (**atrás do patch panel indicando a sala** e **na tomada da sala indicando a TR e a porta do patch panel**).
4. **Parâmetros de desempenho (pass):** Apresentação de resultado **aprovado (pass) em 100% dos pontos instalados**, em conformidade com as normas ABNT aplicáveis, contemplando:
   * Mapa de fiação (*wiremap*);
   * Comprimento do lance de cabo;
   * Atenuação e perda de inserção;
   * Perda de retorno (*return loss*);
   * Parâmetros de diafonia (*NEXT, PS-NEXT, ELFEXT, PS-ELFEXT*).
5. **Relatório técnico consolidado:** Entrega da documentação técnica completa contendo os arquivos originais dos testes em meio digital (PDF e arquivo nativo do equipamento certificador).

---

## 5. Normas técnicas e legislações de referência

A execução dos serviços e os ensaios de campo deverão obedecer estritamente às edições vigentes das Normas Brasileiras (ABNT) e Regulamentadoras (MTE):

* **ABNT NBR 14565:** Cabeamento estruturado para edifícios comerciais;
* **ABNT NBR 16264:** Cabeamento estruturado – Ensaios no campo;
* **NR-10 (MTE):** Segurança em instalações e serviços em eletricidade;
* **NR-35 (MTE):** Trabalho em altura.