# Relatório de execução

## Como executar

O protótipo usa Python 3.14 e só a biblioteca padrão (`dataclasses`, `datetime` e `unittest`), sem nada para instalar. O arquivo principal é `codigo/principal.py`. Ele simula o WhatsApp no terminal: mostra a lista de opções do bot, e a pessoa digita o número da opção, ou `sair` para encerrar. Todos os comandos rodam a partir da pasta do projeto. No Windows, o comando é `py`; em outros sistemas, `python3`.

1. Sistema: `py codigo/principal.py`
2. Testes: `py -m unittest discover -s codigo -v`

## Plano e realizado

Trabalho individual: todas as etapas foram feitas por Eduardo Martinho.

1. 16 a 18/10, bot de agendamento (H1). Feito em 17/10, com as histórias de usuário, e em 18/10, com o projeto inicial, os testes de aceitação, a agenda, o bot, os dados de exemplo e o programa principal. Em 19/10 foi corrigido o programa principal, que tinha ficado sem a linha que monta os dados.
2. 19/10, cancelamento de horário e relatório do monitor (H2 e H5). Não implementados (ver mudanças). A documentação técnica e este relatório foram escritos nessa data.
3. 20/10, assunto e atendimento em grupo, dúvidas para o professor. O assunto e o grupo entraram na H1 e foram feitos em 18/10. As dúvidas para o professor (H4) não foram implementadas.
4. 21/10, limite semanal e faltas. O limite de 2 reservas por semana entrou na H1 e foi feito em 18/10. As faltas (H3) não foram implementadas.
5. 22/10, pendências: PDF final, arquivo .zip e autoavaliação.

## Atrasos e mudanças

O plano previa várias funções em 19, 20 e 21/10, mas só a H1 foi implementada, porque é o que o enunciado pede e o prazo não dava para o resto. As outras histórias estão descritas na documentação técnica e marcadas no código com comentários no ponto onde entrariam.

A ligação com o WhatsApp ficou de fora porque exige uma chave da API da Meta e mais tempo do que havia. A conversa foi feita em Python puro, e o terminal faz o papel do WhatsApp.

O bot não aceita texto livre: em cada etapa o aluno marca uma opção de uma lista, como nas listas do WhatsApp. Assim a conversa fica padronizada e o bot não recebe respostas que não entende. Pelo mesmo motivo, o critério 1 da H1 trocou "opções numeradas" por "lista de opções para marcar". Também passou a ser o monitor quem escolhe, no cadastro, se atende em grupo, porque o e-mail diz que só alguns preferem.

Os assuntos de cada disciplina são uma lista fixa, tirada dos planos de ensino de Engenharia de Computação do campus Apucarana. Com a lista fixa, dá para saber quando dois alunos têm a mesma dúvida.

Em 18/10 a escolha do horário virou duas etapas: primeiro o dia, depois o horário desse dia. A lista do WhatsApp aceita no máximo 10 opções, e uma lista única com o semestre todo ficava confusa. A lista de dias mostra os 30 primeiros dias com vaga, e toda lista com mais de 10 opções mostra 9 e a opção "Ver mais". O critério 1 da H1 passou a citar o dia, e os testes já commitados foram ajustados e ganharam 7 casos novos. O projeto inicial ficou como foi registrado.
