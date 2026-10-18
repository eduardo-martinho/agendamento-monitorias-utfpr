import unittest
from datetime import timedelta
from agenda import Agenda
from bot import Bot
from testes.auxiliares import AGORA, CALCULO, LIMITES, adicionar_horario, codigos, ir_ate_horarios, montar_repositorio


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

        mensagem = ir_ate_horarios(bot, "5543999990001", LIMITES)
        self.assertEqual(codigos(mensagem), ["livre"])


if __name__ == "__main__":
    unittest.main()
