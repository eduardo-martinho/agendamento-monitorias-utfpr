# Relatório de execução

## Como executar

O protótipo usa Python 3.14 e só a biblioteca padrão (`dataclasses`, `datetime` e `unittest`), sem nada para instalar. O arquivo principal é `codigo/principal.py`. Ele abre um menu para entrar como aluno, monitor, professor ou coordenação. Como aluno, o terminal simula o WhatsApp: a pessoa digita o número da opção da lista do bot, e `sair` volta ao menu. Nas outras telas, `0` volta. Os comandos rodam a partir da pasta do projeto. No Windows o comando é `py`; em outros sistemas, `python3`.

1. Sistema: `py codigo/principal.py`
2. Testes: `py -m unittest discover -s codigo -v` (85 testes, 37 deles da H1)

## Plano e realizado

Trabalho individual: todas as etapas foram feitas por Eduardo Martinho.

1. 16 a 18/10, bot de agendamento (H1). Histórias em 17/10; projeto inicial, testes e código em 18/10. Em 19/10 foi corrigido o programa principal, que tinha ficado sem a linha que monta os dados.
2. 19/10, cancelamento de horário e relatório do monitor. Documentação técnica, relatório e cancelamento com aviso aos alunos (H2) feitos em 19/10. O relatório de horas (H5) ficou para 21/10.
3. 20/10, assunto e atendimento em grupo, dúvidas para o professor. O assunto e o grupo entraram na H1 em 18/10. Os assuntos mais procurados (H4) foram feitos em 20/10.
4. 21/10, limite semanal e faltas. O limite de 2 reservas por semana entrou na H1 em 18/10, e presença e faltas (H3) foram antecipadas para 20/10. Em 21/10 foram feitos o relatório de horas (H5) e as telas do monitor, do professor e da coordenação.
5. 22/10, pendências: PDF final, arquivo .zip e autoavaliação, adiantados para 21/10.

## Atrasos e mudanças

A H1 é a história implementada para a avaliação. As outras quatro também foram implementadas, cada uma com testes próprios, mas sem projeto inicial, porque o enunciado pede projeto só da história escolhida. O relatório de horas atrasou dois dias em relação ao plano.

A ligação com o WhatsApp ficou de fora porque exige uma chave da API da Meta e mais tempo do que havia. O terminal faz o papel do WhatsApp, e o código marca com comentários onde entrariam o envio das mensagens, o login e o banco de dados.

O bot não aceita texto livre: em cada etapa o aluno marca uma opção de uma lista, como nas listas do WhatsApp, e o bot não recebe respostas que não entende. Por isso o critério 1 da H1 trocou "opções numeradas" por "lista de opções para marcar". Também passou a ser o monitor quem escolhe, no cadastro, se atende em grupo, porque o e-mail diz que só alguns preferem. Os assuntos de cada disciplina são uma lista fixa, tirada dos planos de ensino de Engenharia de Computação de Apucarana, para dar para saber quando dois alunos têm a mesma dúvida.

Em 18/10 a escolha do horário virou duas etapas, primeiro o dia e depois o horário desse dia, porque a lista do WhatsApp aceita no máximo 10 opções e uma lista única com o semestre todo ficava confusa. A lista de dias mostra os 30 primeiros dias com vaga, e toda lista com mais de 10 opções mostra 9 e "Ver mais". O critério 1 da H1 passou a citar o dia, e os testes já commitados foram ajustados e ganharam 7 casos.
