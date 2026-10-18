from datetime import date, datetime, timedelta
from modelos import Aluno, Horario, Reserva
from repositorio import RepositorioMemoria

ANTECEDENCIA_MINIMA = timedelta(hours=1)
LIMITE_SEMANAL = 2


class ErroReserva(Exception):
    """Avisa o aluno que a reserva não deu certo com o motivo"""


class HorarioIndisponivel(ErroReserva):
    def __init__(self) -> None:
        super().__init__("Esse horário não está mais disponível. Escolha outro horário.")


class LimiteSemanalAtingido(ErroReserva):
    def __init__(self) -> None:
        super().__init__(
            f"Você já tem {LIMITE_SEMANAL} reservas nessa disciplina na semana desse horário. "
            f"O limite de {LIMITE_SEMANAL} reservas por semana (de segunda a domingo) vale para cada disciplina."
        )


def inicio_da_semana(dia: datetime) -> date:
    """Segunda-feira da semana do dia."""
    return dia.date() - timedelta(days=dia.weekday())


class Agenda:
    """Regras da reserva"""

    def __init__(self, repositorio: RepositorioMemoria) -> None:
        self._repositorio = repositorio

    def horarios_disponiveis(self, disciplina: str, assunto: str, agora: datetime) -> list[Horario]:
        horarios = [
            horario
            for horario in self._repositorio.horarios_da_disciplina(disciplina)
            if self._aceita_reserva(horario, assunto, agora)
        ]
        return sorted(horarios, key=lambda horario: horario.inicio)

    def reservar(self, telefone: str, horario: str, assunto: str, agora: datetime) -> Reserva:
        # confere tudo antes de gravar
        escolhido = self._repositorio.buscar_horario(horario)
        if escolhido is None or not self._aceita_reserva(escolhido, assunto, agora):
            raise HorarioIndisponivel()
        # aqui entra penalidade por falta futuramente
        if self._reservas_na_semana(telefone, escolhido) >= LIMITE_SEMANAL:
            raise LimiteSemanalAtingido()

        if self._repositorio.buscar_aluno(telefone) is None:
            self._repositorio.adicionar_aluno(Aluno(telefone))
        reserva = Reserva(horario, telefone, assunto)
        self._repositorio.adicionar_reserva(reserva)
        return reserva

    def _aceita_reserva(self, horario: Horario, assunto: str, agora: datetime) -> bool:
        if horario.cancelado or horario.inicio < agora + ANTECEDENCIA_MINIMA:
            return False
        reservas = self._repositorio.reservas_do_horario(horario.codigo)
        if not reservas:
            return True
        monitor = self._repositorio.buscar_monitor(horario.monitor)
        if not monitor.atende_em_grupo:
            return False
        return reservas[0].assunto == assunto and len(reservas) < monitor.vagas_por_horario

    def _reservas_na_semana(self, telefone: str, horario: Horario) -> int:
        # (H2) entra aqui
        semana = inicio_da_semana(horario.inicio)
        total = 0
        for reserva in self._repositorio.reservas_do_aluno(telefone):
            outro = self._repositorio.buscar_horario(reserva.horario)
            if outro.disciplina == horario.disciplina and inicio_da_semana(outro.inicio) == semana:
                total += 1
        return total
