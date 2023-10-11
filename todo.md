
# Casos de Uso

- [x] Durante o jogo o usuário pode ter a opção de acessar um menu para sair do jogo, reiniciar a partida ou voltar para o menu principal.

- [x] Cada entidade pode executar uma quantidade diferentes de ações por turno. O usuário, após executar as ações desejadas com as entidades que ele possui controle, ele deve notificar a passagem de turno. Em seguida, o jogo determina as ações das demais entidades e ao final do turno retorna o controle ao jogador.

- [ ] Cada entidade possui um conjunto de atributo que influencia as ações no jogo. Seu valor inicial é determinado pela raça do personagem e os valores devem ser balanceados entre diferentes raças. Em geral, temos a força, destreza, constituição, inteligência, carisma, sabedoria. Esses atributos serão utilizados para determinar requisitos de habilidades, armas, etc. Habilidades especiais como magia, super poderes, etc. serão baseadas nesses atributos, por exemplo, o super poder de imunidade será baseado em constituição; o poder de lançar bolas de fogo, em inteligência; o poder de cura, em sabedoria.

- [ ] O jogo inicia apresentando uma guilda com o progresso do usuário que consiste nos principais elementos do jogo, isto é, armas, magias, raças, classes, poções, armaduras, etc. Inicialmente estará disponível somente as opções básicas. Além disso, haverá uma seção de pesquisa, outra para recrutamento, outra para missões e outra para exploração. Na aba de pesquisa o usuário pode criar novos elementos, porém, eles só estarão disponíveis após a exploração com sucesso da masmorra associada. A seção de recrutamento oferece a criação novos personagens e equipes considerando os elementos disponíveis. O usuário pode optar pela seleção de missões para liberar elementos secundários como ataques especiais de armas previamente liberadas, variações de magias, etc. Por fim, a aba de exploração permite que o usuário escolha elementos primários que ele deseja explorar que serão liberados após uma exploração efetiva da masmorra. Cada masmorra consiste em 25 níveis com desafios a cada 5 níveis. Uma exploração efetiva consiste em derrotar o desafio associado ao elemento escolhido.

- [ ] O usuário, na seção de pesquisa, pode criar novos elementos. Por exemplo, raças são características das entidades inatas como ter chifres, asas, visão noturna, aptidão para magia, etc. Cada um desses elementos precisam ser liberados através da exploração da masmorra. Além disso, cada elemento pode ter habilidades associadas que devem ser liberadas através de missões. Por exemplo, uma raça que possui chifres pode aprender a habilidade investida com chifres após cumprir a missão que pode ser encontrar touros com esse ataque, conseguir desviar de uma certa quantidade de ataques desse tipo, fazer com que o touro cause dano a si mesmo ao mirar sem considerar as consequências, etc.

- [ ] As masmorras devem se adaptar a quantidade de membros na equipe de modo que uma equipe com um único membro tenha as mesmas condições que uma equipe com vários membros. Assim, a masmorra pode ajustar a quantidade de vida e dano das entidades de modo que diferentes formações de equipes levem o mesmo tempo para completar as masmorras considerando a média dos casos.

- [ ] As habilidades dos personagem interagir com o ambiente de forma significativa. Por exemplo, um personagem com força alta pode mover pedras e destruir paredes enquanto que um personagem com inteligência alta pode operar diferentes mecanismos presentes na masmorra. É esperado que cada habilidade apresente ao menos cinco formas diferentes de iteração e a masmorra deve gerar cenários explorando o uso das habilidades escolhidas pelo personagem. Para avaliar esse item, podemos comparar o tempo de conclusão da masmorra no caso médio explorando ou não o uso das interações.

- [ ] O usuário pode controlar diferentes entidades. O jogo se desenvolve em turnos alternados entre as ações das entidades do personagem e das entidades controladas pelo computador. Cada entidade pode desenvolver diferentes ações e a ordem de execução é controlada pela sua iniciativa (característica da unidade) de modo que ela possa executar todas de uma vez, somente algumas e até mesmo optar por ser a última a agir no turno. Quando várias unidades optam por ficar o final, é criada uma lista de acordo a sequência dos pedidos.

- [ ] As entidades podem colidir com outras ou as paredes do cenário. Essas colisões deve se apresentar de modo diferente.

- [ ] O personagem deve ser capaz de acessar um mapa apresentando as áreas exploradas e destacando as áreas atualmente visíveis.

- [ ] Os cenários podem conter buracos e cavernas que levam aos níveis mais profundos. Dependendo de como a entidade entra no buraco, ele pode sofrer danos da queda. Um nível mais profundo deve ser entendido como ao menos o próximo nível. Esses buracos devem ser representados de forma adequada no cenário.

- [ ] Os cenários devem ter passagens levando aos níveis mais profundos da masmorra. De modo análogo, deve haver passagens para que o personagem possar retornar ao nível anterior. Essas passagens devem ser representadas por escadas, portais ou similares desde que passe a ideia de uma passagem.

- [ ] Os ataques devem alterar o cenário e até mesmo destruir paredes ou o solo. A destruição das paredes pode abrir passagens entre outras regiões do cenário e a destruição do solo deve abrir buracos levando aos níveis mais profundos. Observe que isso não deve ser algo fácil e que dependendo do método pode chamar a atenção de entidades próximas.

- [ ] Dependendo do nível de inteligência, é possível interagir com outras entidades, até mesmo inimigas. Devem existir diferentes linguagens sendo apresentadas ao usuário por fontes diferentes e até mesmo linguagens desconhecidas devem ser apresentadas, isso será feito por símbolos.

- [ ] As entidades podem ser inteligentes o suficiente para se organizar em formações, aumentando a eficiência em combates.

- [ ] Deve haver patrulhas de entidades ao longo dos cenários. Essas patrulhas podem variar entre entidades simples que invocam outras aos desafios do cenário. No entanto, devem ser configuradas de tal modo que o usuário possa optar por engajar em combate, preparar uma armadilha ou mesmo evitar.

- [ ] A guilda deve oferecer missões que possam ser cumpridas numa partida. Essas missões devem geradas proceduralmente e devem ter várias ramificações. Por exemplo, uma missão para coletar ervas pode levar a missão de irrigação, que por sua vez envolve a liberação de um canal através do assassinato de uma entidade no local. As ramificações devem ser transparentes e geradas proceduralmente. Convém pesquisar algum sistema de planejamento.

- [ ] As entidades devem ter emoções influenciando o comportamento imediato. Por exemplo, um inimigo pode ficar com muito apavorado após presenciar a morte de seus companheiros ou então entrar em fúria, etc. Convém pesquisar algum sistema de representação computacional de emoções.

- [ ] As entidades devem ter perfis de personalidade influenciando o comportamento em grupos. Por exemplo, isso pode afetar escolha de alvos fazendo um personagem preferenciar a proteção do grupo sobre a própria.

- [ ] Algumas salas são apenas pontes e as entidades podem usar isso contra as outras.

- [ ] Algumas paredes podem conter passagens secretas. Em vez da entidade colidir com a parede, a passagem secreta será revelada expandindo o campo de visão que antes era limitado pela parede falsa.

- [ ] Alguns poderes estão associados aos sentidos considerando os sentidos básicos e especializados. A visão é responsável pela percepção visual, além de identificar as entidades dentro do campo de visão, ela identifica o nível de dificuldade dos inimigos através de sua cor e também é importante para leitura de mensagens espalhadas no cenário. A audição identifica entidades invisíveis móveis ou ocultas, como mecanismos e armadilhas baseadas em mecanismos, além de escuta de mensagens emitidas pelas entidades. O olfato identifica armadilhas baseadas em veneno e também entidades invisíveis imóveis ou até mesmo rastrear entidades. O tato identifica entidades próximas, como armadilhas e mecanismos baseados em pressão, e também alterações no cenários como tremores. O paladar pode identificar alimentos venenosos além de oferecer bônus e penalidades para preferências alimentares como carnívoro, onívoro e vegetariano. Podemos citar como sentidos especializados a capacidade de sentir a magia nas entidades, sentir o cheiro de sangue, etc.

## Programação

- [ ] Refatorar os sistemas de renderização, animação e controles para ter como base um sistema nas coordenadas na tela e então a especialização deve considerar a câmera e as coordenadas do mundo.

- [ ] Implementar um sistema para os sons monitorando quando eles devem ser interrompidos, isto é, quando a entidade for destruída.

- [ ] Adicionar botão de sair na interface.

- [ ] Implementar a ação de iniciar o jogo.

## Tarefas de Implementação

- [x] Ground System
- [x] Random Walk
- [x] Camera
- [x] Camera Translate
- [x] Mini Map
- [x] Mini Map Controls
- [x] Player Position
- [x] Mini Map Player Position
- [x] Player Directional Controls
- [x] Refactor Position and Dimension
- [x] Field of View
- [x] Field of View Integration with Map
- [x] Animation System
- [x] Camera System
- [x] Animation Transition System
- [x] Motion System
- [x] Player 8 Directional Sprites
- [x] Centralize Minimap
- [x] Message System
- [x] Id for Units
- [ ] Turn System
- [ ] Simple IA System
- [ ] Add Enemies
- [ ] Refactor Game (Minimap)
- [ ] Mouse Control System
- [ ] Refactor Loader
- [ ] Refactor Mouse System
- [ ] Message System with Options
- [ ] Collectable System
- [ ] Doors
- [ ] Triggers
- [ ] Switches
- [ ] Wave Collapse Function
- [ ] Map Generation (Random Walk + Wave Collapse Function)
- [ ] Player Directions Sprites
- [ ] Player Animations
- [ ] Map Levels
- [ ] Binary Spatial Partition Map
- [ ] Cellular Automata Map
- [ ] Voronoy Hive Map
- [ ] Path selection with direction and collision
