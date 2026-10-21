from datetime import datetime, timedelta
from agenda import Agenda, ErroDoMonitor
from bot import formatar_dia
from modelos import FALTA, FALTA_JUSTIFICADA, PRESENTE, Horario
from relatorios import PERFIL_COORDENACAO, PERFIL_MONITOR, ErroRelatorio, Relatorios
from repositorio import RepositorioMemoria

MAXIMO_NA_TELA = 15


def escolher(pergunta: str, opcoes: list[str]) -> int | None:
    while True:
        print(f"\n{pergunta}")
        for numero, opcao in enumerate(opcoes, start=1):
            print(f"  {numero}. {opcao}")
        print("  0. Voltar")
        entrada = input("> ").strip()
        if entrada == "0":
            return None
        if entrada.isdigit() and 1 <= int(entrada) <= len(opcoes):
            return int(entrada) - 1
        print("Opção inválida.")


def formatar_horas(total: timedelta) -> str:
    minutos = int(total.total_seconds()) // 60
    return f"{minutos // 60}h{minutos % 60:02d}"


def descrever(horario: Horario) -> str:
    return f"{formatar_dia(horario.inicio.date())} {horario.inicio:%H:%M} ({horario.sala})"


def tela_monitor(repositorio: RepositorioMemoria, agenda: Agenda, relatorios: Relatorios) -> None:
    # login do monitor entraria aqui
    monitores = sorted(repositorio.listar_monitores(), key=lambda monitor: monitor.nome)
    posicao = escolher("Quem é você?", [monitor.nome for monitor in monitores])
    if posicao is None:
        return
    monitor = monitores[posicao]
    while True:
        acao = escolher(f"Monitor {monitor.nome}:", ["Cancelar um horário", "Marcar presença ou falta", "Ver minhas horas do mês"])
        if acao is None:
            return
        agora = datetime.now()
        horarios = sorted(repositorio.horarios_do_monitor(monitor.codigo), key=lambda horario: horario.inicio)
        if acao == 0:
            _cancelar(repositorio, agenda, monitor.codigo, horarios, agora)
        elif acao == 1:
            _marcar_comparecimento(repositorio, agenda, monitor.codigo, horarios, agora)
        else:
            relatorio = relatorios.relatorio_mensal(PERFIL_MONITOR, monitor.codigo, agora.year, agora.month)[0]
            _mostrar_relatorio(relatorio.nome, relatorio.total, relatorio.atendimentos)


def _cancelar(repositorio: RepositorioMemoria, agenda: Agenda, monitor: str, horarios: list[Horario], agora: datetime) -> None:
    futuros = [horario for horario in horarios if horario.inicio > agora and not horario.cancelado][:MAXIMO_NA_TELA]
    textos = [f"{descrever(h)}, {len(repositorio.reservas_do_horario(h.codigo))} reserva(s)" for h in futuros]
    posicao = escolher("Qual horário você quer cancelar?", textos)
    if posicao is None:
        return
    try:
        avisos = agenda.cancelar_horario(monitor, futuros[posicao].codigo, datetime.now())
    except ErroDoMonitor as erro:
        print(erro)
        return
    print("Horário cancelado.")
    for aviso in avisos:
        print(f"Aviso para {aviso.telefone}: {aviso.texto}")


def _marcar_comparecimento(
    repositorio: RepositorioMemoria, agenda: Agenda, monitor: str, horarios: list[Horario], agora: datetime
) -> None:
    comecados = [h for h in horarios if h.inicio <= agora and not h.cancelado and repositorio.reservas_do_horario(h.codigo)]
    comecados = comecados[-MAXIMO_NA_TELA:]
    posicao = escolher("Qual horário?", [descrever(horario) for horario in comecados])
    if posicao is None:
        return
    horario = comecados[posicao]
    reservas = repositorio.reservas_do_horario(horario.codigo)
    textos = [f"{r.telefone}, {r.assunto}, {r.comparecimento or 'sem marcação'}" for r in reservas]
    aluno = escolher("Qual aluno?", textos)
    if aluno is None:
        return
    situacoes = [PRESENTE, FALTA, FALTA_JUSTIFICADA]
    situacao = escolher("O aluno:", ["Veio", "Faltou", "Faltou com justificativa"])
    if situacao is None:
        return
    try:
        agenda.registrar_comparecimento(monitor, horario.codigo, reservas[aluno].telefone, situacoes[situacao], datetime.now())
    except ErroDoMonitor as erro:
        print(erro)
        return
    print("Marcado.")


def tela_professor(repositorio: RepositorioMemoria, relatorios: Relatorios) -> None:
    # login do professor entraria aqui
    professores = sorted(repositorio.listar_professores(), key=lambda professor: professor.nome)
    posicao = escolher("Quem é você?", [professor.nome for professor in professores])
    if posicao is None:
        return
    professor = professores[posicao]
    disciplinas = relatorios.disciplinas_do_professor(professor.codigo)
    while True:
        escolhida = escolher("Qual disciplina?", [disciplina.nome for disciplina in disciplinas])
        if escolhida is None:
            return
        hoje = datetime.now().date()
        periodos = [("Últimos 7 dias", hoje - timedelta(days=6)), ("Últimos 30 dias", hoje - timedelta(days=29)), ("Este mês", hoje.replace(day=1))]
        periodo = escolher("Qual período?", [nome for nome, _ in periodos])
        if periodo is None:
            continue
        inicio = periodos[periodo][1]
        try:
            contagem = relatorios.assuntos_mais_procurados(professor.codigo, disciplinas[escolhida].codigo, inicio, hoje)
        except ErroRelatorio as erro:
            print(erro)
            continue
        print(f"\nAssuntos de {disciplinas[escolhida].nome} de {inicio:%d/%m} a {hoje:%d/%m}:")
        for assunto, total in contagem:
            print(f"  {total:3d}  {assunto}")


def tela_coordenacao(relatorios: Relatorios) -> None:
    # login da coordenação entraria aqui
    hoje = datetime.now().date()
    mes_passado = hoje.replace(day=1) - timedelta(days=1)
    meses = [(hoje.year, hoje.month), (mes_passado.year, mes_passado.month)]
    while True:
        posicao = escolher("Relatório de horas de qual mês?", [f"{mes:02d}/{ano}" for ano, mes in meses])
        if posicao is None:
            return
        ano, mes = meses[posicao]
        for relatorio in relatorios.relatorio_mensal(PERFIL_COORDENACAO, "coordenacao", ano, mes):
            _mostrar_relatorio(relatorio.nome, relatorio.total, relatorio.atendimentos)


def _mostrar_relatorio(nome: str, total: timedelta, atendimentos: list[Horario]) -> None:
    print(f"\n{nome}: {formatar_horas(total)} em {len(atendimentos)} atendimento(s)")
    for horario in atendimentos:
        print(f"  {descrever(horario)}")

