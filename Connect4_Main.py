import pygame
import random
import argparse

AZUL = (0, 0, 255)
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
TAMANHO_BORDA = (7, 6)


class ColunaPreenchidaTotalmente(Exception):

    def __init__(self, valor):
        self.valor = valor

    def __str__(self):
        return repr(self.valor)


class EspacoMoedas():
    """Representa um espaço no quadro"""
    TAMANHO = 80

    def __init__(self, linha_index, coluna_index, width, height, x1, y1):
        """Inicializa um espaço em uma determinada posição no quadro"""
        self.content = 0
        self.linha_index = linha_index
        self.coluna_index = coluna_index
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width * 2, height * 2))
        self.x_pos = x1
        self.y_pos = y1

    def get_localizacao(self):
        return (self.linha_index, self.coluna_index)

    def get_posicao(self):
        return (self.x_pos, self.y_pos)

    def set_moeda(self, moeda):
        self.content = moeda.get_tipo_moeda()

    def checa_espaco_preenchido(self):
        return (self.content != 0)

    def get_content(self):
        return self.content

    def desenha(self, background):
        pygame.draw.rect(self.surface, VERDE, (0, 0, self.width, self.height))
        pygame.draw.rect(self.surface, BRANCO, (1, 1, self.width - 2, self.height - 2))
        self.surface = self.surface.convert()
        background.blit(self.surface, (self.x_pos, self.y_pos))


class RastreadorNodo():
    """Representa o nodo na representação gráfica interna do tabuleiro do jogo"""

    def __init__(self):
        """Inicializa com ponteiros para os nodos em todas as 8 direções ao redor"""
        self.top_left = None
        self.top_right = None
        self.top = None
        self.left = None
        self.right = None
        self.bottom_left = None
        self.bottom = None
        self.bottom_right = None
        self.top_left_score = 1
        self.top_right_score = 1
        self.top_score = 1
        self.left_score = 1
        self.right_score = 1
        self.bottom_left_score = 1
        self.bottom_score = 1
        self.bottom_right_score = 1
        self.value = 0
        self.visited = False


class Borda():
    MARGEM_X = 350
    MARGEM_Y = 150

    def __init__(self, numero_linhas, numero_colunas):
        self.container = [[EspacoMoedas(i, j, EspacoMoedas.TAMANHO, EspacoMoedas.TAMANHO,
                                        j * EspacoMoedas.TAMANHO + Borda.MARGEM_X,
                                        i * EspacoMoedas.TAMANHO + Borda.MARGEM_Y) for j in range(numero_colunas)] for i in range(numero_linhas)]
        self.numero_linhas = numero_linhas
        self.numero_colunas = numero_colunas
        self.total_espacos = numero_linhas * numero_colunas
        self.numero_espacos_preenchidos = 0
        self.ultimo_nodo_visitado = []
        self.ultimo_valor = 0

        self.estado = [[0 for j in range(numero_colunas)] for i in range(numero_linhas)]
        self.estado_anterior = None
        self.movimento_anterior = (None, None, None)

        self.representacao = [[RastreadorNodo() for j in range(numero_colunas)] for i in range(numero_linhas)]
        for i in range(numero_linhas):
            linha_index_anterior = i - 1
            linha_index_proxima = i + 1
            for j in range(numero_colunas):
                coluna_index_anterior = j - 1
                coluna_index_proxima = j + 1
                nodo_atual = self.representacao[i][j]
                if linha_index_anterior >= 0 and coluna_index_anterior >= 0:
                    nodo_atual.top_left = self.representacao[linha_index_anterior][coluna_index_anterior]
                if linha_index_anterior >= 0:
                    nodo_atual.top = self.representacao[linha_index_anterior][j]
                if linha_index_anterior >= 0 and coluna_index_proxima < numero_colunas:
                    nodo_atual.top_right = self.representacao[linha_index_anterior][coluna_index_proxima]
                if coluna_index_anterior >= 0:
                    nodo_atual.left = self.representacao[i][coluna_index_anterior]

                if coluna_index_proxima < numero_colunas:
                    nodo_atual.right = self.representacao[i][coluna_index_proxima]
                if linha_index_proxima < numero_linhas and coluna_index_anterior >= 0:
                    nodo_atual.bottom_left = self.representacao[linha_index_proxima][coluna_index_anterior]

                if linha_index_proxima < numero_linhas:
                    nodo_atual.bottom = self.representacao[linha_index_proxima][j]
                if linha_index_proxima < numero_linhas and coluna_index_proxima < numero_colunas:
                    nodo_atual.bottom_right = self.representacao[linha_index_proxima][coluna_index_proxima]

    def desenha(self, background):
        """Desenha a borda inteira na tela"""
        for i in range(self.numero_linhas):
            for j in range(self.numero_colunas):
                self.container[i][j].desenha(background)

    def get_espaco(self, linha_index, coluna_index):
        return self.container[linha_index][coluna_index]

    def checa_coluna_preenchida(self, numero_coluna):
        """Retorna Verdadeiro se o numero da coluna na borda está preenchido"""
        for i in range(len(self.container)):
            # se um espaço não estiver preenchido então a coluna não está preenchida
            if not self.container[i][numero_coluna].checa_espaco_preenchido():
                return False
        return True

    def insere_moeda(self, moeda, background, logica_jogo):
        """Insere a moeda na borda e atualiza o seu estado e representação interna"""

        numero_coluna = moeda.get_coluna()
        if not self.checa_coluna_preenchida(numero_coluna):
            linha_index = self.determina_linha_para_inserir(numero_coluna)
            self.container[linha_index][numero_coluna].set_moeda(moeda)
            if self.movimento_anterior[0] == None:
                self.estado_anterior = [[0 for j in range(self.numero_colunas)] for i in range(self.numero_linhas)]
            else:
                (linha_anterior, coluna_anterior, valor) = self.movimento_anterior
                self.estado_anterior[linha_anterior][coluna_anterior] = valor
            self.movimento_anterior = (linha_index, numero_coluna, moeda.get_tipo_moeda())
            self.estado[linha_index][numero_coluna] = moeda.get_tipo_moeda()
            self.atualizar_espaco_rastreado(linha_index, numero_coluna, moeda.get_tipo_moeda())
            self.numero_espacos_preenchidos += 1
            self.ultimo_valor = moeda.get_tipo_moeda()
            moeda.solta(background, linha_index)
        else:
            raise ColunaPreenchidaTotalmente('Coluna já está preenchida!')

        result = logica_jogo.checa_fim_de_jogo()

        return result

    def determina_linha_para_inserir(self, numero_coluna):
        for i in range(len(self.container)):
            if self.container[i][numero_coluna].checa_espaco_preenchido():
                return i - 1

        return self.numero_linhas - 1

    def get_dimensoes(self):
        return (self.numero_linhas, self.numero_colunas)

    def checa_borda_preenchida(self):
        return (self.total_espacos == self.numero_espacos_preenchidos)

    def get_representacao(self):
        return self.representacao

    def get_acoes_disponiveis(self):
        acoes = []
        for i in range(self.numero_colunas):
            if (not self.checa_coluna_preenchida(i)):
                acoes.append(i)
        return acoes

    def get_estado(self):
        result = tuple(tuple(x) for x in self.estado)

        return result

    def get_estado_anterior(self):
        result = tuple(tuple(x) for x in self.estado_anterior)

        return result

    def get_ultima_informacao_preenchida(self):
        return (self.ultimo_nodo_visitado, self.ultimo_valor)

    def atualizar_espaco_rastreado(self, i, j, tipo_moeada):
        self.ultimo_nodo_visitado = []
        nodo_inicial = self.representacao[i][j]
        nodo_inicial.value = tipo_moeada
        self.atravessa(nodo_inicial, tipo_moeada, i, j, self.ultimo_nodo_visitado)
        # reseta todos os nodos se eles não foram visitados
        for indices in self.ultimo_nodo_visitado:
            self.representacao[indices[0]][indices[1]].visited = False

    def atravessa(self, nodo_atual, valor_desejado, i, j, nodos_visitados):
        """Atualiza recursivamente as pontuações dos nodos relevantes com base em seus nós adjacentes"""

        nodo_atual.visited = True
        nodos_visitados.append((i, j))
        if nodo_atual.top_left:
            nodo_top_left = nodo_atual.top_left
            if nodo_top_left.value == valor_desejado:
                nodo_atual.top_left_score = nodo_top_left.top_left_score + 1
                if not nodo_top_left.visited:
                    self.atravessa(nodo_top_left, valor_desejado, i - 1, j - 1, nodos_visitados)

        if nodo_atual.top:
            nodo_top = nodo_atual.top
            if nodo_top.value == valor_desejado:
                nodo_atual.top_score = nodo_top.top_score + 1
                if not nodo_top.visited:
                    self.atravessa(nodo_top, valor_desejado, i - 1, j, nodos_visitados)

        if nodo_atual.top_right:
            nodo_top_rigth = nodo_atual.top_right
            if nodo_top_rigth.value == valor_desejado:
                nodo_atual.top_right_score = nodo_top_rigth.top_right_score + 1
                if not nodo_top_rigth.visited:
                    self.atravessa(nodo_top_rigth, valor_desejado, i - 1, j + 1, nodos_visitados)

        if nodo_atual.left:
            nodo_left = nodo_atual.left
            if nodo_left.value == valor_desejado:
                nodo_atual.left_score = nodo_left.left_score + 1
                if not nodo_left.visited:
                    self.atravessa(nodo_left, valor_desejado, i, j - 1, nodos_visitados)

        if nodo_atual.right:
            nodo_rigth = nodo_atual.right
            if nodo_rigth.value == valor_desejado:
                nodo_atual.right_score = nodo_rigth.right_score + 1
                if not nodo_rigth.visited:
                    self.atravessa(nodo_rigth, valor_desejado, i, j + 1, nodos_visitados)

        if nodo_atual.bottom_left:
            nodo_bottom_left = nodo_atual.bottom_left
            if nodo_bottom_left.value == valor_desejado:
                nodo_atual.bottom_left_score = nodo_bottom_left.bottom_left_score + 1
                if not nodo_bottom_left.visited:
                    self.atravessa(nodo_bottom_left, valor_desejado, i + 1, j - 1, nodos_visitados)

        if nodo_atual.bottom:
            nodo_bottom = nodo_atual.bottom
            if nodo_bottom.value == valor_desejado:
                nodo_atual.bottom_score = nodo_bottom.bottom_score + 1
                if not nodo_bottom.visited:
                    self.atravessa(nodo_bottom, valor_desejado, i + 1, j, nodos_visitados)

        if nodo_atual.bottom_right:
            nodo_bottom_right = nodo_atual.bottom_right
            if nodo_bottom_right.value == valor_desejado:
                nodo_atual.bottom_right_score = nodo_bottom_right.bottom_right_score + 1
                if not nodo_bottom_right.visited:
                    self.atravessa(nodo_bottom_right, valor_desejado, i + 1, j + 1, nodos_visitados)


class Moeda():
    RAIO = 30

    def __init__(self, tipo_moeda):
        self.tipo_moeda = tipo_moeda
        self.surface = pygame.Surface((EspacoMoedas.TAMANHO - 3, EspacoMoedas.TAMANHO - 3))
        if self.tipo_moeda == 1:
            self.cor = AZUL
        else:
            self.cor = VERMELHO

    def set_posicao(self, x1, y1):
        self.x_pos = x1
        self.y_pos = y1

    def set_coluna(self, coluna):
        self.coluna = coluna

    def get_coluna(self):
        return self.coluna

    def set_linha(self, linha):
        self.linha = linha

    def get_linha(self):
        return self.linha

    def mover_direita(self, background, step=1):
        self.set_coluna(self.coluna + 1)
        self.surface.fill((0, 0, 0))
        background.blit(self.surface, (self.x_pos, self.y_pos))
        self.set_posicao(self.x_pos + step * EspacoMoedas.TAMANHO, self.y_pos)
        self.desenha(background)

    def mover_esquerda(self, background):
        self.set_coluna(self.coluna - 1)
        self.surface.fill((0, 0, 0))
        background.blit(self.surface, (self.x_pos, self.y_pos))
        self.set_posicao(self.x_pos - EspacoMoedas.TAMANHO, self.y_pos)
        self.desenha(background)

    def solta(self, background, numero_linha):
        self.set_linha(numero_linha)
        self.surface.fill((0, 0, 0))
        background.blit(self.surface, (self.x_pos, self.y_pos))
        self.set_posicao(self.x_pos, self.y_pos + ((self.linha + 1) * EspacoMoedas.TAMANHO))
        self.surface.fill((255, 255, 255))
        background.blit(self.surface, (self.x_pos, self.y_pos))
        self.desenha(background)

    def get_tipo_moeda(self):
        return self.tipo_moeda

    def desenha(self, background):
        pygame.draw.circle(self.surface, self.cor, (EspacoMoedas.TAMANHO // 2, EspacoMoedas.TAMANHO // 2), Moeda.RAIO)
        self.surface = self.surface.convert()
        background.blit(self.surface, (self.x_pos, self.y_pos))


class VisaoJogo(object):

    def __init__(self, width=640, height=400, fps=30):
        """Inicializa pygame, janela, fundo, fonte"""
        pygame.init()
        pygame.display.set_caption("ESC para sair")
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0
        self.font = pygame.font.SysFont('mono', 20, bold=True)
        self.pc_treinado = None
        self.lst_vitoria = [0, 0]

    def inicializa_variaveis(self, modo_de_jogo):
        """Inicializa a borda do jogo e objeto de lógica"""
        self.borda_do_jogo = Borda(TAMANHO_BORDA[0], TAMANHO_BORDA[1])
        (self.linhas_bordas, self.colunas_bordas) = self.borda_do_jogo.get_dimensoes()
        self.logica_jogo = LogicaJogo(self.borda_do_jogo)
        primeiro_tipo_moeda = random.randint(1, 2)
        segundo_tipo_moeda = 2 if primeiro_tipo_moeda == 1 else 1

        if modo_de_jogo == "sozinho":
            self.p1 = JogadorHumano(primeiro_tipo_moeda)
            if (self.pc_treinado == None):
                self.p2 = JogadorPC(segundo_tipo_moeda, "qlearner")
                self.pc_treinado = self.p2
            else:
                self.pc_treinado.set_tipo_moeda(segundo_tipo_moeda)
                self.p2 = self.pc_treinado
        elif modo_de_jogo == "2_player":
            self.p1 = JogadorHumano(primeiro_tipo_moeda)
            self.p2 = JogadorHumano(segundo_tipo_moeda)
        else:
            self.pc_treinado = None
            self.lst_vitoria = [0, 0]
            self.p1 = JogadorPC(primeiro_tipo_moeda, "qlearner")
            self.p2 = JogadorPC(segundo_tipo_moeda, "qlearner")

    def main_menu(self, iteracoes=20):
        main_menu = True
        jogar_jogo = False
        self.background.fill(BRANCO)
        self.desenhar_menu()

        while main_menu:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if self.rect1.collidepoint(pos):
                        jogar_jogo = True
                        main_menu = False
                        modo_jogo = "2_player"
                    elif self.rect2.collidepoint(pos):
                        jogar_jogo = True
                        main_menu = False
                        modo_jogo = "sozinho"
                    elif self.rect3.collidepoint(pos):
                        jogar_jogo = True
                        main_menu = False
                        modo_jogo = "treino"
                    elif self.rect4.collidepoint(pos):
                        main_menu = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        main_menu = False

            milliseconds = self.clock.tick(self.fps)
            self.playtime += milliseconds / 1000.0
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))

        if not jogar_jogo:
            pygame.quit()

        elif modo_jogo == "treino":
            self.run(modo_jogo, iteracoes)

        else:
            self.run(modo_jogo)

    def run(self, modo_jogo, iteracoes=1):
        """Principal loop no jogo"""
        while (iteracoes > 0):
            self.inicializa_variaveis(modo_jogo)
            self.background.fill(PRETO)
            self.borda_do_jogo.desenha(self.background)
            fim_de_jogo = False
            fim_de_turno = False
            nao_inicializado = True
            tipo_atual = random.randint(1, 2)
            if modo_jogo == "sozinho":
                turno_humano = (self.p1.get_tipo_moeda() == tipo_atual)
            elif modo_jogo == "2_player":
                turno_humano = True
            else:
                turno_humano = False

            turno_p1 = (self.p1.get_tipo_moeda() == tipo_atual)

            (primeiro_espaco_X, primeiro_espaco_Y) = self.borda_do_jogo.get_espaco(0, 0).get_posicao()
            moeda = Moeda(tipo_atual)
            tela_fim_de_jogo = False

            while not fim_de_jogo:

                if nao_inicializado:
                    moeda = Moeda(tipo_atual)
                    moeda.set_posicao(primeiro_espaco_X, primeiro_espaco_Y - EspacoMoedas.TAMANHO)
                    moeda.set_coluna(0)
                    nao_inicializado = False
                    moeda_inserida = False

                moeda.desenha(self.background)

                jogador_atual = self.p1 if turno_p1 else self.p2

                if not turno_humano:
                    fim_de_jogo = jogador_atual.movimento_completo(moeda, self.borda_do_jogo, self.logica_jogo,
                                                                   self.background)
                    moeda_inserida = True
                    nao_inicializado = True

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        fim_de_jogo = True
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            fim_de_jogo = True
                        if event.key == pygame.K_RIGHT and turno_humano:
                            if (moeda.get_coluna() + 1 < self.colunas_bordas):
                                moeda.mover_direita(self.background)
                        elif event.key == pygame.K_LEFT and turno_humano:
                            if (moeda.get_coluna() - 1 >= 0):
                                moeda.mover_esquerda(self.background)
                        elif event.key == pygame.K_RETURN and turno_humano and not moeda_inserida:
                            try:
                                fim_de_jogo = self.borda_do_jogo.insere_moeda(moeda, self.background, self.logica_jogo)
                                jogador_atual.movimento_completo()
                                nao_inicializado = True
                                moeda_inserida = True
                            except ColunaPreenchidaTotalmente as e:
                                pass

                if fim_de_jogo:
                    ganhador = self.logica_jogo.determina_nome_ganhador()
                    ganhador_valor = self.logica_jogo.get_ganhador()
                    if (ganhador_valor > 0 and modo_jogo == "treino"):
                        self.lst_vitoria[ganhador_valor - 1] += 1
                    tela_fim_de_jogo = True

                if moeda_inserida:
                    if modo_jogo == "sozinho":
                        turno_humano = not turno_humano
                    tipo_atual = 1 if tipo_atual == 2 else 2
                    turno_p1 = not turno_p1

                milliseconds = self.clock.tick(self.fps)
                self.playtime += milliseconds / 1000.0
                pygame.display.flip()
                self.screen.blit(self.background, (0, 0))

            iteracoes -= 1

        if modo_jogo == "treino":
            index = self.lst_vitoria.index(max(self.lst_vitoria))
            self.pc_treinado = self.p1 if index == 0 else self.p2
            self.main_menu()
        else:
            self.visao_fim_de_jogo(ganhador)

    def desenhar_menu(self):
        font = pygame.font.SysFont('mono', 60, bold=True)
        self.titulo_surface = font.render('CONNECT 4', True, PRETO)
        fw, fh = font.size('CONNECT 4')
        self.background.blit(self.titulo_surface, ((self.width - fw) // 2, 150))
        texto_dois_jogadores = '2 Jogadores'
        texto_pc_jogador = 'vs PC'
        texto_treino = 'Treinar PC'
        texto_sair = 'Sair'
        font = pygame.font.SysFont('mono', 40, bold=True)

        self.play_surface = font.render(texto_dois_jogadores, True, PRETO)
        fw, fh = font.size(texto_dois_jogadores)
        self.rect1 = self.play_surface.get_rect(topleft=((self.width - fw) // 2, 300))
        self.background.blit(self.play_surface, ((self.width - fw) // 2, 300))

        computer_play_surface = font.render(texto_pc_jogador, True, PRETO)
        fw, fh = font.size(texto_pc_jogador)
        self.rect2 = computer_play_surface.get_rect(topleft=((self.width - fw) // 2, 350))
        self.background.blit(computer_play_surface, ((self.width - fw) // 2, 350))

        self.train_surface = font.render(texto_treino, True, PRETO)
        fw, fh = font.size(texto_treino)
        self.rect3 = self.train_surface.get_rect(topleft=((self.width - fw) // 2, 400))
        self.background.blit(self.train_surface, ((self.width - fw) // 2, 400))

        self.quit_surface = font.render(texto_sair, True, PRETO)
        fw, fh = font.size(texto_sair)
        self.rect4 = self.quit_surface.get_rect(topleft=((self.width - fw) // 2, 450))
        self.background.blit(self.quit_surface, ((self.width - fw) // 2, 450))

    def visao_fim_de_jogo(self, ganhador):
        tela_fim_jogo = True
        main_menu = False
        self.background.fill(BRANCO)
        self.desenha_fim_de_jogo(ganhador)

        while tela_fim_jogo:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.rect1.collidepoint(pygame.mouse.get_pos()):
                        main_menu = True
                        tela_fim_jogo = False
                    elif self.rect2.collidepoint(pygame.mouse.get_pos()):
                        tela_fim_jogo = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        tela_fim_jogo = False

            milliseconds = self.clock.tick(self.fps)
            self.playtime += milliseconds / 1000.0
            pygame.display.flip()
            self.screen.blit(self.background, (0, 0))

        if not main_menu:
            pygame.quit()
        else:
            self.main_menu()

    def desenha_fim_de_jogo(self, ganhador):
        font = pygame.font.SysFont('mono', 60, bold=True)
        texto_fim_de_jogo = 'FIM DE JOGO'
        self.titulo_surface = font.render(texto_fim_de_jogo, True, VERDE)
        fw, fh = font.size(texto_fim_de_jogo)
        self.background.blit(self.titulo_surface, ((self.width - fw) // 2, 150))
        texto_jogar_novamento = 'Retornar ao Menu Principal'
        texto_sair = 'SAIR'
        if ganhador != 'Empate':
            texto_ganhador = ganhador + " ganhou!"
        else:
            texto_ganhador = "Houve um " + ganhador + "!"
        font = pygame.font.SysFont('mono', 40, bold=True)
        winner_surface = font.render(texto_ganhador, True, PRETO)
        fw, fh = font.size(texto_ganhador)
        self.background.blit(winner_surface, ((self.width - fw) // 2, 300))

        font = pygame.font.SysFont('mono', 40, bold=False)
        self.play_surface = font.render(texto_jogar_novamento, True, (0, 0, 0))
        fw, fh = font.size(texto_jogar_novamento)
        self.rect1 = self.play_surface.get_rect(topleft=((self.width - fw) // 2, 360))
        self.background.blit(self.play_surface, ((self.width - fw) // 2, 360))

        self.quit_surface = font.render(texto_sair, True, (0, 0, 0))
        fw, fh = font.size(texto_sair)
        self.rect2 = self.quit_surface.get_rect(topleft=((self.width - fw) // 2, 410))
        self.background.blit(self.quit_surface, ((self.width - fw) // 2, 410))


class LogicaJogo():
    """Seta as condições de vitória e determina o vencedor"""
    SEQUENCIA_VITORIA_LENGTH = 4

    def __init__(self, borda):
        self.borda = borda
        (numero_linhas, numero_colunas) = self.borda.get_dimensoes()
        self.linhas_bordas = numero_linhas
        self.colunas_bordas = numero_colunas
        self.valor_ganhador = 0

    def checa_fim_de_jogo(self):
        """Checa se o jogo terminou, que pode ter sido por um empato ou um dos 2 jogadores tiver ganhado"""
        (ultimo_nodo_visitado, valor_jogador) = self.borda.get_ultima_informacao_preenchida()
        representacao = self.borda.get_representacao()
        jogador_ganhador = self.pesquisa_ganhador(ultimo_nodo_visitado, representacao)
        if jogador_ganhador:
            self.valor_ganhador = valor_jogador

        return ( jogador_ganhador or self.borda.checa_borda_preenchida() )

    def pesquisa_ganhador(self, ultimo_nodo_visitado, representacao):
        """"Determina se algum dos 2 jogadores ganhou"""
        for indices in ultimo_nodo_visitado:
            nodo_atual = representacao[indices[0]][indices[1]]
            if (nodo_atual.top_left_score == LogicaJogo.SEQUENCIA_VITORIA_LENGTH or
                    nodo_atual.top_score == LogicaJogo.SEQUENCIA_VITORIA_LENGTH or
                    nodo_atual.top_right_score == LogicaJogo.SEQUENCIA_VITORIA_LENGTH or
                    nodo_atual.left_score == LogicaJogo.SEQUENCIA_VITORIA_LENGTH or
                    nodo_atual.right_score == LogicaJogo.SEQUENCIA_VITORIA_LENGTH or
                    nodo_atual.bottom_left_score == LogicaJogo.SEQUENCIA_VITORIA_LENGTH or
                    nodo_atual.bottom_score == LogicaJogo.SEQUENCIA_VITORIA_LENGTH or
                    nodo_atual.bottom_right_score == LogicaJogo.SEQUENCIA_VITORIA_LENGTH):
                return True

        return False

    def determina_nome_ganhador(self):
        if (self.valor_ganhador == 1):
            return "AZUL"
        elif (self.valor_ganhador == 2):
            return "VERMELHO"
        else:
            return "Empate"

    def get_ganhador(self):
        """"Retorna o valor do tipo da moeda do ganhador"""
        return self.valor_ganhador


# region Jogadores

class Player():

    def __init__(self, tipo_moeda):
        self.tipo_moeda = tipo_moeda

    def movimento_completo(self):
        """Faz uma mudança e atualiza qualquer parâmetro de aprendizado, se houver"""
        pass

    def get_tipo_moeda(self):
        return self.tipo_moeda

    def set_tipo_moeda(self, tipo_moeda):
        self.tipo_moeda = tipo_moeda


class JogadorHumano(Player):

    def __init__(self, tipo_moeda):
        Player.__init__(self, tipo_moeda)


class JogadorPC(Player):

    def __init__(self, tipo_moeda, tipo_jogador):
        if (tipo_jogador == "random"):
            self.jogador = JogadorRandom(tipo_moeda)
        else:
            self.jogador = JogadorQLearningPlayer(tipo_moeda)

    def movimento_completo(self, moeda, borda, logica_jogo, background):
        acoes = borda.get_acoes_disponiveis()
        estado = borda.get_estado()
        acao_escolhida = self.escolher_acao(estado, acoes)
        moeda.mover_direita(background, acao_escolhida)
        moeda.set_coluna(acao_escolhida)
        fim_de_jogo = borda.insere_moeda(moeda, background, logica_jogo)
        self.jogador.aprender(borda, acoes, acao_escolhida, fim_de_jogo, logica_jogo)

        return fim_de_jogo

    def get_tipo_moeda(self):
        return self.jogador.get_tipo_moeda()

    def escolher_acao(self, estado, acoes):
        return self.jogador.escolher_acao(estado, acoes)


class JogadorRandom(Player):

    def __init__(self, tipo_moeda):
        Player.__init__(self, tipo_moeda)

    def escolher_acao(self, estado, acoes):
        return random.choice(acoes)

    def aprender(self, borda, acao, fim_de_jogo, logica_jogo):
        """O jogador aleatório não aprende com suas ações"""
        pass


class JogadorQLearningPlayer(Player):

    def __init__(self, tipo_moeda, epsilon=0.2, alpha=0.3, gamma=0.9):
        Player.__init__(self, tipo_moeda)
        self.q = {}
        self.epsilon = epsilon  # chance de exploração aleatória
        self.alpha = alpha  # taxa de aprendizado
        self.gamma = gamma  # fator de desconto para recompensas futuras

    def getQ(self, estado, acao):
        if self.q.get((estado, acao)) is None:
            self.q[(estado, acao)] = 1.0
        return self.q.get((estado, acao))

    def escolher_acao(self, estado, acoes):
        estado_atual = estado

        if random.random() <= self.epsilon:
            acao_escolhida = random.choice(acoes)
            return acao_escolhida

        qs = [self.getQ(estado_atual, a) for a in acoes]
        maxQ = max(qs)

        if qs.count(maxQ) > 1:
            # mais de uma melhor opção
            melhores_opcoes = [i for i in range(len(acoes)) if qs[i] == maxQ]
            i = random.choice(melhores_opcoes)
        else:
            i = qs.index(maxQ)

        return acoes[i]

    def aprender(self, borda, acoes, acao_escolhida, fim_de_jogo, logica_jogo):
        recompensa = 0
        if (fim_de_jogo):
            valor_ganhador = logica_jogo.get_ganhador()
            if valor_ganhador == 0:
                recompensa = 0.5
            elif valor_ganhador == self.tipo_moeda:
                recompensa = 1
            else:
                recompensa = -2
        estado_anterior = borda.get_estado_anterior()
        anterior = self.getQ(estado_anterior, acao_escolhida)
        estado_resultado = borda.get_estado()
        maxqnew = max([self.getQ(estado_resultado, a) for a in acoes])
        self.q[(estado_anterior, acao_escolhida)] = anterior + self.alpha * ((recompensa + self.gamma * maxqnew) - anterior)

# endregion


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('iterations', nargs='?', default=50, action="store",
                        help="Armazene o número de iterações para treinar o computador")
    args = parser.parse_args()

    VisaoJogo(1200, 760).main_menu(int(args.iterations))
