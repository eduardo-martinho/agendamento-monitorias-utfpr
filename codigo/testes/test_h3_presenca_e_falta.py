import unittest
from datetime import datetime
from agenda import (
    Agenda,
    DisciplinaBloqueada,
    HorarioAindaNaoComecou,
    HorarioDeOutroMonitor,
    LimiteSemanalAtingido,
    ReservaNaoEncontrada,
)
from bot import Bot
from modelos import FALTA, FALTA_JUSTIFICADA, PRESENTE
from testes.auxiliares import AGORA, LIMITES, NOME_CALCULO, adicionar_horario, codigo_por_titulo, ir_ate_dias, montar_repositorio

TELEFONE = "5543999990001"
DEPOIS_DAS_FALTAS = datetime(2026, 10, 22, 8, 0)


class TestH3PresencaEFalta(unittest.TestCase):
    def setUp(self) -> None:
        self.repositorio = montar_repositorio()
        self.agenda = Agenda(self.repositorio)
        adicionar_horario(self.repositorio, "ter", "ana", datetime(2026, 10, 20, 14, 0))
        adicionar_horario(self.repositorio, "qua", "ana", datetime(2026, 10, 21, 14, 0))
        adicionar_horario(self.repositorio, "ter_seguinte", "ana", datetime(2026, 10, 27, 14, 0))
        adicionar_horario(self.repositorio, "qui_seguinte", "ana", datetime(2026, 10, 29, 14, 0))
        adicionar_horario(self.repositorio, "proximo_semestre", "ana", datetime(2027, 3, 10, 14, 0))
        adicionar_horario(self.repositorio, "poo_ter", "carla", datetime(2026, 10, 27, 10, 0))
        adicionar_horario(self.repositorio, "poo_qua", "carla", datetime(2026, 10, 28, 10, 0))
        self.agenda.reservar(TELEFONE, "ter", LIMITES, AGORA)
        self.agenda.reservar(TELEFONE, "qua", LIMITES, AGORA)

    def marcar(self, horario: str, situacao: str) -> None:
        self.agenda.registrar_comparecimento("ana", horario, TELEFONE, situacao, DEPOIS_DAS_FALTAS)

    def reservar(self, horario: str, assunto: str = LIMITES) -> None:
        self.agenda.reservar(TELEFONE, horario, assunto, DEPOIS_DAS_FALTAS)

    # Critério 1
    def test_monitor_marca_presenca_depois_que_o_horario_comeca(self) -> None:
        self.marcar("ter", PRESENTE)
        self.assertEqual(self.repositorio.reservas_do_horario("ter")[0].comparecimento, PRESENTE)

    def test_pode_marcar_no_minuto_em_que_o_horario_comeca(self) -> None:
        self.agenda.registrar_comparecimento("ana", "ter", TELEFONE, FALTA, datetime(2026, 10, 20, 14, 0))
        self.assertEqual(self.repositorio.reservas_do_horario("ter")[0].comparecimento, FALTA)

    def test_monitor_nao_marca_falta_antes_do_horario_comecar(self) -> None:
        with self.assertRaises(HorarioAindaNaoComecou):
            self.agenda.registrar_comparecimento("ana", "ter", TELEFONE, FALTA, datetime(2026, 10, 20, 13, 59))
        self.assertIsNone(self.repositorio.reservas_do_horario("ter")[0].comparecimento)

    def test_monitor_nao_marca_em_horario_de_outro_monitor(self) -> None:
        with self.assertRaises(HorarioDeOutroMonitor):
            self.agenda.registrar_comparecimento("bruno", "ter", TELEFONE, FALTA, DEPOIS_DAS_FALTAS)

    def test_nao_marca_para_aluno_sem_reserva_no_horario(self) -> None:
        with self.assertRaises(ReservaNaoEncontrada):
            self.agenda.registrar_comparecimento("ana", "ter", "5543999990009", FALTA, DEPOIS_DAS_FALTAS)

    # Critério 2
    def test_depois_da_primeira_falta_so_1_reserva_por_semana_na_disciplina(self) -> None:
        self.marcar("ter", FALTA)
        self.reservar("ter_seguinte")
        with self.assertRaises(LimiteSemanalAtingido) as erro:
            self.reservar("qui_seguinte")
        self.assertIn("1 reserva por semana", str(erro.exception))

    def test_presenca_nao_muda_o_limite(self) -> None:
        self.marcar("ter", PRESENTE)
        self.marcar("qua", PRESENTE)
        self.reservar("ter_seguinte")
        self.reservar("qui_seguinte")
        self.assertEqual(len(self.repositorio.reservas_do_aluno(TELEFONE)), 4)

    def test_primeira_falta_nao_muda_o_limite_de_outra_disciplina(self) -> None:
        self.marcar("ter", FALTA)
        self.reservar("poo_ter", "Tratamento de exceções")
        self.reservar("poo_qua", "Tratamento de exceções")
        self.assertEqual(len(self.repositorio.reservas_do_aluno(TELEFONE)), 4)

    # Critério 3
    def test_segunda_falta_bloqueia_a_disciplina(self) -> None:
        self.marcar("ter", FALTA)
        self.marcar("qua", FALTA)
        with self.assertRaises(DisciplinaBloqueada):
            self.reservar("ter_seguinte")

    def test_bloqueio_nao_vale_para_outra_disciplina(self) -> None:
        self.marcar("ter", FALTA)
        self.marcar("qua", FALTA)
        self.reservar("poo_ter", "Tratamento de exceções")
        self.assertEqual(len(self.repositorio.reservas_do_aluno(TELEFONE)), 3)

    def test_bloqueio_acaba_no_semestre_seguinte(self) -> None:
        self.marcar("ter", FALTA)
        self.marcar("qua", FALTA)
        self.reservar("proximo_semestre")
        self.assertEqual(len(self.repositorio.reservas_do_aluno(TELEFONE)), 3)

    def test_bot_avisa_o_motivo_quando_o_aluno_escolhe_a_disciplina_bloqueada(self) -> None:
        self.marcar("ter", FALTA)
        self.marcar("qua", FALTA)
        bot = Bot(self.repositorio, self.agenda)
        mensagem = bot.responder(TELEFONE, "oi", DEPOIS_DAS_FALTAS)
        for titulo in ["Apucarana", "Engenharia de Computação", NOME_CALCULO]:
            mensagem = bot.responder(TELEFONE, codigo_por_titulo(mensagem, titulo), DEPOIS_DAS_FALTAS)
        self.assertIn("2 faltas sem justificativa", mensagem.texto)
        self.assertIn("fim do semestre", mensagem.texto)
        self.assertIn(NOME_CALCULO, [opcao.titulo for opcao in mensagem.opcoes])

    def test_bot_deixa_escolher_a_disciplina_sem_bloqueio(self) -> None:
        self.marcar("ter", FALTA)
        bot = Bot(self.repositorio, self.agenda)
        mensagem = ir_ate_dias(bot, TELEFONE, LIMITES, DEPOIS_DAS_FALTAS)
        self.assertIn("dia", mensagem.texto.lower())

    # Critério 4
    def test_falta_justificada_nao_diminui_o_limite(self) -> None:
        self.marcar("ter", FALTA_JUSTIFICADA)
        self.reservar("ter_seguinte")
        self.reservar("qui_seguinte")
        self.assertEqual(len(self.repositorio.reservas_do_aluno(TELEFONE)), 4)

    def test_duas_faltas_justificadas_nao_bloqueiam(self) -> None:
        self.marcar("ter", FALTA_JUSTIFICADA)
        self.marcar("qua", FALTA_JUSTIFICADA)
        self.reservar("ter_seguinte")
        self.assertEqual(len(self.repositorio.reservas_do_aluno(TELEFONE)), 3)

    def test_monitor_pode_trocar_falta_por_falta_justificada(self) -> None:
        self.marcar("ter", FALTA)
        self.marcar("qua", FALTA)
        self.marcar("qua", FALTA_JUSTIFICADA)
        self.reservar("ter_seguinte")
        with self.assertRaises(LimiteSemanalAtingido):
            self.reservar("qui_seguinte")


if __name__ == "__main__":
    unittest.main()
