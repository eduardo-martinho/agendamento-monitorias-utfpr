from datetime import datetime
from agenda import Agenda
from bot import Bot
from dados_exemplo import montar_repositorio
from modelos import Mensagem

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


def main() -> None:
    # Adaptador da api do whatsapp entraria aqui
    bot = Bot(repositorio, Agenda(repositorio))
    print("Simulação do bot de monitorias da UTFPR. Digite o número da opção, ou sair para encerrar.")

    mensagem = bot.responder(TELEFONE_DE_EXEMPLO, "oi", datetime.now())
    while True:
        mostrar(mensagem)
        if not mensagem.opcoes:
            print("\n(Mande qualquer mensagem para começar outra reserva.)")
        entrada = input("> ").strip()
        if entrada.lower() == "sair":
            break
        mensagem = bot.responder(TELEFONE_DE_EXEMPLO, traduzir_entrada(entrada, mensagem), datetime.now())


if __name__ == "__main__":
    main()
