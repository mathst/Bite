<h1 align="center"> Resumo em pr-br </h1>

## Índice 

* [Índice](#índice)
* [Descrição](#descrição)
* [Preparo e Acesso](#preparo)
* [Acesso ao Projeto](#acesso-ao-projeto)
* [Tecnologias utilizadas](#tecnologias-utilizadas)
* [End points](#end points)

## Descrição

<p align="justify">
um teste de logica e um de contrução de api, eu tentei fazer uma implementação com react mas acabou me enrrolando e preferi deixar de fora
</p>

## Preparo e Acesso

:heavy_check_mark: `install python:`  Ter no minimo a versão 3.8 ou posterior do python

:heavy_check_mark: `crie uma env:`  Pse o comando `python3 -m venv env` para poder criar uma env

:heavy_check_mark: `ative uma env:`  Pse o comando `source env/bin/activate` para poder ativar a env

:heavy_check_mark: `instalar os requirements:` Para instalar basta dar um `pip install -r requirements.txt` para instalar as dependencias na env

:heavy_check_mark: `migrate e makemigrations:`python3 manage.py migrate` e depois `python3 manage.py makemigrations`para poder criar e atualizar o DB

:heavy_check_mark: `api:` para rodar a api, basta entrar na pasta api e rodar `python3 manage.py runserver`

##Tecnologias utilizadas

:heavy_check_mark: python3

:heavy_check_mark: django

:heavy_check_mark: django Framework

:heavy_check_mark: sqlite

## End points

` GET - ../veiculos` - tras todos os ceiculos
` GET - ../veiculos/?marca={str:marca}&ano={int:ano}&cor={str:cor}` - filtra os veiculos listados
` GET - ../veiculos/<int:id>` - mostra todods os dados do veiculos
` POST - ../veiculos` - ex:{
  "veiculo": "uno mile",
  "marca": "fiat",
  "cor": "branco",
  "ano": "2020",
  "descricao": "uno com escada em cima e com uma otima velocidade",
  "vendido": "false" ("false" é não vendido e "true" é vendido),
  "created" : " esse campo tem qeu vim vazio pois ele se auto completa",
  "updated" : " esse campo tem qeu vim vazio pois ele se auto completa"

  }
` PATCH - ../veiculos/<int:id>` - ex:{
  "veiculo": "uno mile",
  "marca": "fiat",
  "cor": "branco",
  "ano": "2020",
  "descricao": "uno com escada em cima e com uma otima velocidade",
  "vendido": "false" ("false" é não vendido e "true" é vendido)
  }
  as datas não são alteraveis se não da erro pela formatação
` DELETE - ../veiculos/<int:id> - deleta o veiculo pelo id dele