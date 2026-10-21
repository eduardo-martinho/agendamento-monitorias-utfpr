from datetime import date, datetime, time, timedelta
from modelos import FALTA, PRESENTE, Campus, Curso, Disciplina, Horario, Monitor, Professor, Reserva
from repositorio import RepositorioMemoria

SEMANAS_DE_HORARIOS = 4
SEMANAS_DE_HISTORICO = 2

PROFESSORES = [
    Professor("marcos", "Marcos Oliveira"),
    Professor("renata", "Renata Lopes"),
    Professor("lucia", "Lúcia Ramos"),
]

RESPONSAVEIS = {"CGCO1A": "marcos", "FTCO2A": "renata", "POCO4A": "lucia", "EDCO3A": "lucia"}
CAMPUS = [
    Campus("APU", "Apucarana"),
    Campus("LON", "Londrina"),
    Campus("CP", "Cornélio Procópio"),
]

CURSOS = [
    Curso("ECO-APU", "Engenharia de Computação", "APU"),
    Curso("ECV-APU", "Engenharia Civil", "APU"),
    Curso("EQ-APU", "Engenharia Química", "APU"),
    Curso("EAM-LON", "Engenharia Ambiental", "LON"),
    Curso("EMT-LON", "Engenharia de Materiais", "LON"),
    Curso("ECO-CP", "Engenharia de Computação", "CP"),
    Curso("EE-CP", "Engenharia Elétrica", "CP"),
]

# Assuntos tirados do plano de ensino do portal da utfpr Engenharia de Computação de Apucarana.
DISCIPLINAS = [
    Disciplina(
        "CGCO1A",
        "Cálculo Diferencial e Integral 1",
        "ECO-APU",
        [
            "Conjuntos numéricos",
            "Funções reais de uma variável real",
            "Limites e continuidade",
            "Derivadas, diferenciais e aplicações",
            "Integrais definidas e indefinidas",
            "Técnicas de integração e integrais impróprias",
        ],
    ),
    Disciplina(
        "FTCO2A",
        "Física Teórica 1",
        "ECO-APU",
        [
            "Medição",
            "Movimento retilíneo",
            "Vetores",
            "Movimento multidimensional",
            "Leis de Newton, força e movimento",
            "Trabalho, energia e conservação da energia",
            "Sistema de partículas, centro de massa e momento linear",
            "Rotação",
            "Rolamento, torque e momento angular",
            "Equilíbrio estático",
        ],
    ),
    Disciplina(
        "POCO4A",
        "Programação Orientada a Objetos",
        "ECO-APU",
        [
            "Introdução à orientação a objetos",
            "Classes, objetos, encapsulamento, herança e polimorfismo",
            "Tratamento de exceções",
            "Padrões de projeto",
            "Interfaces gráficas",
        ],
    ),
    Disciplina(
        "EDCO3A",
        "Estrutura de Dados 1",
        "ECO-APU",
        [
            "Tipos abstratos de dados",
            "Listas lineares",
            "Pilhas, filas e filas de prioridade",
            "Árvores e árvores binárias de busca",
            "Árvores balanceadas (AVL)",
            "Tabela de espalhamento (hash)",
            "Grafos",
            "Pesquisa e ordenação",
        ],
    ),
]

MONITORES = [
    Monitor("ana", "Ana Souza", "CGCO1A"),
    Monitor("bruno", "Bruno Lima", "CGCO1A", atende_em_grupo=True, vagas_por_horario=3),
    Monitor("carla", "Carla Dias", "CGCO1A"),
    Monitor("diego", "Diego Rocha", "FTCO2A", atende_em_grupo=True, vagas_por_horario=3),
    Monitor("elisa", "Elisa Martins", "FTCO2A"),
    Monitor("fabio", "Fábio Nunes", "POCO4A"),
    Monitor("gabriela", "Gabriela Prado", "POCO4A", atende_em_grupo=True, vagas_por_horario=2),
    Monitor("heitor", "Heitor Alves", "EDCO3A"),
    Monitor("isabela", "Isabela Costa", "EDCO3A", atende_em_grupo=True, vagas_por_horario=2),
    Monitor("joao", "João Pereira", "EDCO3A"),
]
GRADE_SEMANAL = [
    ("ana", 0, time(13, 30), "E101"),
    ("ana", 0, time(14, 0), "E101"),
    ("ana", 2, time(13, 30), "E101"),
    ("bruno", 1, time(18, 0), "E203"),
    ("bruno", 3, time(18, 0), "E203"),
    ("carla", 4, time(10, 0), "E105"),
    ("carla", 4, time(10, 30), "E105"),
    ("diego", 0, time(18, 30), "F201"),
    ("diego", 2, time(18, 30), "F201"),
    ("elisa", 1, time(12, 30), "F104"),
    ("elisa", 3, time(12, 30), "F104"),
    ("fabio", 1, time(15, 0), "Lab. C005"),
    ("fabio", 1, time(15, 30), "Lab. C005"),
    ("gabriela", 3, time(16, 0), "Lab. C007"),
    ("heitor", 0, time(10, 0), "Lab. C003"),
    ("isabela", 2, time(16, 30), "Lab. C003"),
    ("joao", 4, time(14, 0), "Lab. C005"),
]


def montar_repositorio(agora: datetime) -> RepositorioMemoria:
    repositorio = RepositorioMemoria()
    for campus in CAMPUS:
        repositorio.adicionar_campus(campus)
    for curso in CURSOS:
        repositorio.adicionar_curso(curso)
    for disciplina in DISCIPLINAS:
        repositorio.adicionar_disciplina(disciplina)
    for professor in PROFESSORES:
        repositorio.adicionar_professor(professor)
    for codigo, professor in RESPONSAVEIS.items():
        repositorio.buscar_disciplina(codigo).professor = professor
    for monitor in MONITORES:
        repositorio.adicionar_monitor(monitor)

    segunda: date = agora.date() - timedelta(days=agora.weekday())
    for semana in range(-SEMANAS_DE_HISTORICO, SEMANAS_DE_HORARIOS):
        for codigo_monitor, dia_da_semana, hora, sala in GRADE_SEMANAL:
            dia = segunda + timedelta(weeks=semana, days=dia_da_semana)
            inicio = datetime.combine(dia, hora)
            monitor = repositorio.buscar_monitor(codigo_monitor)
            codigo = f"{codigo_monitor}-{inicio:%Y%m%d-%H%M}"
            repositorio.adicionar_horario(Horario(codigo, monitor.disciplina, codigo_monitor, inicio, sala))

    _preparar_historico(repositorio, agora)
    _preparar_exemplos(repositorio, agora)
    return repositorio


def _preparar_historico(repositorio: RepositorioMemoria, agora: datetime) -> None:
    passados = sorted(
        (
            horario
            for monitor in repositorio.listar_monitores()
            for horario in repositorio.horarios_do_monitor(monitor.codigo)
            if horario.inicio < agora
        ),
        key=lambda horario: (horario.inicio, horario.codigo),
    )
    for numero, horario in enumerate(passados):
        if numero % 6 == 5:
            continue
        assuntos = repositorio.buscar_disciplina(horario.disciplina).assuntos
        assunto = assuntos[(numero * 7) % len(assuntos)]
        situacao = FALTA if numero % 5 == 3 else PRESENTE
        repositorio.adicionar_reserva(Reserva(horario.codigo, f"55439777{numero:05d}", assunto, comparecimento=situacao))
        if repositorio.buscar_monitor(horario.monitor).atende_em_grupo and numero % 2 == 0:
            repositorio.adicionar_reserva(Reserva(horario.codigo, f"55439666{numero:05d}", assunto, comparecimento=PRESENTE))


def _preparar_exemplos(repositorio: RepositorioMemoria, agora: datetime) -> None:
    proximo_ana = _proximo_horario(repositorio, "CGCO1A", "ana", agora)
    if proximo_ana is not None:
        repositorio.adicionar_reserva(Reserva(proximo_ana.codigo, "5543988880001", "Limites e continuidade"))

    proximo_bruno = _proximo_horario(repositorio, "CGCO1A", "bruno", agora)
    if proximo_bruno is not None:
        repositorio.adicionar_reserva(Reserva(proximo_bruno.codigo, "5543988880002", "Limites e continuidade"))

    # cancelamento por parte do monitor e aviso ao aluno entra aqui
    proximo_elisa = _proximo_horario(repositorio, "FTCO2A", "elisa", agora)
    if proximo_elisa is not None:
        proximo_elisa.cancelado = True


def _proximo_horario(repositorio: RepositorioMemoria, disciplina: str, monitor: str, agora: datetime) -> Horario | None:
    futuros = [
        horario
        for horario in repositorio.horarios_da_disciplina(disciplina)
        if horario.monitor == monitor and horario.inicio >= agora + timedelta(hours=1)
    ]
    return min(futuros, key=lambda horario: horario.inicio, default=None)
