from dataclasses import dataclass, field
from datetime import datetime, timedelta

DURACAO_ATENDIMENTO = timedelta(minutes=30)

# Marca se o aluno faltou ou não (H3).
PRESENTE = "presente"
FALTA = "falta"
FALTA_JUSTIFICADA = "falta justificada"


@dataclass
class Campus:
    codigo: str
    nome: str


@dataclass
class Curso:
    codigo: str
    nome: str
    campus: str


@dataclass
class Disciplina:
    codigo: str
    nome: str
    curso: str
    assuntos: list[str]


@dataclass
class Monitor:
    codigo: str
    nome: str
    disciplina: str
    atende_em_grupo: bool = False
    vagas_por_horario: int = 1


@dataclass
class Horario:
    codigo: str
    disciplina: str
    monitor: str
    inicio: datetime
    sala: str
    cancelado: bool = False


@dataclass
class Aluno:
    telefone: str


@dataclass
class Reserva:
    horario: str
    telefone: str
    assunto: str
    cancelada_pelo_monitor: bool = False
    comparecimento: str | None = None


@dataclass
class Aviso:

    telefone: str
    texto: str


@dataclass
class Opcao:
    codigo: str
    titulo: str


@dataclass
class Mensagem:
    texto: str
    opcoes: list[Opcao] = field(default_factory=list)
