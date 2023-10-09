# Guia pratico para usar o git e este repositorio

## Sobre a formatacao deste guia 

Comandos sempre estao entre crases (`), por exemplo: 
`git pull`, ou
```
manim -pql draw_names.py Main
```

## Git 
O Git é um sistema de controle de versão, o que significa que ele ajuda a gerenciar as alterações feitas em arquivos ao longo do tempo. Ele é amplamente utilizado por desenvolvedores de software para acompanhar as mudanças feitas no código-fonte de um projeto.
Imagine que você está trabalhando em um projeto com outras pessoas. Cada vez que você faz uma alteração em um arquivo, o Git registra essa alteração. Ele armazena uma cópia do arquivo no estado atual, permitindo que você volte a qualquer versão anterior, se necessário.

Carrager alteracoes remotas:
```
git pull 
```

Resetar alteracoes:
```
git reset --hard 
```

## Copilar a animacao 
Comandos para compilar a animacao, utilize a opção -pqh para alta qualidade (lembre de lancar de dentro da pasta exemples/):
```
manim -pql draw_names.py Main
manim -pqh draw_names.py Main
```

Adicione a opcao -t para fundo transparente, por exemplo:
```
manim -pql -t draw_names.py Main
```
