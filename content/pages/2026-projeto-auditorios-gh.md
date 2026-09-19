---
title: Proposta de rede na Reforma de recuperação dos auditórios Milton Santos e Nicolau Sevcenko
---

<p align="center">
  <img src="../../assets/2026/auditorios-gh/reforma.svg" alt="Reforma Auditórios" width="100%">
</p>

**Nota Introdutória:**  
A figura apresentada é um recorte da planta oficial e serve como representação ilustrativa da proposta da equipe de TI para os trajetos de cabeamento e o posicionamento das caixas de rede. O desenho não está em escala e não possui o posicionamento executivo exato, devendo ser apreciado pela equipe de Engenharia e incorporado ao projeto executivo da obra.  
 
No esquema gráfico, não foi indicada a posição de subida da eletrocalha até o rack, por se tratar de uma definição de infraestrutura física/civil que transcende o escopo exclusivo de TI.  

Optou-se pela instalação de **2 (dois) pontos de rede por caixa de tomada**, com a finalidade de prover conectividade para Access Points (Wi-Fi), câmeras PTZ, computadores, projetores e outros periféricos.

Ressalta-se que toda a infraestrutura destinada a este projeto — incluindo eletrocalhas, canaletas, eletrodutos e caixas de tomada — é de uso exclusivo para o cabeamento de rede Cat6. Para mitigar riscos de interferência eletromagnética e degradação do sinal, essas vias e caixas não devem, em hipótese alguma, conter circuitos elétricos de potência ou cabos de outros sistemas, como áudio, vídeo (HDMI) e automação.

---

## 1. Descrição Detalhada da Legenda

<table style="width:100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 20px;">
  <thead>
    <tr style="background-color: #f4f6f8; border-bottom: 2px solid #cccccc;">
      <th style="padding: 10px; text-align: center; border: 1px solid #dddddd; width: 8%;">Item</th>
      <th style="padding: 10px; text-align: left; border: 1px solid #dddddd; width: 22%;">Elemento Gráfico</th>
      <th style="padding: 10px; text-align: left; border: 1px solid #dddddd; width: 28%;">Identificação na Legenda</th>
      <th style="padding: 10px; text-align: left; border: 1px solid #dddddd;">Descrição Técnica e Aplicação</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 10px; text-align: center; border: 1px solid #dddddd; font-weight: bold;">1</td>
      <td style="padding: 10px; border: 1px solid #dddddd;">Linha Verde</td>
      <td style="padding: 10px; border: 1px solid #dddddd; font-weight: bold;">Eletrocalha Principal</td>
      <td style="padding: 10px; border: 1px solid #dddddd;">Tronco metálico principal de distribuição do cabeamento estruturado (<em>backbone</em> horizontal). Concentra os cabos vindos do rack principal.</td>
    </tr>
    <tr style="background-color: #fcfcfc;">
      <td style="padding: 10px; text-align: center; border: 1px solid #dddddd; font-weight: bold;">2</td>
      <td style="padding: 10px; border: 1px solid #dddddd;">Linha Azul</td>
      <td style="padding: 10px; border: 1px solid #dddddd; font-weight: bold;">Eletroduto ou Canaleta Aéreo</td>
      <td style="padding: 10px; border: 1px solid #dddddd;">Infraestrutura secundária aérea encarregada de conduzir os cabos da eletrocalha principal até os pontos de rede em altura elevada (Access Points, câmeras PTZ e projetores).</td>
    </tr>
    <tr>
      <td style="padding: 10px; text-align: center; border: 1px solid #dddddd; font-weight: bold;">3</td>
      <td style="padding: 10px; border: 1px solid #dddddd;">Linha Marrom</td>
      <td style="padding: 10px; border: 1px solid #dddddd; font-weight: bold;">Eletroduto ou Canaleta à Meia-Altura</td>
      <td style="padding: 10px; border: 1px solid #dddddd;">Canaleta ou eletroduto instalado na altura de trabalho (aprox. 1,10 m do piso) para atendimento de bancadas e mesas de trabalho.</td>
    </tr>
    <tr style="background-color: #fcfcfc;">
      <td style="padding: 10px; text-align: center; border: 1px solid #dddddd; font-weight: bold;">4</td>
      <td style="padding: 10px; border: 1px solid #dddddd;">Linha Amarela</td>
      <td style="padding: 10px; border: 1px solid #dddddd; font-weight: bold;">Eletroduto ou Canaleta Embutido no Piso</td>
      <td style="padding: 10px; border: 1px solid #dddddd;">Infraestrutura sob o piso para atendimento de pontos localizados na área do palco/piso.</td>
    </tr>
    <tr>
      <td style="padding: 10px; text-align: center; border: 1px solid #dddddd; font-weight: bold;">5</td>
      <td style="padding: 10px; border: 1px solid #dddddd;">Triângulo Laranja (Δ)</td>
      <td style="padding: 10px; border: 1px solid #dddddd; font-weight: bold;">Caixa/Tomada de Rede com 2 Pontos</td>
      <td style="padding: 10px; border: 1px solid #dddddd;">Caixa de tomada (sobrepor ou embutir) contendo <strong>2 conectores fêmea RJ-45 Cat6</strong>.</td>
    </tr>
    <tr style="background-color: #fcfcfc;">
      <td style="padding: 10px; text-align: center; border: 1px solid #dddddd; font-weight: bold;">6</td>
      <td style="padding: 10px; border: 1px solid #dddddd;">Bloco Rosa/Magenta</td>
      <td style="padding: 10px; border: 1px solid #dddddd; font-weight: bold;">Eletroduto ou Canaleta Descida Vertical</td>
      <td style="padding: 10px; border: 1px solid #dddddd;">Elemento de transição (coluna de descida ou caixa de passagem) que realiza o <em>drop</em> vertical da eletrocalha tronco para as derivações secundárias.</td>
    </tr>
  </tbody>
</table>

---

## 2. Quantificação de Caixas, Pontos e Cabos Cat6

* **Total de Caixas de Tomada (2 Pontos cada):** 23 caixas
* **Total de Pontos RJ-45 Cat6:** 23 x 2 = 46 pontos
* **Total de Cabos U/UTP Cat6 a Lançar:** **46 cabos**

---

## 3. Dimensionamento da Eletrocalha Principal (Item 1)

* **Dimensão Recomendada:** **100 x 50 mm** (Largura x Altura)
* **Tipo:** Perfurada, para favorecer a ventilação e proteção mecânica.

Para acomodar o total de **46 cabos Cat6**, a dimensão de 100 x 50 mm atende às diretrizes da norma ABNT NBR 14565. Essa medida mantém a taxa de ocupação inicial em torno de **30%**, ficando abaixo do limite máximo permitido de 40%. Essa folga é indispensável para evitar o esmagamento dos cabos, acomodar as curvas de raio mínimo sem atrito e permitir futuras expansões de rede sem necessidade de troca da infraestrutura principal.
