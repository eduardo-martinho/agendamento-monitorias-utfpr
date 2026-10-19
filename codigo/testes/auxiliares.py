from datetime import datetime
from bot import Bot
from modelos import Campus, Curso, Disciplina, Horario, Mensagem, Monitor
from repositorio import RepositorioMemoria
AGORA = datetime(2026, 10, 19, 8, 0)

CALCULO = "CGCO1A"
POO = "POCO4A"
NOME_CALCULO = "Cálculo Diferencial e Integral 1"
NOME_POO = "Programação Orientada a Objetos"
LIMITES = "Limites e continuidade"
DERIVADAS = "Derivadas, diferenciais e aplicações"


def montar_repositorio() -> RepositorioMemoria:
    repositorio = RepositorioMemoria()
    repositorio.adicionar_campus(Campus("APU", "Apucarana"))
    repositorio.adicionar_campus(Campus("LON", "Londrina"))
    repositorio.adicionar_curso(Curso("ECO-APU", "Engenharia de Computação", "APU"))
    repositorio.adicionar_curso(Curso("ECV-APU", "Engenharia Civil", "APU"))
    repositorio.adicionar_curso(Curso("ECO-LON", "Engenharia de Computação", "LON"))
    repositorio.adicionar_disciplina(
        Disciplina(CALCULO, NOME_CALCULO, "ECO-APU", ["Funções reais de uma variável real", LIMITES, DERIVADAS])
    )
    repositorio.adicionar_disciplina(
        Disciplina(POO, NOME_POO, "ECO-APU", ["Introdução à orientação a objetos", "Tratamento de exceções"])
    )
    repositorio.adicionar_monitor(Monitor("ana", "Ana Souza", CALCULO))
    repositorio.adicionar_monitor(Monitor("bruno", "Bruno Lima", CALCULO, atende_em_grupo=True, vagas_por_horario=2))
    repositorio.adicionar_monitor(Monitor("carla", "Carla Dias", POO))
    return repositorio


def adicionar_horario(
    repositorio: RepositorioMemoria,
    codigo: str,
    monitor: str,
    inicio: datetime,
    sala: str = "E101",
    cancelado: bool = False,
) -> Horario:
    disciplina = repositorio.buscar_monitor(monitor).disciplina
    horario = Horario(codigo, disciplina, monitor, inicio, sala, cancelado)
    repositorio.adicionar_horario(horario)
    return horario


def titulos(mensagem: Mensagem) -> list[str]:
    return [opcao.titulo for opcao in mensagem.opcoes]


def codigos(mensagem: Mensagem) -> list[str]:
    return [opcao.codigo for opcao in mensagem.opcoes]


def codigo_por_titulo(mensagem: Mensagem, titulo: str) -> str:
    for opcao in mensagem.opcoes:
        if opcao.titulo == titulo:
            return opcao.codigo
    raise AssertionError(f"A opção {titulo!r} não está na lista: {titulos(mensagem)}")


def ir_ate_dias(
    bot: Bot,
    telefone: str,
    assunto: str,
    agora: datetime = AGORA,
    disciplina: str = NOME_CALCULO,
) -> Mensagem:
    mensagem = bot.responder(telefone, "oi", agora)
    for titulo in ["Apucarana", "Engenharia de Computação", disciplina, assunto]:
        mensagem = bot.responder(telefone, codigo_por_titulo(mensagem, titulo), agora)
    return mensagem


def ir_ate_horarios(
    bot: Bot,
    telefone: str,
    assunto: str,
    dia: str,
    agora: datetime = AGORA,
    disciplina: str = NOME_CALCULO,
) -> Mensagem:
    mensagem = ir_ate_dias(bot, telefone, assunto, agora, disciplina)
    return bot.responder(telefone, codigo_por_titulo(mensagem, dia), agora)
