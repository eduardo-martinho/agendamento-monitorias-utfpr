import unittest
from datetime import datetime
from agenda import Agenda
from testes.auxiliares import AGORA, CALCULO, DERIVADAS, LIMITES, adicionar_horario, montar_repositorio

INICIO = datetime(2026, 10, 20, 14, 0)


class TestCriterio3IndividualEGrupo(unittest.TestCase):
    def setUp(self) -> None:
        self.repositorio = montar_repositorio()
        self.agenda = Agenda(self.repositorio)

    def codigos_para(self, assunto: str) -> list[str]:
        return [horario.codigo for horario in self.agenda.horarios_disponiveis(CALCULO, assunto, AGORA)]

    def test_horario_individual_ja_reservado_nao_aparece(self) -> None:
        adicionar_horario(self.repositorio, "ana1", "ana", INICIO)
        self.agenda.reservar("5543999990001", "ana1", LIMITES, AGORA)
        self.assertEqual(self.codigos_para(LIMITES), [])

    def test_horario_individual_livre_aparece_para_qualquer_assunto(self) -> None:
        adicionar_horario(self.repositorio, "ana1", "ana", INICIO)
        self.assertEqual(self.codigos_para(LIMITES), ["ana1"])
        self.assertEqual(self.codigos_para(DERIVADAS), ["ana1"])

    def test_horario_em_grupo_vazio_aparece_para_qualquer_assunto(self) -> None:
        adicionar_horario(self.repositorio, "bruno1", "bruno", INICIO)
        self.assertEqual(self.codigos_para(LIMITES), ["bruno1"])
        self.assertEqual(self.codigos_para(DERIVADAS), ["bruno1"])

    def test_horario_em_grupo_com_vaga_aparece_para_o_mesmo_assunto(self) -> None:
        adicionar_horario(self.repositorio, "bruno1", "bruno", INICIO)
        self.agenda.reservar("5543999990001", "bruno1", LIMITES, AGORA)
        self.assertEqual(self.codigos_para(LIMITES), ["bruno1"])

    def test_segundo_aluno_do_mesmo_assunto_consegue_reservar_o_horario_em_grupo(self) -> None:
        adicionar_horario(self.repositorio, "bruno1", "bruno", INICIO)
        self.agenda.reservar("5543999990001", "bruno1", LIMITES, AGORA)
        self.agenda.reservar("5543999990002", "bruno1", LIMITES, AGORA)
        self.assertEqual(len(self.repositorio.reservas_do_horario("bruno1")), 2)

    def test_horario_em_grupo_nao_aparece_para_outro_assunto(self) -> None:
        adicionar_horario(self.repositorio, "bruno1", "bruno", INICIO)
        self.agenda.reservar("5543999990001", "bruno1", LIMITES, AGORA)
        self.assertEqual(self.codigos_para(DERIVADAS), [])

    def test_horario_em_grupo_lotado_nao_aparece(self) -> None:
        adicionar_horario(self.repositorio, "bruno1", "bruno", INICIO)
        self.agenda.reservar("5543999990001", "bruno1", LIMITES, AGORA)
        self.agenda.reservar("5543999990002", "bruno1", LIMITES, AGORA)
        self.assertEqual(self.codigos_para(LIMITES), [])


if __name__ == "__main__":
    unittest.main()
