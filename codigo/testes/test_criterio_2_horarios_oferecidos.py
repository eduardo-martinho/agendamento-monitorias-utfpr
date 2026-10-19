import unittest
from datetime import date, datetime, timedelta
from agenda import Agenda
from bot import Bot
from testes.auxiliares import (
    AGORA,
    CALCULO,
    LIMITES,
    adicionar_horario,
    codigo_por_titulo,
    codigos,
    ir_ate_dias,
    montar_repositorio,
    titulos,
)


def codigos_dos_horarios(agenda: Agenda) -> list[str]:
    return [horario.codigo for horario in agenda.horarios_disponiveis(CALCULO, LIMITES, AGORA)]


class TestCriterio2HorariosOferecidos(unittest.TestCase):
    def setUp(self) -> None:
        self.repositorio = montar_repositorio()
        self.agenda = Agenda(self.repositorio)

    def test_horario_que_comeca_exatamente_1_hora_depois_aparece(self) -> None:
        adicionar_horario(self.repositorio, "h1", "ana", AGORA + timedelta(hours=1))
        self.assertEqual(codigos_dos_horarios(self.agenda), ["h1"])

    def test_horario_que_comeca_em_menos_de_1_hora_nao_aparece(self) -> None:
        adicionar_horario(self.repositorio, "h1", "ana", AGORA + timedelta(minutes=59))
        self.assertEqual(codigos_dos_horarios(self.agenda), [])

    def test_horario_que_ja_passou_nao_aparece(self) -> None:
        adicionar_horario(self.repositorio, "h1", "ana", AGORA - timedelta(days=1))
        self.assertEqual(codigos_dos_horarios(self.agenda), [])

    def test_horario_cancelado_pelo_monitor_nao_aparece(self) -> None:
        adicionar_horario(self.repositorio, "h1", "ana", AGORA + timedelta(days=1), cancelado=True)
        self.assertEqual(codigos_dos_horarios(self.agenda), [])

    def test_horario_de_outra_disciplina_nao_aparece(self) -> None:
        adicionar_horario(self.repositorio, "h1", "carla", AGORA + timedelta(days=1))
        self.assertEqual(codigos_dos_horarios(self.agenda), [])

    def test_horarios_aparecem_em_ordem_de_inicio(self) -> None:
        adicionar_horario(self.repositorio, "tarde", "ana", AGORA + timedelta(hours=6))
        adicionar_horario(self.repositorio, "manha", "bruno", AGORA + timedelta(hours=2))
        self.assertEqual(codigos_dos_horarios(self.agenda), ["manha", "tarde"])

    def test_bot_oferece_so_os_horarios_que_a_agenda_libera(self) -> None:
        adicionar_horario(self.repositorio, "livre", "ana", AGORA + timedelta(days=1))
        adicionar_horario(self.repositorio, "cancelado", "ana", AGORA + timedelta(days=2), cancelado=True)
        adicionar_horario(self.repositorio, "em_cima", "bruno", AGORA + timedelta(minutes=30))
        adicionar_horario(self.repositorio, "poo", "carla", AGORA + timedelta(days=1))
        bot = Bot(self.repositorio, self.agenda)

        mensagem = ir_ate_dias(bot, "5543999990001", LIMITES)
        self.assertEqual(titulos(mensagem), ["ter 20/10"])
        mensagem = bot.responder("5543999990001", codigo_por_titulo(mensagem, "ter 20/10"), AGORA)
        self.assertEqual(codigos(mensagem), ["livre"])

    def test_dia_so_com_horario_cancelado_nao_aparece(self) -> None:
        adicionar_horario(self.repositorio, "ter", "ana", datetime(2026, 10, 20, 14, 0), cancelado=True)
        adicionar_horario(self.repositorio, "qua", "ana", datetime(2026, 10, 21, 14, 0))
        self.assertEqual(self.agenda.dias_disponiveis(CALCULO, LIMITES, AGORA), [date(2026, 10, 21)])

    def test_aparecem_so_os_30_primeiros_dias_com_vaga(self) -> None:
        for numero in range(41):
            inicio = datetime(2026, 10, 20, 14, 0) + timedelta(days=2 * numero)
            adicionar_horario(self.repositorio, f"h{numero}", "ana", inicio, cancelado=numero == 5)
        dias = self.agenda.dias_disponiveis(CALCULO, LIMITES, AGORA)
        self.assertEqual(len(dias), 30)
        self.assertNotIn(date(2026, 10, 30), dias)
        self.assertEqual(dias[-1], date(2026, 12, 19))


if __name__ == "__main__":
    unittest.main()
