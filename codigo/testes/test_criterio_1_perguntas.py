import unittest
from datetime import datetime, timedelta
from agenda import Agenda
from bot import Bot
from testes.auxiliares import (
    AGORA,
    LIMITES,
    NOME_CALCULO,
    NOME_POO,
    adicionar_horario,
    codigo_por_titulo,
    codigos,
    ir_ate_dias,
    ir_ate_horarios,
    montar_repositorio,
    titulos,
)

TELEFONE = "5543999990001"


class TestCriterio1Perguntas(unittest.TestCase):
    def setUp(self) -> None:
        self.repositorio = montar_repositorio()
        adicionar_horario(self.repositorio, "h1", "ana", datetime(2026, 10, 20, 14, 0))
        self.bot = Bot(self.repositorio, Agenda(self.repositorio))

    def test_pergunta_campus_curso_disciplina_assunto_dia_e_horario_nessa_ordem(self) -> None:
        mensagem = self.bot.responder(TELEFONE, "oi", AGORA)
        self.assertIn("campus", mensagem.texto.lower())
        self.assertEqual(titulos(mensagem), ["Apucarana", "Londrina"])

        mensagem = self.bot.responder(TELEFONE, codigo_por_titulo(mensagem, "Apucarana"), AGORA)
        self.assertIn("curso", mensagem.texto.lower())
        self.assertEqual(titulos(mensagem), ["Engenharia de Computação", "Engenharia Civil"])

        mensagem = self.bot.responder(TELEFONE, codigo_por_titulo(mensagem, "Engenharia de Computação"), AGORA)
        self.assertIn("disciplina", mensagem.texto.lower())
        self.assertEqual(titulos(mensagem), [NOME_CALCULO, NOME_POO])

        mensagem = self.bot.responder(TELEFONE, codigo_por_titulo(mensagem, NOME_CALCULO), AGORA)
        self.assertIn("assunto", mensagem.texto.lower())
        self.assertEqual(
            titulos(mensagem),
            ["Funções reais de uma variável real", LIMITES, "Derivadas, diferenciais e aplicações"],
        )

        mensagem = self.bot.responder(TELEFONE, codigo_por_titulo(mensagem, LIMITES), AGORA)
        self.assertIn("dia", mensagem.texto.lower())
        self.assertEqual(titulos(mensagem), ["ter 20/10"])

        mensagem = self.bot.responder(TELEFONE, codigo_por_titulo(mensagem, "ter 20/10"), AGORA)
        self.assertIn("horário", mensagem.texto.lower())
        self.assertEqual(codigos(mensagem), ["h1"])

    def test_texto_digitado_e_recusado_e_a_pergunta_se_repete(self) -> None:
        pergunta = self.bot.responder(TELEFONE, "oi", AGORA)
        resposta = self.bot.responder(TELEFONE, "quero Apucarana", AGORA)
        self.assertIn(pergunta.texto, resposta.texto)
        self.assertEqual(resposta.opcoes, pergunta.opcoes)

    def test_opcao_de_uma_lista_antiga_e_recusada_e_a_pergunta_se_repete(self) -> None:
        lista_campus = self.bot.responder(TELEFONE, "oi", AGORA)
        codigo_apucarana = codigo_por_titulo(lista_campus, "Apucarana")
        lista_cursos = self.bot.responder(TELEFONE, codigo_apucarana, AGORA)

        resposta = self.bot.responder(TELEFONE, codigo_apucarana, AGORA)
        self.assertIn(lista_cursos.texto, resposta.texto)
        self.assertEqual(resposta.opcoes, lista_cursos.opcoes)

    def test_depois_da_recusa_a_conversa_continua_da_mesma_etapa(self) -> None:
        pergunta = self.bot.responder(TELEFONE, "oi", AGORA)
        self.bot.responder(TELEFONE, "xyz", AGORA)
        mensagem = self.bot.responder(TELEFONE, codigo_por_titulo(pergunta, "Apucarana"), AGORA)
        self.assertIn("curso", mensagem.texto.lower())

    def test_depois_da_confirmacao_a_proxima_mensagem_recomeca_pelo_campus(self) -> None:
        mensagem = self.bot.responder(TELEFONE, "oi", AGORA)
        for titulo in ["Apucarana", "Engenharia de Computação", NOME_CALCULO, LIMITES, "ter 20/10"]:
            mensagem = self.bot.responder(TELEFONE, codigo_por_titulo(mensagem, titulo), AGORA)
        self.bot.responder(TELEFONE, "h1", AGORA)

        mensagem = self.bot.responder(TELEFONE, "oi de novo", AGORA)
        self.assertIn("campus", mensagem.texto.lower())
        self.assertEqual(titulos(mensagem), ["Apucarana", "Londrina"])


    def test_mais_de_10_dias_mostra_9_e_a_opcao_ver_mais_dias(self) -> None:
        for numero in range(1, 12):
            adicionar_horario(self.repositorio, f"d{numero}", "ana", datetime(2026, 10, 20, 15, 0) + timedelta(days=numero))
        mensagem = ir_ate_dias(self.bot, TELEFONE, LIMITES)
        self.assertEqual(len(mensagem.opcoes), 10)
        self.assertEqual(titulos(mensagem)[0], "ter 20/10")
        self.assertEqual(titulos(mensagem)[-1], "Ver mais dias")

        mensagem = self.bot.responder(TELEFONE, codigo_por_titulo(mensagem, "Ver mais dias"), AGORA)
        self.assertEqual(titulos(mensagem), ["qui 29/10", "sex 30/10", "sáb 31/10"])

    def test_ate_10_dias_aparecem_todos_sem_ver_mais(self) -> None:
        for numero in range(1, 10):
            adicionar_horario(self.repositorio, f"d{numero}", "ana", datetime(2026, 10, 20, 15, 0) + timedelta(days=numero))
        mensagem = ir_ate_dias(self.bot, TELEFONE, LIMITES)
        self.assertEqual(len(mensagem.opcoes), 10)
        self.assertNotIn("Ver mais dias", titulos(mensagem))

    def test_lista_do_dia_mostra_todos_os_horarios_livres_desse_dia(self) -> None:
        adicionar_horario(self.repositorio, "h2", "ana", datetime(2026, 10, 20, 14, 30))
        adicionar_horario(self.repositorio, "h3", "bruno", datetime(2026, 10, 20, 9, 0))
        adicionar_horario(self.repositorio, "outro_dia", "bruno", datetime(2026, 10, 21, 9, 0))
        mensagem = ir_ate_horarios(self.bot, TELEFONE, LIMITES, "ter 20/10")
        self.assertEqual(codigos(mensagem), ["h3", "h1", "h2"])

    def test_curso_sem_monitoria_avisa_e_volta_para_a_lista_de_cursos(self) -> None:
        mensagem = self.bot.responder(TELEFONE, "oi", AGORA)
        mensagem = self.bot.responder(TELEFONE, codigo_por_titulo(mensagem, "Apucarana"), AGORA)
        mensagem = self.bot.responder(TELEFONE, codigo_por_titulo(mensagem, "Engenharia Civil"), AGORA)
        self.assertIn("Ainda não há monitorias cadastradas nesse curso.", mensagem.texto)
        self.assertEqual(titulos(mensagem), ["Engenharia de Computação", "Engenharia Civil"])

    def test_assunto_sem_horario_livre_avisa_e_volta_para_a_lista_de_assuntos(self) -> None:
        mensagem = ir_ate_dias(self.bot, TELEFONE, "Tratamento de exceções", disciplina=NOME_POO)
        self.assertIn("Não há horários livres para esse assunto no momento.", mensagem.texto)
        self.assertEqual(titulos(mensagem), ["Introdução à orientação a objetos", "Tratamento de exceções"])

if __name__ == "__main__":
    unittest.main()
