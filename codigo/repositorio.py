from modelos import Aluno, Campus, Curso, Disciplina, Horario, Monitor, Reserva


class RepositorioMemoria:
 # Banco de dados subtitui aqui futuramente, mantendo os mesmos métodos

    def __init__(self) -> None:
        self._campus: dict[str, Campus] = {}
        self._cursos: dict[str, Curso] = {}
        self._disciplinas: dict[str, Disciplina] = {}
        self._monitores: dict[str, Monitor] = {}
        self._horarios: dict[str, Horario] = {}
        self._alunos: dict[str, Aluno] = {}
        self._reservas: list[Reserva] = []

    def adicionar_campus(self, campus: Campus) -> None:
        self._campus[campus.codigo] = campus

    def adicionar_curso(self, curso: Curso) -> None:
        self._cursos[curso.codigo] = curso

    def adicionar_disciplina(self, disciplina: Disciplina) -> None:
        self._disciplinas[disciplina.codigo] = disciplina

    def adicionar_monitor(self, monitor: Monitor) -> None:
        # cadastro de monitor e aceite pelo professor entra aqui depois
        self._monitores[monitor.codigo] = monitor

    def adicionar_horario(self, horario: Horario) -> None:
        self._horarios[horario.codigo] = horario

    def adicionar_aluno(self, aluno: Aluno) -> None:
        self._alunos[aluno.telefone] = aluno

    def adicionar_reserva(self, reserva: Reserva) -> None:
        self._reservas.append(reserva)

    def listar_campus(self) -> list[Campus]:
        return list(self._campus.values())

    def cursos_do_campus(self, campus: str) -> list[Curso]:
        return [curso for curso in self._cursos.values() if curso.campus == campus]

    def disciplinas_do_curso(self, curso: str) -> list[Disciplina]:
        return [disciplina for disciplina in self._disciplinas.values() if disciplina.curso == curso]

    def horarios_da_disciplina(self, disciplina: str) -> list[Horario]:
        return [horario for horario in self._horarios.values() if horario.disciplina == disciplina]

    def reservas_do_horario(self, horario: str) -> list[Reserva]:
        return [reserva for reserva in self._reservas if reserva.horario == horario]

    def reservas_do_aluno(self, telefone: str) -> list[Reserva]:
        return [reserva for reserva in self._reservas if reserva.telefone == telefone]

    def buscar_disciplina(self, codigo: str) -> Disciplina | None:
        return self._disciplinas.get(codigo)

    def buscar_monitor(self, codigo: str) -> Monitor | None:
        return self._monitores.get(codigo)

    def buscar_horario(self, codigo: str) -> Horario | None:
        return self._horarios.get(codigo)

    def buscar_aluno(self, telefone: str) -> Aluno | None:
        return self._alunos.get(telefone)
