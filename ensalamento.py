class Aula:
    def __init__(self, nome, inicio, fim):
        """
        Construtor da classe Aula. Inicializa o nome, horário de início e horário de término da aula.
        
        Parâmetros:
        - nome: Nome da aula.
        - inicio: Horário de início da aula (em formato 24h).
        - fim: Horário de término da aula (em formato 24h).
        """
        self.nome = nome
        self.inicio = inicio
        self.fim = fim

    def __repr__(self):
        """
        Representação em string da aula, que será usada ao imprimir a lista de aulas alocadas.
        Exibe o nome da aula e seu intervalo de horários.
        """
        return f'{self.nome} ({self.inicio}-{self.fim})'


def verificar_conflito(aula1, aula2):
    """
    Função que verifica se há conflito de horários entre duas aulas.
    
    Parâmetros:
    - aula1: Objeto da classe Aula.
    - aula2: Outro objeto da classe Aula.
    
    Retorna:
    - True se não houver conflito (ou seja, se os horários não se sobrepõem).
    - False se houver conflito (ou seja, se os horários se sobrepõem).
    """
    return not (aula1.fim <= aula2.inicio or aula1.inicio >= aula2.fim)


def alocar_aulas(aulas, num_salas):
    """
    Função que aloca as aulas nas salas disponíveis de acordo com os horários.
    
    Parâmetros:
    - aulas: Lista de objetos da classe Aula, ordenados por horário de início.
    - num_salas: Número de salas disponíveis.
    
    Retorna:
    - Uma lista de listas, onde cada lista interna representa as aulas alocadas em uma sala.
    """
    # Inicializa as salas como listas vazias
    salas = [[] for _ in range(num_salas)]
    
    # Itera sobre todas as aulas
    for aula in aulas:
        alocada = False  # Flag para verificar se a aula foi alocada
        
        # Tenta alocar a aula em uma sala disponível
        for sala in salas:
            # Verifica se há conflito de horário com outras aulas já alocadas na sala
            if all(not verificar_conflito(aula, a) for a in sala):
                sala.append(aula)  # Aloca a aula na sala
                alocada = True  # Marca a aula como alocada
                break
        
        # Se a aula não pôde ser alocada, imprime uma mensagem de aviso
        if not alocada:
            print(f'Não foi possível alocar a aula {aula.nome}')
    
    return salas


def obter_input_aulas():
    """
    Função que obtém os dados das aulas diretamente do usuário via input.
    
    Pergunta ao usuário o número de aulas, e para cada aula solicita o nome, horário de início e horário de término.
    
    Retorna:
    - Uma lista de objetos da classe Aula.
    """
    aulas = []
    num_aulas = int(input("Digite o número de aulas: "))  # Pergunta o número total de aulas
    for i in range(num_aulas):
        nome = input(f"Digite o nome da aula {i + 1}: ")  # Nome da aula
        inicio = int(input(f"Digite o horário de início da aula {nome} (em formato 24h, ex: 8 para 08:00): "))  # Horário de início
        fim = int(input(f"Digite o horário de término da aula {nome} (em formato 24h, ex: 10 para 10:00): "))  # Horário de término
        aulas.append(Aula(nome, inicio, fim))  # Adiciona a aula à lista de aulas
    return aulas


# Função principal
if __name__ == "__main__":
    """
    Função principal que executa o programa.
    
    Solicita ao usuário o número de salas e as aulas, e depois tenta alocá-las de forma otimizada.
    Ao final, exibe as alocações feitas para cada sala.
    """
    # Obtém o número de salas disponíveis
    num_salas = int(input("Digite o número de salas disponíveis: "))
    
    # Obtém as aulas diretamente do usuário
    aulas = obter_input_aulas()

    # Aloca as aulas nas salas disponíveis
    salas_alocadas = alocar_aulas(sorted(aulas, key=lambda x: x.inicio), num_salas)

    # Exibe a alocação final das aulas por sala
    for i, sala in enumerate(salas_alocadas):
        print(f'Sala {i + 1}: {sala}')
