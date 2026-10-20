from datetime import date, datetime, timedelta
from modelos import FALTA, Aluno, Aviso, Horario, Reserva
from repositorio import RepositorioMemoria

ANTECEDENCIA_MINIMA = timedelta(hours=1)
LIMITE_SEMANAL = 2
LIMITE_SEMANAL_DEPOIS_DA_FALTA = 1
FALTAS_PARA_BLOQUEIO = 2
MAXIMO_DIAS = 30


class ErroReserva(Exception):
    """Avisa o aluno que a reserva não deu certo com o motivo"""


class HorarioIndisponivel(ErroReserva):
    def __init__(self) -> None:
        super().__init__("Esse horário não está mais disponível.")


class LimiteSemanalAtingido(ErroReserva):
    def __init__(self, limite: int = LIMITE_SEMANAL) -> None:
        if limite == LIMITE_SEMANAL:
            super().__init__(
                f"Você já tem {LIMITE_SEMANAL} reservas nessa disciplina na semana desse horário. "
                f"O limite de {LIMITE_SEMANAL} reservas por semana (de segunda a domingo) vale para cada disciplina."
            )
        else:
            super().__init__(
                "Você já tem uma reserva nessa disciplina na semana desse horário. Depois de uma falta sem "
                f"justificativa, o seu limite nela passou a ser de {limite} reserva por semana neste semestre."
            )


class DisciplinaBloqueada(ErroReserva):
    def __init__(self, disciplina: str) -> None:
        super().__init__(
            f"Você teve {FALTAS_PARA_BLOQUEIO} faltas sem justificativa em monitorias de {disciplina} neste "
            "semestre e não pode mais reservar nessa disciplina até o fim do semestre."
        )


class ErroDoMonitor(Exception):
    """Motivo pelo qual o sistema recusou o que o monitor tentou fazer."""


class HorarioJaComecou(ErroDoMonitor):
    def __init__(self) -> None:
        super().__init__("Esse horário já começou e não pode mais ser cancelado.")


class HorarioDeOutroMonitor(ErroDoMonitor):
    def __init__(self) -> None:
        super().__init__("Esse horário não é seu.")


class HorarioAindaNaoComecou(ErroDoMonitor):
    def __init__(self) -> None:
        super().__init__("Presença e falta só podem ser marcadas depois que o horário começa.")


class ReservaNaoEncontrada(ErroDoMonitor):
    def __init__(self) -> None:
        super().__init__("Esse aluno não tem reserva nesse horário.")


def semestre(dia: datetime) -> tuple[int, int]:
    # aqui precisa colocar quando o semestre começa e acaba
    return dia.year, 1 if dia.month <= 7 else 2


def inicio_da_semana(dia: datetime) -> date:
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

    def dias_disponiveis(self, disciplina: str, assunto: str, agora: datetime) -> list[date]:
        """Os primeiros dias que têm pelo menos um horário livre, até MAXIMO_DIAS dias."""
        dias: list[date] = []
        for horario in self.horarios_disponiveis(disciplina, assunto, agora):
            if horario.inicio.date() not in dias:
                dias.append(horario.inicio.date())
        return dias[:MAXIMO_DIAS]

    def horarios_do_dia(self, disciplina: str, assunto: str, dia: date, agora: datetime) -> list[Horario]:
        return [
            horario
            for horario in self.horarios_disponiveis(disciplina, assunto, agora)
            if horario.inicio.date() == dia
        ]

    def reservar(self, telefone: str, horario: str, assunto: str, agora: datetime) -> Reserva:
        # confere tudo antes de gravar
        escolhido = self._repositorio.buscar_horario(horario)
        if escolhido is None or not self._aceita_reserva(escolhido, assunto, agora):
            raise HorarioIndisponivel()
        faltas = self._faltas_no_semestre(telefone, escolhido.disciplina, escolhido.inicio)
        if faltas >= FALTAS_PARA_BLOQUEIO:
            raise DisciplinaBloqueada(self._repositorio.buscar_disciplina(escolhido.disciplina).nome)
        limite = LIMITE_SEMANAL_DEPOIS_DA_FALTA if faltas > 0 else LIMITE_SEMANAL
        if self._reservas_na_semana(telefone, escolhido) >= limite:
            raise LimiteSemanalAtingido(limite)

        if self._repositorio.buscar_aluno(telefone) is None:
            self._repositorio.adicionar_aluno(Aluno(telefone))
        reserva = Reserva(horario, telefone, assunto)
        self._repositorio.adicionar_reserva(reserva)
        return reserva

    def cancelar_horario(self, monitor: str, horario: str, agora: datetime) -> list[Aviso]:
        """(H2, cancela o horário e avisa o aluno que tinha reservado)"""
        escolhido = self._repositorio.buscar_horario(horario)
        if escolhido is None or escolhido.monitor != monitor:
            raise HorarioDeOutroMonitor()
        if agora >= escolhido.inicio:
            raise HorarioJaComecou()

        escolhido.cancelado = True
        disciplina = self._repositorio.buscar_disciplina(escolhido.disciplina)
        texto = (
            f"Sua monitoria de {disciplina.nome} em {escolhido.inicio:%d/%m/%Y} às {escolhido.inicio:%H:%M} "
            "foi cancelada pelo monitor. Essa reserva não conta no seu limite da semana."
        )
        avisos = []
        for reserva in self._repositorio.reservas_do_horario(horario):
            if not reserva.cancelada_pelo_monitor:
                reserva.cancelada_pelo_monitor = True
                avisos.append(Aviso(reserva.telefone, texto))
        # Aqui iria: mandar cada aviso pelo adaptador do WhatsApp.
        return avisos

    def motivo_de_bloqueio(self, telefone: str, disciplina: str, agora: datetime) -> str | None:
        """bloqueio por faltas (H3)."""
        if self._faltas_no_semestre(telefone, disciplina, agora) >= FALTAS_PARA_BLOQUEIO:
            return str(DisciplinaBloqueada(self._repositorio.buscar_disciplina(disciplina).nome))
        return None

    def registrar_comparecimento(self, monitor: str, horario: str, telefone: str, situacao: str, agora: datetime) -> None:
        """marca se o aluno faltou ou não  (H3)."""
        escolhido = self._repositorio.buscar_horario(horario)
        if escolhido is None or escolhido.monitor != monitor:
            raise HorarioDeOutroMonitor()
        if agora < escolhido.inicio:
            raise HorarioAindaNaoComecou()
        for reserva in self._repositorio.reservas_do_horario(horario):
            if reserva.telefone == telefone and not reserva.cancelada_pelo_monitor:
                reserva.comparecimento = situacao
                return
        raise ReservaNaoEncontrada()

    def _faltas_no_semestre(self, telefone: str, disciplina: str, dia: datetime) -> int:
        total = 0
        for reserva in self._repositorio.reservas_do_aluno(telefone):
            horario = self._repositorio.buscar_horario(reserva.horario)
            if (
                reserva.comparecimento == FALTA
                and horario.disciplina == disciplina
                and semestre(horario.inicio) == semestre(dia)
            ):
                total += 1
        return total

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
        semana = inicio_da_semana(horario.inicio)
        total = 0
        for reserva in self._repositorio.reservas_do_aluno(telefone):
            if reserva.cancelada_pelo_monitor:
                continue
            outro = self._repositorio.buscar_horario(reserva.horario)
            if outro.disciplina == horario.disciplina and inicio_da_semana(outro.inicio) == semana:
                total += 1
        return total
