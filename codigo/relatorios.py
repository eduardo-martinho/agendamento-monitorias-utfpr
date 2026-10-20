from datetime import date

from modelos import PRESENTE, Disciplina
from repositorio import RepositorioMemoria


class ErroRelatorio(Exception):
    """Motivo pelo qual o relatório não pôde ser gerado."""


class DisciplinaDeOutroProfessor(ErroRelatorio):
    def __init__(self) -> None:
        super().__init__("Você não é o professor responsável por essa disciplina.")


class PeriodoInvalido(ErroRelatorio):
    def __init__(self) -> None:
        super().__init__("A data final não pode ser antes da data inicial.")


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
