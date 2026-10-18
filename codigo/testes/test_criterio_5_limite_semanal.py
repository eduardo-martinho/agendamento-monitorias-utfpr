import unittest
from datetime import datetime
from agenda import Agenda, LimiteSemanalAtingido
from bot import Bot
from testes.auxiliares import AGORA, LIMITES, NOME_POO, adicionar_horario, ir_ate_horarios, montar_repositorio

TELEFONE = "5543999990001"


class TestCriterio5LimiteSemanal(unittest.TestCase):
    def setUp(self) -> None:
        self.repositorio = montar_repositorio()
        self.agenda = Agenda(self.repositorio)
        adicionar_horario(self.repositorio, "seg", "ana", datetime(2026, 10, 19, 14, 0))
        adicionar_horario(self.repositorio, "qua", "ana", datetime(2026, 10, 21, 14, 0))
        adicionar_horario(self.repositorio, "sex", "ana", datetime(2026, 10, 23, 14, 0))
        adicionar_horario(self.repositorio, "dom", "ana", datetime(2026, 10, 25, 23, 30))
        adicionar_horario(self.repositorio, "seg_seguinte", "ana", datetime(2026, 10, 26, 0, 0))
        adicionar_horario(self.repositorio, "qua_seguinte", "ana", datetime(2026, 10, 28, 14, 0))
        adicionar_horario(self.repositorio, "sex_seguinte", "ana", datetime(2026, 10, 30, 14, 0))
        adicionar_horario(self.repositorio, "poo", "carla", datetime(2026, 10, 22, 10, 0))

    def reservar(self, horario: str, assunto: str = LIMITES) -> None:
        self.agenda.reservar(TELEFONE, horario, assunto, AGORA)

    def test_terceira_reserva_na_mesma_disciplina_e_semana_e_recusada(self) -> None:
        self.reservar("seg")
        self.reservar("qua")
        with self.assertRaises(LimiteSemanalAtingido):
            self.reservar("sex")
        self.assertEqual(len(self.repositorio.reservas_do_aluno(TELEFONE)), 2)

    def test_domingo_ainda_conta_na_mesma_semana(self) -> None:
        self.reservar("seg")
        self.reservar("qua")
        with self.assertRaises(LimiteSemanalAtingido):
            self.reservar("dom")

    def test_reserva_na_semana_seguinte_e_aceita(self) -> None:
        self.reservar("seg")
        self.reservar("qua")
        self.reservar("seg_seguinte")
        self.assertEqual(len(self.repositorio.reservas_do_aluno(TELEFONE)), 3)

    def test_reserva_em_outra_disciplina_na_mesma_semana_e_aceita(self) -> None:
        self.reservar("seg")
        self.reservar("qua")
        self.reservar("poo", "Tratamento de exceções")
        self.assertEqual(len(self.repositorio.reservas_do_aluno(TELEFONE)), 3)

    def test_conta_a_semana_do_horario_e_nao_a_da_conversa(self) -> None:
        self.reservar("qua_seguinte")
        self.reservar("sex_seguinte")
        self.reservar("qua")
        with self.assertRaises(LimiteSemanalAtingido):
            self.reservar("seg_seguinte")

    def test_bot_explica_o_limite_quando_a_reserva_e_recusada(self) -> None:
        self.reservar("seg")
        self.reservar("qua")
        bot = Bot(self.repositorio, self.agenda)

        ir_ate_horarios(bot, TELEFONE, LIMITES)
        resposta = bot.responder(TELEFONE, "sex", AGORA)
        self.assertIn("limite de 2 reservas por semana", resposta.texto)
        self.assertEqual(len(self.repositorio.reservas_do_aluno(TELEFONE)), 2)


if __name__ == "__main__":
    unittest.main()
