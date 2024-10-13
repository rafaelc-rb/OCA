# Problema do Ensalamento

## Descrição

O problema do ensalamento refere-se ao desafio de alocar aulas ou eventos em um conjunto limitado de salas, respeitando certas restrições como horários e capacidades. Esse tipo de problema é comumente enfrentado por instituições de ensino ao organizar a ocupação de salas de aula durante o semestre ou por organizações que precisam alocar salas de reuniões de forma eficiente.

### Restrições comuns:
- Cada aula tem um horário de início e fim.
- Não pode haver sobreposição de aulas em uma mesma sala.
- O número de salas disponíveis é limitado.

### Objetivo:
O objetivo deste projeto é alocar as aulas nas salas disponíveis de forma eficiente, garantindo que não ocorram conflitos de horários e que todas as aulas sejam alocadas, sempre que possível.

---

## Solução

Este projeto em Python utiliza uma abordagem simples para resolver o problema do ensalamento. A solução envolve a criação de aulas e a verificação de conflitos de horários entre elas, a fim de alocá-las nas salas de maneira otimizada.

### Funcionalidades:
- O programa solicita ao usuário o número de salas e aulas.
- Para cada aula, o usuário informa o nome, horário de início e término.
- O programa tenta alocar cada aula em uma sala disponível, evitando sobreposição de horários.

### Estrutura do Código:

- **Classe `Aula`**: Representa cada aula com um nome, horário de início e horário de término.
- **Função `verificar_conflito`**: Verifica se duas aulas têm conflito de horário (ou seja, se suas aulas se sobrepõem).
- **Função `alocar_aulas`**: Responsável por alocar as aulas nas salas, respeitando os horários e evitando sobreposição.
- **Função `obter_input_aulas`**: Solicita ao usuário os dados das aulas, como nome, horário de início e término.
  
### Exemplo de Execução:

```plaintext
Digite o número de salas disponíveis: 2
Digite o número de aulas: 3
Digite o nome da aula 1: Matemática
Digite o horário de início da aula Matemática (em formato 24h, ex: 8 para 08:00): 8
Digite o horário de término da aula Matemática (em formato 24h, ex: 10 para 10:00): 10
Digite o nome da aula 2: Física
Digite o horário de início da aula Física (em formato 24h, ex: 10 para 10:00): 10
Digite o horário de término da aula Física (em formato 24h, ex: 12 para 12:00): 12
Digite o nome da aula 3: Química
Digite o horário de início da aula Química (em formato 24h, ex: 9 para 09:00): 9
Digite o horário de término da aula Química (em formato 24h, ex: 11 para 11:00): 11
Sala 1: [Matemática (8-10), Física (10-12)]
Sala 2: [Química (9-11)]
