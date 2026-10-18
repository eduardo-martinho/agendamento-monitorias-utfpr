import unittest
from datetime import datetime
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
    montar_repositorio,
    titulos,
)

TELEFONE = "5543999990001"


class TestCriterio1Perguntas(unittest.TestCase):
    def setUp(self) -> None:
        self.repositorio = montar_repositorio()
        adicionar_horario(self.repositorio, "h1", "ana", datetime(2026, 10, 20, 14, 0))
        self.bot = Bot(self.repositorio, Agenda(self.repositorio))

    def test_pergunta_campus_curso_disciplina_assunto_e_horario_nessa_ordem(self) -> None:
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
        for titulo in ["Apucarana", "Engenharia de Computação", NOME_CALCULO, LIMITES]:
            mensagem = self.bot.responder(TELEFONE, codigo_por_titulo(mensagem, titulo), AGORA)
        self.bot.responder(TELEFONE, "h1", AGORA)

        mensagem = self.bot.responder(TELEFONE, "oi de novo", AGORA)
        self.assertIn("campus", mensagem.texto.lower())
        self.assertEqual(titulos(mensagem), ["Apucarana", "Londrina"])


if __name__ == "__main__":
    unittest.main()
