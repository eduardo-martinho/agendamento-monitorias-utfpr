# Projeto inicial

História escolhida: H1, reservar um horário de monitoria pelo bot (prioridade Alta).

## Visão geral

O protótipo implementa a conversa do bot de WhatsApp em Python puro, sem a ligação com o WhatsApp, pois isso exigiria uma chave de API da Meta e um tempo de implementação incompatível com o prazo da atividade. A conversa segue o formato das listas de opções do WhatsApp, como nos bots de agendamento de barbearia: em cada etapa o bot manda uma pergunta com uma lista, e o aluno marca uma das opções em vez de digitar. O bot recebe o telefone do aluno, a opção marcada (ou o texto, se ele digitar mesmo assim) e o momento em que a mensagem chegou, e devolve a próxima pergunta com a lista dela. Como o momento entra junto com a mensagem, os testes conseguem simular qualquer dia e hora sem depender do relógio do computador. Os dados ficam em memória e são montados no começo de cada execução. O protótipo usa só a biblioteca padrão do Python.

O que não faz parte da H1 fica marcado no código com um comentário dizendo o que seria implementado ali futuramente. É o caso do envio e recebimento pelo WhatsApp, do banco de dados, do aviso de cancelamento (H2), da redução do limite por falta (H3) e dos relatórios (H4 e H5).

## Classes e responsabilidades

Modelos. Classes simples de dados, sem regra: campus, curso, disciplina (com a lista fixa de assuntos dela), monitor (com a escolha, feita no cadastro, de atender em grupo ou não e, se atender, quantos alunos cabem por horário), horário (disciplina, monitor, início, sala e se foi cancelado), aluno (identificado pelo telefone) e reserva (horário, aluno e assunto). A duração de 30 minutos é fixa. A mensagem do bot também é um modelo: o texto da pergunta e a lista de opções, cada opção com um código e o título que o aluno vê.

Repositório em memória. Guarda os campus, cursos, disciplinas, horários, alunos e reservas, e responde às consultas que a agenda precisa: os cursos de um campus, as disciplinas de um curso, os horários de uma disciplina e as reservas de um horário ou de um aluno. Mais tarde seria trocado por um banco sem mudar a agenda.

Agenda. Concentra as regras da reserva. Ela lista os horários que um aluno pode reservar numa disciplina para um assunto, num dado momento, aplicando os critérios 2 e 3: horário não cancelado, começando pelo menos 1 hora depois, livre se o monitor atende um aluno por vez, ou com o mesmo assunto e com vaga se o monitor atende em grupo. Também faz a reserva, conferindo tudo de novo (outro aluno pode ter reservado o horário enquanto a conversa estava parada) e o limite de 2 reservas por semana na disciplina (critério 5). Quando a reserva não pode ser feita, a agenda lança um erro próprio que diz o motivo: horário indisponível ou limite semanal atingido. O registro do aluno é criado na primeira reserva (critério 4).

Bot. Conduz a conversa. Guarda, para cada telefone, em que etapa o aluno está (campus, curso, disciplina, assunto ou horário) e o que ele já escolheu. Em cada etapa monta a pergunta com a lista de opções, confere se a resposta é uma das opções da lista atual e, se não for, repete a pergunta com a mesma lista (critério 1). Isso cobre o aluno que digita em vez de marcar e o que marca uma opção de uma lista antiga. Na última etapa pede a reserva à agenda e transforma o resultado em mensagem: a confirmação com disciplina, monitor, dia, horário e sala (critério 4) ou a explicação do erro (critério 5). O bot não decide nenhuma regra de reserva, só pergunta e repassa.

Dados de exemplo. Monta dados próximos dos reais para a execução manual: três campus da UTFPR, entre eles Apucarana, com dois ou três cursos cada; no curso de Engenharia de Computação de Apucarana, as quatro disciplinas citadas no e-mail (Cálculo, Física, POO e Estruturas de Dados), com os assuntos informados no plano de ensino de cada disciplina no portal do aluno, dois ou três monitores (alguns atendem em grupo, outros não) e seus horários.

Programa principal. Simula o WhatsApp no terminal: mostra a pergunta do bot e a lista de opções, e a pessoa escolhe uma delas pelo número, como se tocasse na opção. É a única parte que lê o teclado e não tem regra nenhuma.

## Testes de aceitação

Os testes ficam num arquivo por critério dentro da pasta de testes, com unittest. Cada teste monta seus próprios dados e chama o bot ou a agenda diretamente, sem teclado e sem relógio do computador.

Critério 1, perguntas em ordem e resposta inválida. Um teste percorre a conversa inteira e confere que as perguntas vêm na ordem campus, curso, disciplina, assunto e horário, sempre com uma lista de opções (sucesso). Outro responde com texto digitado e com uma opção que não está na lista atual e confere que o bot recusa e repete a mesma pergunta (falha).

Critério 2, horários oferecidos. Testes conferem que não aparecem o horário cancelado, o horário que começa em menos de 1 hora e o horário de outra disciplina (falha), e que aparece o horário que começa exatamente 1 hora depois (sucesso, no limite).

Critério 3, individual e grupo. Testes conferem que o horário já reservado de um monitor que atende um aluno por vez some, que o horário de um monitor que atende em grupo aparece para o mesmo assunto enquanto há vaga (sucesso), e que não aparece para outro assunto nem quando está lotado (falha).

Critério 4, confirmação. Um teste faz a reserva e confere que ela foi gravada, que o aluno foi registrado pelo telefone e que a mensagem traz disciplina, monitor, dia, horário e sala (sucesso). Outro simula um segundo aluno pegando o horário individual antes da confirmação e confere que a reserva é recusada (exceção).

Critério 5, limite semanal. Um teste confere que a terceira reserva na mesma disciplina e na mesma semana é recusada com a explicação do limite (falha). Outros conferem que a reserva é aceita numa semana diferente e numa disciplina diferente (sucesso).

## Execução

Os testes rodam com o unittest da biblioteca padrão a partir da pasta do projeto, e o programa principal abre a simulação no terminal. Os comandos exatos ficam no relatório de execução.
