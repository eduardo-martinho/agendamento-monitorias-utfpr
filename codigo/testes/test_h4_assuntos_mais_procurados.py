import unittest
from datetime import date, datetime

from agenda import Agenda
from modelos import FALTA, FALTA_JUSTIFICADA, PRESENTE, Professor
from relatorios import DisciplinaDeOutroProfessor, PeriodoInvalido, Relatorios
from testes.auxiliares import AGORA, CALCULO, DERIVADAS, LIMITES, POO, adicionar_horario, montar_repositorio

FUNCOES = "Funções reais de uma variável real"
ALUNO_A = "5543999990001"
ALUNO_B = "5543999990002"
ALUNO_C = "5543999990003"
DEPOIS = datetime(2026, 10, 31, 8, 0)


class TestH4AssuntosMaisProcurados(unittest.TestCase):
    def setUp(self) -> None:
        self.repositorio = montar_repositorio()
        self.repositorio.adicionar_professor(Professor("marcos", "Marcos Oliveira"))
        self.repositorio.adicionar_professor(Professor("lucia", "Lúcia Ramos"))
        self.repositorio.buscar_disciplina(CALCULO).professor = "marcos"
        self.repositorio.buscar_disciplina(POO).professor = "lucia"
        self.agenda = Agenda(self.repositorio)
        self.relatorios = Relatorios(self.repositorio)

        self.atender("ana_ter", "ana", datetime(2026, 10, 20, 14, 0), [(ALUNO_A, LIMITES, PRESENTE)])
        self.atender("ana_qua", "ana", datetime(2026, 10, 21, 14, 0), [(ALUNO_A, LIMITES, PRESENTE)])
        self.atender(
            "bruno_qui",
            "bruno",
            datetime(2026, 10, 22, 18, 0),
            [(ALUNO_B, DERIVADAS, PRESENTE), (ALUNO_C, DERIVADAS, FALTA)],
        )
        self.atender("ana_ter2", "ana", datetime(2026, 10, 27, 14, 0), [(ALUNO_B, LIMITES, PRESENTE)])
        self.atender("ana_qua2", "ana", datetime(2026, 10, 28, 14, 0), [(ALUNO_C, FUNCOES, FALTA_JUSTIFICADA)])
        self.atender("ana_qui2", "ana", datetime(2026, 10, 29, 14, 0), [(ALUNO_A, FUNCOES, None)])

    def atender(self, codigo: str, monitor: str, inicio: datetime, alunos: list[tuple[str, str, str | None]]) -> None:
        """Cria o horário, faz as reservas e marca o comparecimento de cada aluno."""
        adicionar_horario(self.repositorio, codigo, monitor, inicio)
        for telefone, assunto, situacao in alunos:
            self.agenda.reservar(telefone, codigo, assunto, AGORA)
            if situacao is not None:
                self.agenda.registrar_comparecimento(monitor, codigo, telefone, situacao, DEPOIS)

    def contagem(self, inicio: date, fim: date) -> list[tuple[str, int]]:
        return self.relatorios.assuntos_mais_procurados("marcos", CALCULO, inicio, fim)

    # Critério 1
    def test_lista_cada_assunto_do_mais_para_o_menos_procurado(self) -> None:
        self.assertEqual(
            self.contagem(date(2026, 10, 19), date(2026, 10, 31)),
            [(LIMITES, 3), (DERIVADAS, 1), (FUNCOES, 0)],
        )

    def test_empate_segue_a_ordem_do_plano_de_ensino(self) -> None:
        self.assertEqual(
            self.contagem(date(2026, 10, 22), date(2026, 10, 27)),
            [(LIMITES, 1), (DERIVADAS, 1), (FUNCOES, 0)],
        )

    # Critério 2
    def test_falta_e_falta_justificada_nao_contam(self) -> None:
        contagem = dict(self.contagem(date(2026, 10, 28), date(2026, 10, 28)))
        self.assertEqual(contagem[FUNCOES], 0)

    def test_reserva_sem_presenca_marcada_nao_conta(self) -> None:
        contagem = dict(self.contagem(date(2026, 10, 29), date(2026, 10, 29)))
        self.assertEqual(contagem[FUNCOES], 0)

    def test_so_conta_atendimentos_dentro_do_periodo(self) -> None:
        self.assertEqual(
            self.contagem(date(2026, 10, 19), date(2026, 10, 25)),
            [(LIMITES, 2), (DERIVADAS, 1), (FUNCOES, 0)],
        )

    def test_periodo_inclui_o_dia_inicial_e_o_final(self) -> None:
        contagem = dict(self.contagem(date(2026, 10, 20), date(2026, 10, 21)))
        self.assertEqual(contagem[LIMITES], 2)

    def test_data_final_antes_da_inicial_e_recusada(self) -> None:
        with self.assertRaises(PeriodoInvalido):
            self.contagem(date(2026, 10, 25), date(2026, 10, 19))

    # Critério 3
    def test_professor_nao_ve_disciplina_de_outro_professor(self) -> None:
        with self.assertRaises(DisciplinaDeOutroProfessor):
            self.relatorios.assuntos_mais_procurados("lucia", CALCULO, date(2026, 10, 19), date(2026, 10, 31))

    def test_professor_ve_so_as_proprias_disciplinas(self) -> None:
        disciplinas = self.relatorios.disciplinas_do_professor("marcos")
        self.assertEqual([disciplina.codigo for disciplina in disciplinas], [CALCULO])


if __name__ == "__main__":
    unittest.main()
