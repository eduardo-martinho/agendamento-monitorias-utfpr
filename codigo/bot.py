from dataclasses import dataclass, field
from datetime import date, datetime
from agenda import Agenda, ErroReserva
from modelos import DURACAO_ATENDIMENTO, Mensagem, Opcao, Reserva
from repositorio import RepositorioMemoria

# Mudança do commit 4 para o 5: separei "horarios" em "dias" e "horarios" por ficar menos confuso e para
# contornar a limitação de 10 opções do WhatsApp.
ETAPAS = ["campus", "curso", "disciplina", "assunto", "dia", "horario"]
MAXIMO_OPCOES = 10
VER_MAIS = "ver_mais"
DIAS_DA_SEMANA = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


@dataclass
class Conversa:
    etapa: str = "campus"
    escolhas: dict[str, str] = field(default_factory=dict)
    pagina: int = 0
    ultima: Mensagem = field(default_factory=lambda: Mensagem(""))


def formatar_dia(dia: date) -> str:
    return f"{DIAS_DA_SEMANA[dia.weekday()]} {dia:%d/%m}"


def paginar(opcoes: list[Opcao], pagina: int, titulo_ver_mais: str) -> list[Opcao]:
    restantes = opcoes[pagina * (MAXIMO_OPCOES - 1):]
    if len(restantes) <= MAXIMO_OPCOES:
        return restantes
    return restantes[: MAXIMO_OPCOES - 1] + [Opcao(VER_MAIS, titulo_ver_mais)]


class Bot:
    def __init__(self, repositorio: RepositorioMemoria, agenda: Agenda) -> None:
        self._repositorio = repositorio
        self._agenda = agenda
        self._conversas: dict[str, Conversa] = {}

    def responder(self, telefone: str, resposta: str, agora: datetime) -> Mensagem:
        conversa = self._conversas.get(telefone)
        if conversa is None:
            conversa = Conversa()
            self._conversas[telefone] = conversa
            return self._perguntar(conversa, agora)

        if resposta not in [opcao.codigo for opcao in conversa.ultima.opcoes]:
            return Mensagem(f"Não entendi. Escolha uma das opções da lista.\n\n{conversa.ultima.texto}", conversa.ultima.opcoes)
        if resposta == VER_MAIS:
            conversa.pagina += 1
            return self._perguntar(conversa, agora)

        conversa.escolhas[conversa.etapa] = resposta
        conversa.pagina = 0
        if conversa.etapa == "disciplina":
            motivo = self._agenda.motivo_de_bloqueio(telefone, resposta, agora)
            if motivo:
                return self._perguntar(conversa, agora, motivo)
        if conversa.etapa == "horario":
            return self._reservar(telefone, conversa, agora)
        conversa.etapa = ETAPAS[ETAPAS.index(conversa.etapa) + 1]
        return self._perguntar(conversa, agora)

    def _perguntar(self, conversa: Conversa, agora: datetime, aviso: str = "") -> Mensagem:
        """Manda a pergunta da etapa atual. Se a lista sair vazia, avisa e volta uma etapa."""
        texto, opcoes, aviso_lista_vazia, titulo_ver_mais = self._montar_lista(conversa, agora)
        if not opcoes and conversa.etapa != "campus":
            conversa.etapa = ETAPAS[ETAPAS.index(conversa.etapa) - 1]
            conversa.pagina = 0
            return self._perguntar(conversa, agora, f"{aviso}\n\n{aviso_lista_vazia}" if aviso else aviso_lista_vazia)

        if aviso:
            texto = f"{aviso}\n\n{texto}"
        conversa.ultima = Mensagem(texto, paginar(opcoes, conversa.pagina, titulo_ver_mais))
        return conversa.ultima

    def _montar_lista(self, conversa: Conversa, agora: datetime) -> tuple[str, list[Opcao], str, str]:
        escolhas = conversa.escolhas
        match conversa.etapa:
            case "campus":
                opcoes = [Opcao(campus.codigo, campus.nome) for campus in self._repositorio.listar_campus()]
                return "Olá! Vamos reservar um horário de monitoria. Escolha o campus:", opcoes, "", "Ver mais campus"
            case "curso":
                cursos = self._repositorio.cursos_do_campus(escolhas["campus"])
                opcoes = [Opcao(curso.codigo, curso.nome) for curso in cursos]
                return "Escolha o curso:", opcoes, "Ainda não há monitorias cadastradas nesse campus.", "Ver mais cursos"
            case "disciplina":
                disciplinas = self._repositorio.disciplinas_do_curso(escolhas["curso"])
                opcoes = [Opcao(disciplina.codigo, disciplina.nome) for disciplina in disciplinas]
                return (
                    "Escolha a disciplina:",
                    opcoes,
                    "Ainda não há monitorias cadastradas nesse curso.",
                    "Ver mais disciplinas",
                )
            case "assunto":
                assuntos = self._repositorio.buscar_disciplina(escolhas["disciplina"]).assuntos
                opcoes = [Opcao(str(numero), assunto) for numero, assunto in enumerate(assuntos, start=1)]
                return "Escolha o assunto da sua dúvida:", opcoes, "", "Ver mais assuntos"
            case "dia":
                dias = self._agenda.dias_disponiveis(escolhas["disciplina"], self._assunto(conversa), agora)
                opcoes = [Opcao(dia.isoformat(), formatar_dia(dia)) for dia in dias]
                return "Escolha o dia:", opcoes, "Não há horários livres para esse assunto no momento.", "Ver mais dias"
            case _:
                dia = date.fromisoformat(escolhas["dia"])
                horarios = self._agenda.horarios_do_dia(escolhas["disciplina"], self._assunto(conversa), dia, agora)
                opcoes = []
                for horario in horarios:
                    monitor = self._repositorio.buscar_monitor(horario.monitor)
                    opcoes.append(Opcao(horario.codigo, f"{horario.inicio:%H:%M} {monitor.nome} ({horario.sala})"))
                return "Escolha o horário:", opcoes, "Não há mais horários livres nesse dia.", "Ver mais horários"

    def _assunto(self, conversa: Conversa) -> str:
        assuntos = self._repositorio.buscar_disciplina(conversa.escolhas["disciplina"]).assuntos
        return assuntos[int(conversa.escolhas["assunto"]) - 1]

    def _reservar(self, telefone: str, conversa: Conversa, agora: datetime) -> Mensagem:
        try:
            reserva = self._agenda.reservar(telefone, conversa.escolhas["horario"], self._assunto(conversa), agora)
        except ErroReserva as erro:
            conversa.etapa = "dia"
            return self._perguntar(conversa, agora, str(erro))
        del self._conversas[telefone]
        return self._confirmacao(reserva)

    def _confirmacao(self, reserva: Reserva) -> Mensagem:
        horario = self._repositorio.buscar_horario(reserva.horario)
        disciplina = self._repositorio.buscar_disciplina(horario.disciplina)
        monitor = self._repositorio.buscar_monitor(horario.monitor)
        fim = horario.inicio + DURACAO_ATENDIMENTO
        linhas = [
            "Reserva confirmada!",
            f"Disciplina: {disciplina.nome}",
            f"Assunto: {reserva.assunto}",
            f"Monitor: {monitor.nome}",
            f"Dia: {DIAS_DA_SEMANA[horario.inicio.weekday()]} {horario.inicio:%d/%m/%Y}",
            f"Horário: {horario.inicio:%H:%M} às {fim:%H:%M}",
            f"Sala: {horario.sala}",
        ]
        return Mensagem("\n".join(linhas))
