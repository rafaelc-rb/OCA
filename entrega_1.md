<!-- Escolher um algoritmo/problema e justificar a escolha
Não pode ser algoritmo de ordenação
Sugiro problema do ensalamento -->

# Entregável 1

## Algoritmo: Problema do Ensalamento

### Descrição do Problema

O problema do ensalamento trata da alocação de eventos (como aulas, reuniões ou provas) em um número limitado de salas, respeitando restrições como o horário de início e término de cada evento, de modo que não haja sobreposição de eventos em uma mesma sala. Em outras palavras, cada sala deve conter eventos que não se sobreponham no tempo.

Este problema é comumente encontrado em instituições de ensino ao definir o uso das salas de aula durante o semestre ou em empresas ao organizar reuniões em salas disponíveis. Além da restrição de tempo, o problema pode ser estendido para considerar capacidades das salas, preferências de horários, ou características específicas de cada evento.

#### Exemplo Prático
Considere uma instituição de ensino com um conjunto limitado de salas. Cada aula tem um nome, um horário de início e um horário de término. A tarefa é alocar as aulas nessas salas de modo que não haja sobreposição de horários dentro de uma mesma sala, mas utilizando o mínimo possível de salas.

---

### Justificativa da Escolha do Problema

A escolha do problema do ensalamento se justifica por sua relevância e aplicabilidade em diversos cenários do mundo real, especialmente em ambientes educacionais e empresariais. É um problema de otimização bastante comum e pode ser abordado com diferentes técnicas, desde soluções simples até algoritmos mais sofisticados de otimização.

Além disso, ele envolve múltiplas restrições (como horários e quantidade de salas), o que o torna um ótimo exemplo de como lidar com problemas complexos de alocação de recursos limitados. A solução desse problema pode impactar diretamente a eficiência da gestão de espaço e tempo, tornando-se uma tarefa crucial em várias instituições.

Por não ser um problema de ordenação simples, ele também envolve a consideração de múltiplos fatores simultaneamente (horário, sala, conflito de tempo), o que demanda uma abordagem mais elaborada e justifica sua escolha.

---

### Abordagem: Algoritmo Guloso

#### Explicação da Abordagem Gulosa

Uma abordagem gulosa, ou **greedy**, é uma estratégia algorítmica onde tomamos decisões passo a passo, selecionando a melhor opção local em cada etapa, sem reavaliar escolhas anteriores. No caso do problema do ensalamento, a abordagem gulosa tenta alocar cada aula na primeira sala disponível que não tenha conflito de horário com as aulas já alocadas naquela sala.

O algoritmo funciona da seguinte forma:
1. Ordena-se a lista de aulas com base no horário de início.
2. A cada nova aula, verifica-se em qual das salas já ocupadas a aula pode ser alocada sem causar conflito de horário.
3. Se não houver sala disponível, uma nova sala é aberta.
4. O processo continua até que todas as aulas estejam alocadas.

Essa abordagem toma decisões locais e rápidas, garantindo uma solução válida para o problema, embora não garanta a solução globalmente ótima (como o uso mínimo de salas). No entanto, para cenários onde o número de salas não precisa ser minimizado ao extremo, a abordagem gulosa é eficiente e direta.

#### Justificativa da Escolha da Abordagem Gulosa

A escolha da abordagem gulosa para este problema é justificada por sua simplicidade e eficiência em problemas onde decisões rápidas são adequadas. A abordagem gulosa é fácil de implementar e fornece uma solução válida sem a necessidade de explorar todas as possíveis combinações de alocação, o que poderia ser computacionalmente custoso.

Para o problema do ensalamento, a abordagem gulosa é apropriada porque:
- **Eficiência**: Ela aloca as aulas de maneira direta e rápida, tomando decisões locais em cada passo.
- **Simplicidade**: É fácil de entender e implementar, sendo uma boa escolha para resolver problemas de alocação de recursos com restrições simples.
- **Aplicabilidade**: Embora não garanta a solução mais otimizada (mínimo de salas), em muitos cenários do mundo real, a abordagem é suficientemente boa para gerar soluções viáveis que atendem às restrições.

Em resumo, a abordagem gulosa é ideal quando precisamos de uma solução eficiente e não exigimos uma otimização global perfeita. Para problemas mais complexos, onde a minimização extrema de recursos é necessária, outras abordagens mais sofisticadas podem ser consideradas, mas a simplicidade da solução gulosa a torna uma excelente escolha inicial.
