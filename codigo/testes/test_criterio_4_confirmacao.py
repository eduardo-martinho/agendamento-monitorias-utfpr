import unittest
from datetime import datetime

from agenda import Agenda, HorarioIndisponivel
from bot import Bot
from testes.auxiliares import AGORA, LIMITES, NOME_CALCULO, adicionar_horario, ir_ate_horarios, montar_repositorio

TELEFONE = "5543999990001"
OUTRO_TELEFONE = "5543999990002"


class TestCriterio4Confirmacao(unittest.TestCase):
    def setUp(self) -> None:
        self.repositorio = montar_repositorio()
        adicionar_horario(self.repositorio, "ana1", "ana", datetime(2026, 10, 21, 14, 30), sala="E203")
        self.agenda = Agenda(self.repositorio)
        self.bot = Bot(self.repositorio, self.agenda)

    def test_reserva_fica_gravada_no_telefone_do_aluno(self) -> None:
        ir_ate_horarios(self.bot, TELEFONE, LIMITES)
        self.bot.responder(TELEFONE, "ana1", AGORA)

        reservas = self.repositorio.reservas_do_aluno(TELEFONE)
        self.assertEqual(len(reservas), 1)
        self.assertEqual(reservas[0].horario, "ana1")
        self.assertEqual(reservas[0].assunto, LIMITES)

    def test_aluno_e_registrado_pelo_telefone_na_primeira_reserva(self) -> None:
        self.assertIsNone(self.repositorio.buscar_aluno(TELEFONE))
        ir_ate_horarios(self.bot, TELEFONE, LIMITES)
        self.bot.responder(TELEFONE, "ana1", AGORA)
        self.assertIsNotNone(self.repositorio.buscar_aluno(TELEFONE))

    def test_confirmacao_traz_disciplina_monitor_dia_horario_e_sala(self) -> None:
        ir_ate_horarios(self.bot, TELEFONE, LIMITES)
        confirmacao = self.bot.responder(TELEFONE, "ana1", AGORA)

        for trecho in [NOME_CALCULO, "Ana Souza", "21/10/2026", "14:30", "E203"]:
            self.assertIn(trecho, confirmacao.texto)

    def test_horario_individual_pego_por_outro_aluno_antes_da_confirmacao_e_recusado(self) -> None:
        ir_ate_horarios(self.bot, TELEFONE, LIMITES)
        self.agenda.reservar(OUTRO_TELEFONE, "ana1", LIMITES, AGORA)

        resposta = self.bot.responder(TELEFONE, "ana1", AGORA)
        self.assertIn("não está mais disponível", resposta.texto)
        self.assertEqual(self.repositorio.reservas_do_aluno(TELEFONE), [])

    def test_agenda_lanca_erro_ao_reservar_horario_individual_ja_ocupado(self) -> None:
        self.agenda.reservar(OUTRO_TELEFONE, "ana1", LIMITES, AGORA)
        with self.assertRaises(HorarioIndisponivel):
            self.agenda.reservar(TELEFONE, "ana1", LIMITES, AGORA)


if __name__ == "__main__":
    unittest.main()
