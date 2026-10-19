# 2. Testes de aceitação

História implementada: H1, reservar um horário de monitoria pelo bot. Os testes usam `unittest` e ficam em `codigo/testes/`, um arquivo por critério. Rodam com `py -m unittest discover -s codigo -v` a partir da pasta do projeto, e os 37 passam. Cada teste monta os próprios dados e passa o momento da conversa como parâmetro, então nenhum depende do teclado nem do relógio do computador.

Ao lado de cada teste está o tipo de cenário: sucesso, quando a ação deve dar certo; falha, quando o sistema deve recusar ou esconder alguma coisa; exceção, quando a agenda lança um erro.

## Critério 1. Perguntas na ordem, sempre com lista, e recusa do que não está na lista

Arquivo `test_criterio_1_perguntas.py`.

1. `test_pergunta_campus_curso_disciplina_assunto_dia_e_horario_nessa_ordem` (sucesso)
2. `test_texto_digitado_e_recusado_e_a_pergunta_se_repete` (falha)
3. `test_opcao_de_uma_lista_antiga_e_recusada_e_a_pergunta_se_repete` (falha)
4. `test_depois_da_recusa_a_conversa_continua_da_mesma_etapa` (falha)
5. `test_depois_da_confirmacao_a_proxima_mensagem_recomeca_pelo_campus` (sucesso)
6. `test_mais_de_10_dias_mostra_9_e_a_opcao_ver_mais_dias` (sucesso)
7. `test_ate_10_dias_aparecem_todos_sem_ver_mais` (sucesso)
8. `test_lista_do_dia_mostra_todos_os_horarios_livres_desse_dia` (sucesso)
9. `test_curso_sem_monitoria_avisa_e_volta_para_a_lista_de_cursos` (falha)
10. `test_assunto_sem_horario_livre_avisa_e_volta_para_a_lista_de_assuntos` (falha)

## Critério 2. Só horários da disciplina, não cancelados e com pelo menos 1 hora de antecedência

Arquivo `test_criterio_2_horarios_oferecidos.py`.

1. `test_horario_que_comeca_exatamente_1_hora_depois_aparece` (sucesso, no limite)
2. `test_horario_que_comeca_em_menos_de_1_hora_nao_aparece` (falha)
3. `test_horario_que_ja_passou_nao_aparece` (falha)
4. `test_horario_cancelado_pelo_monitor_nao_aparece` (falha)
5. `test_horario_de_outra_disciplina_nao_aparece` (falha)
6. `test_horarios_aparecem_em_ordem_de_inicio` (sucesso)
7. `test_bot_oferece_so_os_horarios_que_a_agenda_libera` (sucesso, com três horários que não podem aparecer)
8. `test_dia_so_com_horario_cancelado_nao_aparece` (falha)
9. `test_aparecem_so_os_30_primeiros_dias_com_vaga` (sucesso, no limite)

## Critério 3. Horário individual some depois de reservado; em grupo, só para o mesmo assunto e com vaga

Arquivo `test_criterio_3_individual_e_grupo.py`.

1. `test_horario_individual_ja_reservado_nao_aparece` (falha)
2. `test_horario_individual_livre_aparece_para_qualquer_assunto` (sucesso)
3. `test_horario_em_grupo_vazio_aparece_para_qualquer_assunto` (sucesso)
4. `test_horario_em_grupo_com_vaga_aparece_para_o_mesmo_assunto` (sucesso)
5. `test_segundo_aluno_do_mesmo_assunto_consegue_reservar_o_horario_em_grupo` (sucesso)
6. `test_horario_em_grupo_nao_aparece_para_outro_assunto` (falha)
7. `test_horario_em_grupo_lotado_nao_aparece` (falha)

## Critério 4. Reserva gravada no telefone, aluno registrado na primeira reserva e confirmação completa

Arquivo `test_criterio_4_confirmacao.py`.

1. `test_reserva_fica_gravada_no_telefone_do_aluno` (sucesso)
2. `test_aluno_e_registrado_pelo_telefone_na_primeira_reserva` (sucesso)
3. `test_confirmacao_traz_disciplina_monitor_dia_horario_e_sala` (sucesso)
4. `test_horario_individual_pego_por_outro_aluno_antes_da_confirmacao_e_recusado` (exceção, tratada pelo bot)
5. `test_agenda_lanca_erro_ao_reservar_horario_individual_ja_ocupado` (exceção)

## Critério 5. No máximo 2 reservas por disciplina na semana do horário

Arquivo `test_criterio_5_limite_semanal.py`.

1. `test_terceira_reserva_na_mesma_disciplina_e_semana_e_recusada` (exceção)
2. `test_domingo_ainda_conta_na_mesma_semana` (exceção, no limite da semana)
3. `test_reserva_na_semana_seguinte_e_aceita` (sucesso)
4. `test_reserva_em_outra_disciplina_na_mesma_semana_e_aceita` (sucesso)
5. `test_conta_a_semana_do_horario_e_nao_a_da_conversa` (sucesso nas três primeiras reservas, exceção na quarta)
6. `test_bot_explica_o_limite_quando_a_reserva_e_recusada` (falha)

## O que não foi coberto e por quê

O programa principal (`codigo/principal.py`) não tem teste automático, porque só lê o teclado e mostra as mensagens no terminal, sem regra nenhuma. Foi testado à mão, percorrendo a conversa até a confirmação. Os dados de exemplo (`codigo/dados_exemplo.py`) também não têm teste: servem só para a execução manual, e os testes usam dados próprios e menores.

A ligação com o WhatsApp não existe no protótipo, então não há teste de envio e recebimento de mensagens, nem do limite de caracteres que o WhatsApp impõe ao título de cada opção. Também não há teste de duas mensagens chegando ao mesmo tempo: o protótipo roda num processo só, com os dados em memória. O caso parecido que existe, outro aluno pegar o horário enquanto a conversa estava parada, está coberto no critério 4.
