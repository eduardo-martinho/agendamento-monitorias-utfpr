from dataclasses import dataclass
from datetime import date, timedelta

from modelos import DURACAO_ATENDIMENTO, PRESENTE, Disciplina, Horario
from repositorio import RepositorioMemoria


class ErroRelatorio(Exception):
    """Motivo pelo qual o relatório não pôde ser gerado."""


class DisciplinaDeOutroProfessor(ErroRelatorio):
    def __init__(self) -> None:
        super().__init__("Você não é o professor responsável por essa disciplina.")


class PeriodoInvalido(ErroRelatorio):
    def __init__(self) -> None:
        super().__init__("A data final não pode ser antes da data inicial.")


class MesInvalido(ErroRelatorio):
    def __init__(self) -> None:
        super().__init__("O mês precisa estar entre 1 e 12.")


class AcessoNegado(ErroRelatorio):
    def __init__(self) -> None:
        super().__init__("Só o próprio monitor e a coordenação podem ver o relatório de horas.")


PERFIL_MONITOR = "monitor"
PERFIL_COORDENACAO = "coordenacao"


@dataclass
class RelatorioDoMonitor:
    monitor: str
    nome: str
    total: timedelta
    atendimentos: list[Horario]


class Relatorios:

    # aqui entraria uma interface do professor

    def __init__(self, repositorio: RepositorioMemoria) -> None:
        self._repositorio = repositorio

    def disciplinas_do_professor(self, professor: str) -> list[Disciplina]:
        return self._repositorio.disciplinas_do_professor(professor)

    def assuntos_mais_procurados(self, professor: str, disciplina: str, inicio: date, fim: date) -> list[tuple[str, int]]:
        """numero de duvidas por assunto da disciplina (H4)."""
        escolhida = self._repositorio.buscar_disciplina(disciplina)
        if escolhida is None or escolhida.professor != professor:
            raise DisciplinaDeOutroProfessor()
        if fim < inicio:
            raise PeriodoInvalido()

        contagem = {assunto: 0 for assunto in escolhida.assuntos}
        for horario in self._repositorio.horarios_da_disciplina(disciplina):
            if not inicio <= horario.inicio.date() <= fim:
                continue
            for reserva in self._repositorio.reservas_do_horario(horario.codigo):
                if reserva.comparecimento == PRESENTE and reserva.assunto in contagem:
                    contagem[reserva.assunto] += 1
        return sorted(contagem.items(), key=lambda item: item[1], reverse=True)

    def relatorio_mensal(self, perfil: str, solicitante: str, ano: int, mes: int) -> list[RelatorioDoMonitor]:
        # Aqui teria uma aba de login
        if not 1 <= mes <= 12:
            raise MesInvalido()
        if perfil == PERFIL_MONITOR and self._repositorio.buscar_monitor(solicitante) is not None:
            monitores = [self._repositorio.buscar_monitor(solicitante)]
        elif perfil == PERFIL_COORDENACAO:
            monitores = sorted(self._repositorio.listar_monitores(), key=lambda monitor: monitor.nome)
        else:
            raise AcessoNegado()

        relatorios = []
        for monitor in monitores:
            atendimentos = sorted(
                (
                    horario
                    for horario in self._repositorio.horarios_do_monitor(monitor.codigo)
                    if (horario.inicio.year, horario.inicio.month) == (ano, mes) and self._teve_atendimento(horario)
                ),
                key=lambda horario: horario.inicio,
            )
            total = DURACAO_ATENDIMENTO * len(atendimentos)
            relatorios.append(RelatorioDoMonitor(monitor.codigo, monitor.nome, total, atendimentos))
        return relatorios

    def _teve_atendimento(self, horario: Horario) -> bool:
        if horario.cancelado:
            return False
        return any(reserva.comparecimento == PRESENTE for reserva in self._repositorio.reservas_do_horario(horario.codigo))
