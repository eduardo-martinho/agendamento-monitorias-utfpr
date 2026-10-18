from datetime import datetime
from agenda import Agenda
from modelos import Mensagem
from repositorio import RepositorioMemoria


class Bot:
    """Conversa do bot com o aluno. Provisório"""

    def __init__(self, repositorio: RepositorioMemoria, agenda: Agenda) -> None:
        self._repositorio = repositorio
        self._agenda = agenda

    def responder(self, telefone: str, resposta: str, agora: datetime) -> Mensagem:
        raise NotImplementedError("A conversa do bot entra no próximo commit.")
