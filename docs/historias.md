# 1. Histórias de usuário

O sistema agenda as monitorias da UTFPR, e o aluno usa tudo por um bot de WhatsApp. Os tipos de usuário são aluno, monitor, professor e coordenação. Cada atendimento dura 30 minutos. No cadastro, cada monitor escolhe se atende em grupo: quem não atende recebe um aluno por horário, e quem atende diz quantos alunos cabem em cada horário dele.

## H1. Reservar um horário de monitoria pelo bot

Como aluno, eu quero escolher pelo bot o campus, o curso, a disciplina e o assunto da minha dúvida e reservar um horário livre para ser atendido sem precisar combinar com o monitor por mensagem.

Critérios de aceitação:
1. O bot pergunta campus, curso, disciplina, assunto e horário, nessa ordem, sempre com uma lista de opções para marcar, como as listas do WhatsApp. Se a resposta não for uma das opções da lista, o bot recusa e repete a pergunta.
2. O bot só oferece horários da disciplina escolhida que não foram cancelados pelo monitor e que começam pelo menos 1 hora depois do momento da conversa.
3. Se o monitor atende um aluno por vez, o horário que já tem reserva não aparece. Se ele atende em grupo, o horário que já tem reserva só aparece para quem escolheu o mesmo assunto, e só enquanto houver vaga.
4. Quando o aluno escolhe o horário, a reserva fica gravada no telefone dele (o registro do aluno é criado na primeira reserva) e o bot confirma a disciplina, o monitor, o dia, o horário e a sala.
5. Se o aluno já tem 2 reservas na mesma disciplina na semana do horário (de segunda a domingo), ele não consegue reservar outra nessa semana e o bot explica o limite.

Prioridade: Alta. Resolve o problema principal do e-mail, que são horários lotados enquanto outros ficam vazios, e a coordenação diz que só a reserva funcionando já ajuda muito.

Trecho do e-mail: "A ideia é que o aluno escolha a disciplina, veja os horários livres e reserve um atendimento." e "Se a reserva de horários funcionar, já ajuda muito."

## H2. Cancelar um horário e avisar quem reservou

Como monitor, eu quero cancelar um horário em que não vou poder atender para que ninguém mais reserve e quem já reservou fique sabendo antes de ir até a sala.

Critérios de aceitação:
1. Depois de cancelado, o horário não aparece mais no bot.
2. Cada aluno que tinha reserva nesse horário recebe uma mensagem no WhatsApp com a disciplina, o dia e o horário cancelados.
3. As reservas desse horário passam a constar como canceladas pelo monitor e não contam no limite semanal do aluno.
4. O monitor não consegue cancelar um horário que já começou.

Prioridade: Alta. É a outra reclamação que os alunos fazem no e-mail. Sem o aviso, o aluno que reservou pela H1 continua indo até a sala para descobrir que não vai ter atendimento.

Trecho do e-mail: "às vezes precisa cancelar por causa de prova. Os alunos reclamam que só descobrem o cancelamento quando chegam na sala."

## H3. Registrar presença e falta

Como monitor, eu quero marcar presença ou falta em cada reserva para que quem falta sem justificativa perca reservas e os horários não fiquem perdidos.

Critérios de aceitação:
1. Só dá para marcar presença ou falta em reservas de horários que já começaram.
2. Depois da primeira falta sem justificativa, o aluno só pode reservar 1 horário por semana naquela disciplina.
3. Depois da segunda falta sem justificativa, o aluno não consegue mais reservar naquela disciplina até o fim do semestre, e o bot avisa o motivo quando ele tenta.
4. Falta marcada como justificada não diminui o limite.

Prioridade: Média. Ajuda com os horários perdidos, mas nem os monitores concordam com o bloqueio. Por isso a regra primeiro reduz o limite e só depois bloqueia, e pode entrar depois que a reserva já estiver em uso.

Trecho do e-mail: "Quando o aluno reserva e não aparece, o horário fica perdido. Alguns monitores sugeriram bloquear quem falta muito, mas outros acham isso exagerado."

## H4. Ver os assuntos que geram mais dúvidas

Como professor, eu quero ver os assuntos com mais atendimentos nas minhas disciplinas em um período para reforçar esses conteúdos em aula.

Critérios de aceitação:
1. A lista mostra cada assunto e quantos atendimentos teve, do mais procurado para o menos procurado.
2. Só contam os atendimentos com presença marcada, entre a data inicial e a final escolhidas.
3. O professor só vê os dados das disciplinas pelas quais é responsável.

Prioridade: Baixa. É útil para as aulas, mas não resolve nada do agendamento, e só tem dados depois que a H1 e a H3 estiverem funcionando.

Trecho do e-mail: "Os professores das disciplinas gostariam de saber quais conteúdos geram mais dúvidas, para reforçar em aula."

## H5. Relatório mensal de horas do monitor

Como coordenação do curso, eu quero receber o relatório mensal com as horas atendidas por cada monitor para calcular o pagamento da bolsa.

Critérios de aceitação:
1. Cada horário com pelo menos um aluno presente conta 30 minutos, uma vez só, mesmo quando é em grupo.
2. Horários cancelados, ou em que todos os alunos faltaram, não contam.
3. O relatório é de um mês escolhido e mostra, para cada monitor, o total de horas e a lista dos atendimentos.
4. O monitor só consegue gerar o próprio relatório, a coordenação consegue gerar o de todos, e o bot nunca mostra horas nem valores de bolsa.

Prioridade: Média. A bolsa depende dele, mas o relatório é mensal e hoje já é feito de outro jeito. Também depende da reserva e da presença, então vem depois delas.

Trecho do e-mail: "A coordenação precisa de um relatório mensal com as horas atendidas por cada monitor, porque isso conta para o pagamento da bolsa. Essas informações de bolsa não podem ficar visíveis para todo mundo."
