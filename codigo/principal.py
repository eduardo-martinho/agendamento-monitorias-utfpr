from datetime import datetime
from agenda import Agenda
from bot import Bot
from dados_exemplo import montar_repositorio
from modelos import Mensagem
from relatorios import Relatorios
from telas import escolher, tela_coordenacao, tela_monitor, tela_professor

TELEFONE_DE_EXEMPLO = "5543999990000"


def mostrar(mensagem: Mensagem) -> None:
    print()
    print(mensagem.texto)
    for numero, opcao in enumerate(mensagem.opcoes, start=1):
        print(f"  {numero}. {opcao.titulo}")


def traduzir_entrada(entrada: str, mensagem: Mensagem) -> str:
    if entrada.isdigit() and 1 <= int(entrada) <= len(mensagem.opcoes):
        return mensagem.opcoes[int(entrada) - 1].codigo
    return entrada


def conversar_com_o_bot(bot: Bot) -> None:
    print("\nSimulação do bot no WhatsApp. Digite o número da opção, ou sair para voltar ao menu.")
    mensagem = bot.responder(TELEFONE_DE_EXEMPLO, "oi", datetime.now())
    while True:
        mostrar(mensagem)
        if not mensagem.opcoes:
            print("\n(Mande qualquer mensagem para começar outra reserva.)")
        entrada = input("> ").strip()
        if entrada.lower() == "sair":
            return
        mensagem = bot.responder(TELEFONE_DE_EXEMPLO, traduzir_entrada(entrada, mensagem), datetime.now())


def main() -> None:
    # Adaptador da api do whatsapp entraria aqui
    repositorio = montar_repositorio(datetime.now())
    agenda = Agenda(repositorio)
    bot = Bot(repositorio, agenda)
    relatorios = Relatorios(repositorio)
    print("Sistema de monitorias da UTFPR (protótipo).")
    while True:
        perfil = escolher("Entrar como:", ["Aluno (bot do WhatsApp)", "Monitor", "Professor", "Coordenação"])
        if perfil is None:
            break
        if perfil == 0:
            conversar_com_o_bot(bot)
        elif perfil == 1:
            tela_monitor(repositorio, agenda, relatorios)
        elif perfil == 2:
            tela_professor(repositorio, relatorios)
        else:
            tela_coordenacao(relatorios)


if __name__ == "__main__":
    main()
