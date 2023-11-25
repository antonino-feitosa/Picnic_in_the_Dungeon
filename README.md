
# Picnic in the Dungeon


Jogo de exploração de masmorras com foco no desenvolvimento de habilidades. As masmorras apresentarão alta dificuldade sendo a morte do personagem permanente, no entanto, armas, raças e habilidades serão liberadas para novos personagens à medida que objetivos da masmorra forem alcançados. Será oferecido um sistema de desenvolvimento de habilidades de modo que o usuário possa customizar o seu personagem e por esse motivo não serão fornecidas classes.

Além disso, o jogo também apresentará opções de customização de modo que o usuário possa gerar conteúdo. Isso inclui o desenvolvimento de cenários, quebra-cabeças, armadilhas, equipamentos, armas, poções, além do desenvolvimento de habilidades.

Princípios do Jogo:
1. Customização: o usuário é livre para escolher como deseja evoluir o personagem, escolhendo as principais características como: uso de armas, uso de magias, uso de aliados, habilidades, etc. Por exemplo, ele pode desejar criar um guerreiro que usa magia de fortalecimento enquanto ataca com um machado, ou então, um psíquico usando controle mental para fazer os inimigos lutarem entre si. Além disso, o usuário pode criar suas próprias habilidades combinando as mecânicas disponíveis no jogo.
2. Aprendizado: cada partida deve ser única de modo que o usuário precisa aprender a identificar os inimigos, suas táticas e combate e habilidades. Assim, os inimigos incluindo suas táticas e habilidades serão gerados proceduralmente a cada partida.
3. Único: cada partida deve ser única, isto é, os cenários são gerados proceduralmente e a morte é permanente. No entanto, para a morte nao frustrar o usuário, o personagem será utilizado para gerar novos inimigos especiais que aparecerão nas novas partidas considerando o contexto da morte, por exemplo, a morte por um zumbi pode gerar super zumbi fazendo uso da habilidades e equipamentos do personagem, ou então, a morte por goblins pode gerar uma horda de goblins equipadas com os equipamentos do personagem.
4. Cenários Atrativos: os cenários devem ser atrativos do ponto de vista visual como imagens e disposição do espaço físico como também no sentido de interação. Os cenários devem apresentar diferentes elementos de interação, por exemplo, correntezas de água, rochas que podem ser quebradas para liberar a passagem, possibilidade de explorar cavernas submersas, diferentes quebra-cabeças gerando recompensas, armadilhas inteligentes que podem ser usadas em favor do usuário.
5. Ambiente Hostil: os cenários devem ser hostis e dinâmicos de modo uma exploração cautelosa gerará mais recompensas ao custo de riscos maiores. Por exemplo, os cenários terão diferentes armadilhas que sempre podem ser evitados com tempo suficiente, porém, ao longo do tempo, os inimigos podem evoluir aumentando a dificuldade caso a exploração torne muito longa.
6. Estratégias: os inimigos são desenvolvidos para que o usuário empregue diferentes táticas apresente desafios além do modo massacrar e cortar. No entanto, o usuário pode evitar esses desafios optando por um modo de jogo mais simples. Assim, outras habilidades podem ser exploradas como uso da diplomacia para evitar combates, treinamento de inimigos tornando-os aliados, uso da inteligência para operar mecanismos desconhecidos, etc. Desse modo, outras características podem facilitar a exploração da masmorra, por exemplo, inteligência pode ser usada para operar mecanismos como um robô, carisma pode ser usada obter aliados, sabedoria para identificar caminhos perigosos ou alimentos seguros.
7. Morte Permanente: devido à dificuldade, o personagem pode morrer frequentemente, no entanto, isso não deve ser visto como algo negativo. O personagem deve sentir que cursou uma aventura e obteve experiências dessa jornada. Para isso, deve ser implementado um ambiente de guilda, corporação ou associação, assim, o usuário pode focar em melhorar a guilda catalogando espécies, formas de ataque, armas, magias, etc. Desse modo, se espera que uma desassociação do personagem removendo o ponto negativo da morte do personagem.


Simple ARPG with rogue like game elements:
- [ ] Turn Based (Strategy)
- [ ] Procedural Map Generation;
- [ ] Permanent Death;
- [ ] High difficulty;
- [ ] Powers Customization (like Daemon Supers[^1]);
- [ ] Rare and Champion Monsters (like Diablo 3[^2]);
- [ ] Puzzles (like Zelda[^3], Pokemon[^4], video games[^5], Goof a Troop[^16] and RPG[^6]);
- [ ] Races, Classes and Weapons (race customization by user choices);
- [ ] Dialog and Conversation Strategies;
- [ ] Environment Interaction (like Brogue[^14], Pokemon[^13], Metroid[^15] and Divinity Original Sin 2[^25]);
- [ ] Map Height, Walter, Caves (like Zelda[^3], Pokemon[^13] and Metroid[^15]);
- [ ] Weapons Strategy (like Brogue[^12]);
- [ ] Strange and Hostil Environment (like Roadside Picnic[^7] and Annihilation[^8] with elements of Debris[^9], Doctor Who[^10] and Darker than Black[^19]);
- [ ] Tower Defense Elements (like traps and defenses in Clash of Clans[^11]);
- [ ] Monster Capture (like Pokemon[^4]);
- [ ] Procedural Quests
- [ ] Combat System (like Civilization [^20] with elements of Pokemon[^4])
- [ ] Skills (like Dungeons and Dragons[^21])
- [ ] Camps (like Civilization [^20])
- [ ] Hordes (like Left for Dead [^22])


## Progresso

## Detalhes de Implementação

Projeto pessoal em desenvolvimento. Para executar, use:

```python
python3 -m pip install -U pygame --user
python3 main.py
```

### Algoritmo de Passeio Aleatório

O algoritmo de passeio aleatório é aplicado para geração procedural de mapas. Recebe a posição inicial do passeio, a quantidade de passos e um conjunto de possíveis direções a serem seguidas (geralmente as direções cardinais) e então efetua o passeio retornando um conjunto de posições representado os espaço em que os personagens podem se mover.

Ele é aplicado na geração no mapa em formato de ilha que consiste em aplicar o passeio uma quantidade N de vezes a partir do centro do mapa de dimensões bidimensional. A quantidade de passos é escolhida como o mínimo entre a metade da largura e metade da altura do mapa. A posição inicial é configurada como o centro do mapa e a posição final como o ponto mais distante do início, considerando somente o passo final de cada passeio. Os mapas gerados por esse processo apresentam o formato de uma grande área concentrada no centro do mapa com ramificações radiais.

Trabalho Futuro
- [ ] Mapa em formato de arquipélago
- [ ] Mapa em formato de continente
- [ ] Mapa em formato de cavernas
- [ ] Mapa em formato de estrela

### Algoritmo de Campo de Visão

Avaliando o estudo efetuado em [^33], escolhemos o algoritmo básico (ray casting) para a implementação do campo de visão. O estudo conclui que o algoritmo é equivalente aos demais em tempo de processamento e gera campos plausíveis nos cenários de pilares e diagonais, além de apresentar boa simetria em mapas fechados, com exceção das situações de cantos perpendiculares. No entanto, o estudo é de 2009 e não há referência disponível para a implementação utilizada.

Nossa implementação utiliza o algoritmo de desenho de linhas de Bresenham [^34], traçando linhas a partir de um centro para cada posição de distância _radius_ considerando a distância de Manhattan. Os pontos em cada linha são ordenados, iniciando no centro considerando visíveis todos os pontos que não encontram obstáculos a partir do centro. Isto é, percorremos as linhas do centro até a borda, considerando todos os pontos visíveis até encontrar um obstáculo.

Trabalho Futuro
- [x] Alterar o raio do foco de visão
    - [x] Formato circular
    - [x] Formato diamante
    - [x] Formato octogonal
    - [x] Formato frontal
    - [x] Formato periférico

### Dependências

Densevolvimento em Python 3 com Pygame [^32] para implementação de recursos básicos como janela, tratamento de imagens, etc.

```pip3 install pygame```

Todas as imagens são de autoria própria.

Todas as músicas, sons e fontes foram obtidas como licença GPL. Para cada recurso, indicamos o link usado para obtenção e incluímos a licença associada, sempre que disponível. Caso algum autor seja contra o uso de seu material, entre em contato para remoção do conteúdo.

As fontes utilizadas são listadas a seguir:
https://all-free-download.com/font/download/gadaj_6918765.html
https://www.dafont.com/pt/haunting-spirits.font


### Problemas

[ ] Apresentação dos tooltips quando monstro e um item ocupam o mesmo espaço.
[ ] Se o usuário possuir muitos itens, alguns deles não serão apresentados na tela, pois a renderização assume uma tela infinita.
[ ] Mensagens dificultam a visualização do mapa nas laterais.
[ ] Falta feedback para uso de magias em posições vazias.
[ ] Feedback de alvos afetados por possível dano em área.

<!--

https://fontesk.com/consola-mono-typeface/
https://fontesk.com/tomorrow-typeface/
https://fontesk.com/project-space-font/
https://fontesk.com/fleuron-typeface/
https://fontesk.com/kalmunt-font/

https://www.gnu.org/software/freefont/


https://all-free-download.com/font/download/laizzier_comic_6911249.html
https://all-free-download.com/font/download/domestic_manners_6899401.html
https://all-free-download.com/font/download/casa_sans_6898880.html
https://all-free-download.com/font/download/subzer0_6915464.html
https://all-free-download.com/font/download/nerko_6912869.html
https://all-free-download.com/font/download/cartoony_worldoz_6906319.html
https://all-free-download.com/font/download/subtlety_6894618.html
https://all-free-download.com/font/download/dr_jekyll_6902903.html
https://all-free-download.com/font/download/cibergotica_6905828.html

Fontes para Desenho
https://all-free-download.com/font/download/voodoo_vampire_6918285.html
https://all-free-download.com/font/download/ye_olde_oak_6919017.html
https://all-free-download.com/font/download/emilio_20_6906777.html
https://all-free-download.com/font/download/code_danger_6905640.html
https://all-free-download.com/font/download/look_sir_droids_6897071.html
https://all-free-download.com/font/download/chronicles_of_arkmar_6898410.html
https://all-free-download.com/font/download/ibm_logo_6909435.html
https://all-free-download.com/font/download/tory_gothic_caps_6917317.html
https://all-free-download.com/font/download/cake_frosting_6894950.html
https://all-free-download.com/font/download/mizike_6899419.html
https://all-free-download.com/font/download/thannhaeuser_zier_6898285.html
https://all-free-download.com/font/download/cheshire_initials_6895514.html
https://all-free-download.com/font/download/typographer_woodcut_initials_one_6898275.html
https://all-free-download.com/font/download/feinsliebchen_barock_6907627.html
https://all-free-download.com/font/download/astroneo_6901744.html
https://all-free-download.com/font/download/bb_petie_boy_6895937.html
https://all-free-download.com/font/download/constanze_initials_6905504.html
https://all-free-download.com/font/download/reddit_face_6915008.html
https://all-free-download.com/font/download/precious_6913754.html
https://all-free-download.com/font/download/riot_act_6894532.html
https://all-free-download.com/font/download/yaki_goma_6919003.html
https://all-free-download.com/font/download/rabanera_6918926.html
https://all-free-download.com/font/download/dead_6903682.html
https://all-free-download.com/font/download/my_font_6911333.html
https://all-free-download.com/font/download/morris_jenson_initialen_6911541.html
https://all-free-download.com/font/download/porter_sans_block_6913790.html
https://all-free-download.com/font/download/scratched_letters_6916835.html
https://all-free-download.com/font/download/circuit_board_6905801.html
https://all-free-download.com/font/download/lilith_6910911.html
https://all-free-download.com/font/download/namskout_6912991.html
https://all-free-download.com/font/download/dark_garden_6898032.html

Fontes para Símbolos
https://all-free-download.com/font/download/x_code_from_east_6918992.html
https://all-free-download.com/font/download/braile_font_6901085.html
https://all-free-download.com/font/download/masonic_cipher_6912307.html
https://www.dafont.com/pt/lomtrian.font
https://www.dafont.com/pt/number-one.font
https://www.dafont.com/pt/the-orb-report.font
https://www.1001freefonts.com/alphacode-pandora.font
https://www.1001freefonts.com/alphacode-emperor.font
https://www.1001freefonts.com/alphacode-beyond.font
-->




[^1]: [Daemon Powers](https://wiki.daemon.com.br/index.php?title=Supers_RPG)
[^2]: [Diablo 3 - Monters](https://www.reddit.com/r/Diablo/comments/tuhcc/whats_the_difference_between_champion_rare_and/)
[^3]: [Zelda - Puzzles](https://gamerant.com/zelda-hardest-puzzles-how-to-solve/)
[^4]: [Pokemon - Puzzles](https://www.thegamer.com/pokemon-hardest-puzzles-across-all-games-ranked/)
[^5]: [Video Game - Puzzles](https://www.denofgeek.com/games/hardest-video-game-puzzles/)
[^6]: [RPG - Puzzles](https://www.reddit.com/r/rpg/comments/1l72cw/10000_greatest_traps_puzzles/)
[^7]: [Roadside Picnic](https://en.wikipedia.org/wiki/Roadside_Picnic)
[^8]: [Annihilation ](https://en.wikipedia.org/wiki/Annihilation_(VanderMeer_novel))
[^9]: [Debris ](https://en.wikipedia.org/wiki/Debris_(TV_series))
[^11]: [Clash of Clans](https://en.wikipedia.org/wiki/Clash_of_Clans)
[^10]: [Doctor Who](https://pt.wikipedia.org/wiki/Doctor_Who)
[^12]: [Brogue - Weapons](https://brogue.fandom.com/wiki/Category:Weapon)
[^13]: [Pokemon Moves](https://bulbapedia.bulbagarden.net/wiki/Field_move)
[^14]: [Brogue - Terrain](https://brogue.fandom.com/wiki/Terrain_Features)
[^15]: [Metroid Powers](https://metroid.fandom.com/wiki/Super_Metroid#Power-ups_and_suit_upgrades)
[^16]: [Goof Troop - Pluzzes](http://playingwithsuperpower.com/goof-troop-review/)
[^17]: [ANSI Escape Codes](https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797)
[^18]: [Rogue Like with Rust](https://bfnightly.bracketproductions.com/chapter_0.html)
[^19]: [Darker than Black](https://en.wikipedia.org/wiki/Darker_than_Black)
[^20]: [Civilization](https://civilization.fandom.com/wiki/Combat_(Civ6))
[^21]: [Dungeons and Dragons Skills](https://ocd20.fandom.com/wiki/Skills)
[^22]: [Left for Dead - Horde](https://left4dead.fandom.com/wiki/Common_Infected#The_Horde)
[^23]: [Formações de Combate - Jogos](https://www.tagmar.com.br/wiki/Default.aspx?PageName=Forma%C3%A7%C3%A3o%20de%20Combate)
[^24]: [Formações de Combate - Aérea](https://www.aereo.jor.br/2010/08/11/mais-sobre-formacoes-de-combate/)
[^25]: [Interações de Ambiente in DOS2](https://divinityoriginalsin2.wiki.fextralife.com/Environmental+Effects)

[^32]: [Pygame](https://www.pygame.org/news)
[^33]: [Comparative study of field of view algorithms for 2D grid based worlds](https://www.roguebasin.com/index.php/Comparative_study_of_field_of_view_algorithms_for_2D_grid_based_worlds)
[^34]: [Bresenham's line algorithm](https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm)


<!--
[^61]: [Configure Key GIT](https://roelofjanelsinga.com/articles/how-to-setup-gpg-signing-keys-in-github/#:~:text=How%20to%20get%20the%20verified%20flag%20on%20your,use%20your%20GPG%20key%20to%20sign%20commits%20)
[^60]: [triangle rasterization](http://www.sunshine2k.de/coding/java/TriangleRasterization/TriangleRasterization.html)
[^61]: [line rasterization](https://www.javatpoint.com/computer-graphics-bresenhams-line-algorithm)
[^62]: [Field of View](https://www.researchgate.net/publication/347719548_New_Algorithms_for_Computing_Field_of_Vision_over_2D_Grids)
[^63]: [Field of View - Rogue](http://www.roguebasin.com/index.php/Comparative_study_of_field_of_view_algorithms_for_2D_grid_based_worlds)
[^64]: [Game Algorithms](https://www.phstudios.com/game-algorithm-series/)
[^65]: [Brogue](https://sites.google.com/site/broguegame/)
[^66]: [Multiple Body](https://www.gridsagegames.com/blog/2020/04/developing-multitile-creatures-roguelikes/)
[^67]: [IA] (http://www.roguebasin.com/index.php/Roguelike_Intelligence_-_Stateless_AIs)
[^68]: [IA - path](https://news.ycombinator.com/item?id=22848888)
[^69]: [Dijkstra map](http://www.roguebasin.com/index.php?title=The_Incredible_Power_of_Dijkstra_Maps)
[^60]: [Dijkstra map - Rogue Basin](http://www.roguebasin.com/index.php/Dijkstra_Maps_Visualized)



[//]: # https://www.dafont.com/pt/haunting-spirits.font
[//]: # https://www.1001freefonts.com/alphacode-beyond.font
[//]: # https://www.1001freefonts.com/alphacode-emperor.font
[//]: # https://www.1001freefonts.com/alphacode-pandora.font
[//]: # https://www.dafont.com/pt/the-orb-report.font
[//]: # https://www.dafont.com/pt/number-one.font
[//]: # https://www.dafont.com/pt/lomtrian.font


-->