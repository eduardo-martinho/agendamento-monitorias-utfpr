import unittest
from datetime import datetime, timedelta
from agenda import Agenda
from bot import Bot
from modelos import FALTA, FALTA_JUSTIFICADA, PRESENTE
from relatorios import PERFIL_COORDENACAO, PERFIL_MONITOR, AcessoNegado, MesInvalido, Relatorios
from testes.auxiliares import AGORA, DERIVADAS, LIMITES, adicionar_horario, ir_ate_horarios, montar_repositorio

ALUNO_A = "5543999990001"
ALUNO_B = "5543999990002"
ALUNO_C = "5543999990003"
DEPOIS = datetime(2026, 11, 3, 8, 0)
MEIA_HORA = timedelta(minutes=30)


class TestH5RelatorioMensal(unittest.TestCase):
    def setUp(self) -> None:
        self.repositorio = montar_repositorio()
        self.agenda = Agenda(self.repositorio)
        self.relatorios = Relatorios(self.repositorio)

        self.atender("ana_presente", "ana", datetime(2026, 10, 20, 14, 0), [(ALUNO_A, PRESENTE)])
        self.atender("ana_falta", "ana", datetime(2026, 10, 21, 14, 0), [(ALUNO_A, FALTA)])
        self.atender("ana_justificada", "ana", datetime(2026, 10, 23, 14, 0), [(ALUNO_B, FALTA_JUSTIFICADA)])
        self.atender("bruno_grupo", "bruno", datetime(2026, 10, 22, 18, 0), [(ALUNO_B, PRESENTE), (ALUNO_C, PRESENTE)])
        self.atender("bruno_novembro", "bruno", datetime(2026, 11, 2, 18, 0), [(ALUNO_A, PRESENTE)])
        adicionar_horario(self.repositorio, "ana_cancelado", "ana", datetime(2026, 10, 22, 14, 0))
        self.agenda.reservar(ALUNO_C, "ana_cancelado", LIMITES, AGORA)
        self.agenda.cancelar_horario("ana", "ana_cancelado", AGORA)

    def atender(self, codigo: str, monitor: str, inicio: datetime, alunos: list[tuple[str, str]]) -> None:
        """Cria o horário, faz as reservas e marca o comparecimento de cada aluno."""
        adicionar_horario(self.repositorio, codigo, monitor, inicio)
        for telefone, situacao in alunos:
            self.agenda.reservar(telefone, codigo, LIMITES, AGORA)
            self.agenda.registrar_comparecimento(monitor, codigo, telefone, situacao, DEPOIS)

    def do_monitor(self, monitor: str, mes: int = 10):
        return self.relatorios.relatorio_mensal(PERFIL_MONITOR, monitor, 2026, mes)[0]

    # Critério 1
    def test_horario_com_aluno_presente_conta_30_minutos(self) -> None:
        self.assertEqual(self.do_monitor("ana").total, MEIA_HORA)

    def test_horario_em_grupo_conta_30_minutos_uma_vez_so(self) -> None:
        relatorio = self.do_monitor("bruno")
        self.assertEqual(relatorio.total, MEIA_HORA)
        self.assertEqual([horario.codigo for horario in relatorio.atendimentos], ["bruno_grupo"])

    # Critério 2
    def test_horario_cancelado_nao_conta(self) -> None:
        codigos = [horario.codigo for horario in self.do_monitor("ana").atendimentos]
        self.assertNotIn("ana_cancelado", codigos)

    def test_horario_em_que_todos_faltaram_nao_conta(self) -> None:
        codigos = [horario.codigo for horario in self.do_monitor("ana").atendimentos]
        self.assertNotIn("ana_falta", codigos)
        self.assertNotIn("ana_justificada", codigos)

    def test_grupo_com_um_presente_e_um_faltante_conta(self) -> None:
        adicionar_horario(self.repositorio, "bruno_misto", "bruno", datetime(2026, 10, 29, 18, 0))
        self.agenda.reservar(ALUNO_B, "bruno_misto", DERIVADAS, AGORA)
        self.agenda.reservar(ALUNO_C, "bruno_misto", DERIVADAS, AGORA)
        self.agenda.registrar_comparecimento("bruno", "bruno_misto", ALUNO_B, FALTA, DEPOIS)
        self.agenda.registrar_comparecimento("bruno", "bruno_misto", ALUNO_C, PRESENTE, DEPOIS)
        self.assertEqual(self.do_monitor("bruno").total, 2 * MEIA_HORA)

    # Critério 3
    def test_relatorio_e_so_do_mes_escolhido(self) -> None:
        novembro = self.do_monitor("bruno", mes=11)
        self.assertEqual([horario.codigo for horario in novembro.atendimentos], ["bruno_novembro"])
        self.assertEqual(novembro.total, MEIA_HORA)

    def test_mostra_total_e_atendimentos_de_cada_monitor(self) -> None:
        relatorios = self.relatorios.relatorio_mensal(PERFIL_COORDENACAO, "coordenacao", 2026, 10)
        resumo = [(r.nome, r.total, [h.codigo for h in r.atendimentos]) for r in relatorios]
        self.assertEqual(
            resumo,
            [
                ("Ana Souza", MEIA_HORA, ["ana_presente"]),
                ("Bruno Lima", MEIA_HORA, ["bruno_grupo"]),
                ("Carla Dias", timedelta(0), []),
            ],
        )

    def test_mes_invalido_e_recusado(self) -> None:
        with self.assertRaises(MesInvalido):
            self.relatorios.relatorio_mensal(PERFIL_COORDENACAO, "coordenacao", 2026, 13)

    # Critério 4
    def test_monitor_gera_so_o_proprio_relatorio(self) -> None:
        relatorios = self.relatorios.relatorio_mensal(PERFIL_MONITOR, "ana", 2026, 10)
        self.assertEqual([relatorio.monitor for relatorio in relatorios], ["ana"])

    def test_outro_perfil_nao_gera_relatorio_de_horas(self) -> None:
        with self.assertRaises(AcessoNegado):
            self.relatorios.relatorio_mensal("professor", "marcos", 2026, 10)

    def test_bot_nunca_mostra_horas_nem_bolsa(self) -> None:
        bot = Bot(self.repositorio, self.agenda)
        adicionar_horario(self.repositorio, "ana_futuro", "ana", datetime(2026, 11, 10, 14, 0))
        mensagens = [ir_ate_horarios(bot, "5543999990009", LIMITES, "ter 10/11", DEPOIS)]
        mensagens.append(bot.responder("5543999990009", "ana_futuro", DEPOIS))
        for mensagem in mensagens:
            texto = mensagem.texto.lower()
            self.assertNotIn("horas", texto)
            self.assertNotIn("bolsa", texto)
        self.assertIn("Reserva confirmada", mensagens[-1].texto)


if __name__ == "__main__":
    unittest.main()
