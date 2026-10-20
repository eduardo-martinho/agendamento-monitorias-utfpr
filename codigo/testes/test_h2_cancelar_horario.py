import unittest
from datetime import datetime, timedelta
from agenda import Agenda, HorarioDeOutroMonitor, HorarioIndisponivel, HorarioJaComecou, LimiteSemanalAtingido
from testes.auxiliares import AGORA, CALCULO, DERIVADAS, LIMITES, NOME_CALCULO, adicionar_horario, montar_repositorio

TELEFONE = "5543999990001"
OUTRO_TELEFONE = "5543999990002"


class TestH2CancelarHorario(unittest.TestCase):
    def setUp(self) -> None:
        self.repositorio = montar_repositorio()
        self.agenda = Agenda(self.repositorio)
        adicionar_horario(self.repositorio, "ana_qua", "ana", datetime(2026, 10, 21, 14, 0))
        adicionar_horario(self.repositorio, "ana_sex", "ana", datetime(2026, 10, 23, 14, 0))
        adicionar_horario(self.repositorio, "bruno_ter", "bruno", datetime(2026, 10, 20, 18, 0))

    def codigos_disponiveis(self, assunto: str = LIMITES) -> list[str]:
        return [horario.codigo for horario in self.agenda.horarios_disponiveis(CALCULO, assunto, AGORA)]

    # Critério 1
    def test_horario_cancelado_nao_aparece_mais(self) -> None:
        self.agenda.cancelar_horario("ana", "ana_qua", AGORA)
        self.assertNotIn("ana_qua", self.codigos_disponiveis())
        self.assertIn("ana_sex", self.codigos_disponiveis())

    def test_horario_cancelado_nao_pode_ser_reservado(self) -> None:
        self.agenda.cancelar_horario("ana", "ana_qua", AGORA)
        with self.assertRaises(HorarioIndisponivel):
            self.agenda.reservar(TELEFONE, "ana_qua", LIMITES, AGORA)

    # Critério 2
    def test_cada_aluno_com_reserva_recebe_um_aviso(self) -> None:
        self.agenda.reservar(TELEFONE, "bruno_ter", LIMITES, AGORA)
        self.agenda.reservar(OUTRO_TELEFONE, "bruno_ter", LIMITES, AGORA)
        avisos = self.agenda.cancelar_horario("bruno", "bruno_ter", AGORA)
        self.assertEqual(sorted(aviso.telefone for aviso in avisos), [TELEFONE, OUTRO_TELEFONE])

    def test_aviso_traz_disciplina_dia_e_horario_cancelados(self) -> None:
        self.agenda.reservar(TELEFONE, "ana_qua", LIMITES, AGORA)
        aviso = self.agenda.cancelar_horario("ana", "ana_qua", AGORA)[0]
        for trecho in [NOME_CALCULO, "21/10/2026", "14:00", "cancelad"]:
            self.assertIn(trecho, aviso.texto)

    def test_horario_sem_reserva_cancela_sem_aviso(self) -> None:
        self.assertEqual(self.agenda.cancelar_horario("ana", "ana_qua", AGORA), [])

    # Critério 3
    def test_reservas_do_horario_ficam_canceladas_pelo_monitor(self) -> None:
        self.agenda.reservar(TELEFONE, "ana_qua", LIMITES, AGORA)
        self.agenda.cancelar_horario("ana", "ana_qua", AGORA)
        reserva = self.repositorio.reservas_do_aluno(TELEFONE)[0]
        self.assertTrue(reserva.cancelada_pelo_monitor)

    def test_reserva_cancelada_nao_conta_no_limite_semanal(self) -> None:
        adicionar_horario(self.repositorio, "ana_qui", "ana", datetime(2026, 10, 22, 14, 0))
        self.agenda.reservar(TELEFONE, "ana_qua", LIMITES, AGORA)
        self.agenda.reservar(TELEFONE, "ana_sex", LIMITES, AGORA)
        self.agenda.cancelar_horario("ana", "ana_qua", AGORA)
        self.agenda.reservar(TELEFONE, "ana_qui", LIMITES, AGORA)
        self.assertEqual(len(self.repositorio.reservas_do_aluno(TELEFONE)), 3)

    def test_reservas_que_nao_foram_canceladas_continuam_contando(self) -> None:
        adicionar_horario(self.repositorio, "ana_qui", "ana", datetime(2026, 10, 22, 14, 0))
        self.agenda.reservar(TELEFONE, "ana_qua", LIMITES, AGORA)
        self.agenda.reservar(TELEFONE, "ana_sex", LIMITES, AGORA)
        self.agenda.cancelar_horario("bruno", "bruno_ter", AGORA)
        with self.assertRaises(LimiteSemanalAtingido):
            self.agenda.reservar(TELEFONE, "ana_qui", LIMITES, AGORA)

    def test_horario_em_grupo_cancelado_nao_volta_para_outro_assunto(self) -> None:
        self.agenda.reservar(TELEFONE, "bruno_ter", LIMITES, AGORA)
        self.agenda.cancelar_horario("bruno", "bruno_ter", AGORA)
        self.assertNotIn("bruno_ter", self.codigos_disponiveis(DERIVADAS))

    # Critério 4
    def test_monitor_nao_cancela_horario_que_ja_comecou(self) -> None:
        depois_do_inicio = datetime(2026, 10, 21, 14, 10)
        with self.assertRaises(HorarioJaComecou):
            self.agenda.cancelar_horario("ana", "ana_qua", depois_do_inicio)
        self.assertFalse(self.repositorio.buscar_horario("ana_qua").cancelado)

    def test_monitor_cancela_ate_o_minuto_antes_do_inicio(self) -> None:
        um_minuto_antes = datetime(2026, 10, 21, 14, 0) - timedelta(minutes=1)
        self.agenda.cancelar_horario("ana", "ana_qua", um_minuto_antes)
        self.assertTrue(self.repositorio.buscar_horario("ana_qua").cancelado)

    def test_monitor_nao_cancela_horario_de_outro_monitor(self) -> None:
        with self.assertRaises(HorarioDeOutroMonitor):
            self.agenda.cancelar_horario("bruno", "ana_qua", AGORA)
        self.assertFalse(self.repositorio.buscar_horario("ana_qua").cancelado)


if __name__ == "__main__":
    unittest.main()
