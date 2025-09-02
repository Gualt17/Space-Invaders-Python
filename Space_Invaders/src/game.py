import pygame
import random

import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from common.game_state import GameState
from common.asset_manager import AssetManager
from common.player import Player
from common.shoot import Shoot, EnemyShot
from common.enemy import Enemy
from common.button import Button

class Game:
    def __init__(self):
        pygame.init()

        # Inizializzazione assets manager
        self.assets = AssetManager()
        # Caricamento degli asset audio
        self._load_audio_assets()

        # Inizializzazione schermo
        self.grid_width, self.grid_height, self.cell_size = 15, 20, 40
        self.sidebar_width = 200  # Larghezza sidebar
        # Area di gioco + sidebar
        self.screen_width = self.grid_width * self.cell_size + self.sidebar_width
        self.screen_height = self.grid_height * self.cell_size
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Space Invaders")

        # Inizializzazione sfondo
        self.background = self.assets.load_background("images/menu_background.jpg", (self.screen_width, self.screen_height))

        # Inizializzazione logo
        self.logo = self.assets.load_image("images/game_logo.png")
        self.logo = pygame.transform.scale(self.logo, (300, 150)) if self.logo else None

        # Inizializzazione giocatore
        self.player = Player(
            x = self.screen_width // 2 - 25,
            y = self.screen_height - 60,
            width = 50,
            height = 50,
            screen_width = self.screen_width,
            asset_manager=self.assets
        )

        # Inizializzazione variabili di stato
        self.DEBUG_MODE = False  # Imposta a False per nascondere la griglia
        self.grid_surface = None
        self._init_debug_grid()

        self.score = 0
        self.lives = 3
        self.bullets = []
        self.enemies = []
        self._init_enemies()
        self.enemy_shots = []
        self.enemy_shot_cooldown = 0
        self.enemy_shot_frequency = 60  # Frame tra i colpi
        self.current_state = GameState.MENU

        # Inizializzazione bottoni
        self._init_menu_buttons()
        self._init_result_buttons()

        self.clock = pygame.time.Clock()
        self.running = True

        # Inizializzazione bottoni
        self._init_menu_buttons()
        self._init_result_buttons()

    def _load_audio_assets(self):
        """Carica tutti gli asset audio necessari"""
        # Musica di sottofondo
        self.assets.load_music("sounds/background_music.mp3", volume=0.5)
        
        # Effetti sonori
        self.assets.load_sound("sounds/shoot.wav", volume=0.3)
        self.assets.load_sound("sounds/explosion.wav", volume=0.3)

    # INIZIALIZZAZIONE GRIGLIA PER DEBUG
    def _init_debug_grid(self):
        if self.DEBUG_MODE:
            # Crea la griglia solo per l'area di gioco (senza sidebar)
            self.grid_surface = self._create_grid_surface(
                self.screen_width,  # Solo area di gioco
                self.screen_height,
                self.cell_size,
                (160, 160, 160)  # Colore grigio chiaro
            )
            
    def _create_grid_surface(self, width, height, cell_size, color):
        grid_surface = pygame.Surface((width, height), pygame.SRCALPHA)

        for x in range(0, width, cell_size):
            pygame.draw.line(grid_surface, color, (x, 0), (x, height))
        for y in range(0, height, cell_size):
            pygame.draw.line(grid_surface, color, (0, y), (width, y))

        return grid_surface

    def _draw_sidebar(self):
        """Disegna la barra laterale con punteggio e vite - SOLO in PLAYING"""
        if self.current_state != GameState.PLAYING:
            return
        
        sidebar_rect = pygame.Rect(self.grid_width * self.cell_size, 0, 
                                self.sidebar_width, self.screen_height)
        
        # Sfondo sidebar
        pygame.draw.rect(self.screen, (50, 50, 50), sidebar_rect)
        
        # Punteggio
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (sidebar_rect.x + 10, 30))
        
        # Vite
        lives_text = font.render("Lives:", True, (255, 255, 255))
        self.screen.blit(lives_text, (sidebar_rect.x + 10, 80))
        
        for i in range(self.lives):
            pygame.draw.circle(self.screen, (255, 0, 0),
                            (sidebar_rect.x + 30 + i * 40, 120), 15)
            
    def start_action(self):
        '''
            Impostazione stato di gioco
            Avvio musica
        '''

        print("Avvio il gioco!")
        self.current_state = GameState.PLAYING
        self.assets.play_music()

    def quit_action(self):
        '''
            Stop finestra di gioco
        '''

        self.running = False

    def _init_enemies(self):
        # Crea una formazione di nemici ordinata da sinistra a destra
        enemies = []
        for row in range(3):
            for col in range(8):
                x = 100 + col * 50
                y = 50 + row * 50
                enemies.append(Enemy(x, y, self.assets))  # Passa l'asset_manager
        
        # Ordina i nemici per coordinata x (importante per il nuovo movimento)
        self.enemies = sorted(enemies, key=lambda e: e.rect.x)

    def reset_game(self):
        """Resetta completamente lo stato del gioco"""
        # Pulisci tutte le liste
        self.enemies.clear()
        self.bullets.clear()
        self.enemy_shots.clear()
        
        # Re-inizializza i nemici
        self._init_enemies()
        
        # Resetta il giocatore
        self.player.reset()
        self.player.rect.x = self.screen_width // 2 - 25
        self.player.rect.y = self.screen_height - 60
        
        # Resetta le variabili di stato
        self.score = 0
        self.lives = 3
        self.enemy_shot_cooldown = 0
        
        # Ripristina lo stato di gioco
        self.current_state = GameState.PLAYING
        
        # Re-inizializza la griglia di debug se necessario
        self._init_debug_grid()
        
        # Gestione musica
        self.assets.stop_music()
        self.assets.play_music()
        
        # Forza un render immediato
        self.render()
        pygame.display.flip()
            
    def _init_menu_buttons(self):
        """Inizializza i bottoni del menu principale"""
        button_width, button_height = 200, 50
        center_x = self.screen_width // 2 - button_width // 2
        
        # Riorganizza i bottoni con più spazio e posizione migliore
        self.menu_buttons = [
            Button(
                center_x, 300, button_width, button_height,
                "Start",
                color=(50, 120, 50),
                hover_color=(70, 150, 70),
                text_color=(255, 255, 255),
                action=self.start_action
            ),
            Button(
                center_x, 380, button_width, button_height,
                "How to Play",
                color=(50, 50, 120),
                hover_color=(70, 70, 150),
                text_color=(255, 255, 255),
                action=self.show_instructions
            ),
            Button(
                center_x, 460, button_width, button_height,
                "Quit",
                color=(120, 50, 50),
                hover_color=(150, 70, 70),
                text_color=(255, 255, 255),
                action=self.quit_action
            )
        ]

    def _init_result_buttons(self):
        """Inizializza i bottoni per gli schermi di vittoria/sconfitta"""
        button_width, button_height = 200, 50
        center_x = self.screen_width // 2 - button_width // 2
        
        # Bottoni condivisi per VICTORY e GAMEOVER
        self.victory_buttons = [
            Button(
                center_x, 300, button_width, button_height,  # Spostato più in basso
                "Play Again",
                color=(50, 120, 50),
                hover_color=(70, 150, 70),
                text_color=(255, 255, 255),
                action=self.reset_game
            ),
            Button(
                center_x, 380, button_width, button_height,
                "Main Menu",
                color=(50, 50, 120),
                hover_color=(70, 70, 150),
                text_color=(255, 255, 255),
                action=self.return_to_menu
            ),
            Button(
                center_x, 460, button_width, button_height,
                "Quit",
                color=(120, 50, 50),
                hover_color=(150, 70, 70),
                text_color=(255, 255, 255),
                action=self.quit_action
            )
        ]
        
        self.gameover_buttons = [
            Button(
                center_x, 300, button_width, button_height,
                "Retry",
                color=(50, 120, 50),
                hover_color=(70, 150, 70),
                text_color=(255, 255, 255),
                action=self.reset_game
            ),
            Button(
                center_x, 380, button_width, button_height,
                "Main Menu",
                color=(50, 50, 120),
                hover_color=(70, 70, 150),
                text_color=(255, 255, 255),
                action=self.return_to_menu
            ),
            Button(
                center_x, 460, button_width, button_height,
                "Quit",
                color=(120, 50, 50),
                hover_color=(150, 70, 70),
                text_color=(255, 255, 255),
                action=self.quit_action
            )
        ]
        
        # Aggiungi stato per le istruzioni
        self.instructions_shown = False

    def show_instructions(self):
        """Mostra le istruzioni del gioco"""
        self.instructions_shown = True

    def return_to_menu(self):
        """Torna al menu principale e resetta il gioco"""
        self.reset_game()
        self.current_state = GameState.MENU
        self.instructions_shown = False
        self.assets.stop_music()

    def handle_events(self):
        """Gestisce tutti gli eventi del gioco"""
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Gestione bottoni in base allo stato corrente
            if self.current_state == GameState.MENU and not self.instructions_shown:
                for button in self.menu_buttons:
                    if button.handle_event(event, mouse_pos):
                        self.render()  # Forza il render dopo il click
                        return

            elif self.current_state == GameState.VICTORY:
                for button in self.victory_buttons:
                    if button.handle_event(event, mouse_pos):
                        self.render()  # Forza il render dopo il click
                        return

            elif self.current_state == GameState.GAMEOVER:
                for button in self.gameover_buttons:
                    if button.handle_event(event, mouse_pos):
                        self.render()  # Forza il render dopo il click
                        return

            elif self.current_state == GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.player.set_moving("left", True)
                    elif event.key == pygame.K_RIGHT:
                        self.player.set_moving("right", True)
                    elif event.key == pygame.K_SPACE:
                        bullet = self.player.shoot()
                        if bullet:
                            self.bullets.append(bullet)
                            self.assets.play_sound("sounds/shoot.wav")
                
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        self.player.set_moving("left", False)
                    elif event.key == pygame.K_RIGHT:
                        self.player.set_moving("right", False)

    def update(self):
        """Aggiorna lo stato del gioco"""
        if hasattr(self, 'skip_checks') and self.skip_checks:
            self.skip_checks = False
            return
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Aggiorna hover per tutti i bottoni visibili
        if self.current_state == GameState.MENU:
            for button in self.menu_buttons:
                button.check_hover(mouse_pos)
        elif self.current_state == GameState.VICTORY:
            for button in self.victory_buttons:
                button.check_hover(mouse_pos)
        elif self.current_state == GameState.GAMEOVER:
            for button in self.gameover_buttons:
                button.check_hover(mouse_pos)

        elif self.current_state == GameState.PLAYING:
            self.player.update()
            
            # Movimento nemici
            edge_hit = False
            if self.enemies:
                if self.enemies[0].direction > 0:
                    rightmost = max(enemy.rect.right for enemy in self.enemies)
                    if rightmost >= self.grid_width * self.cell_size:
                        edge_hit = True
                else:
                    leftmost = min(enemy.rect.left for enemy in self.enemies)
                    if leftmost <= 0:
                        edge_hit = True
            
            if edge_hit:
                for enemy in self.enemies:
                    enemy.move_down()
            
            for enemy in self.enemies:
                enemy.update(self.grid_width * self.cell_size)
            
            # Sparo nemico casuale
            if self.enemies and self.enemy_shot_cooldown <= 0:
                shooter = random.choice(self.enemies)
                self.enemy_shots.append(EnemyShot(
                    shooter.rect.centerx - 2,
                    shooter.rect.bottom
                ))
                self.enemy_shot_cooldown = self.enemy_shot_frequency
            else:
                self.enemy_shot_cooldown -= 1
            
            # Aggiorna proiettili giocatore
            for bullet in self.bullets[:]:
                bullet.update()
                if not bullet.active:
                    self.bullets.remove(bullet)
            
            # Aggiorna colpi nemici
            for shot in self.enemy_shots[:]:
                shot.update()
                if not shot.active:
                    self.enemy_shots.remove(shot)
            
            # Controlla collisioni
            self._check_collisions()
            self._check_game_conditions()

    def _check_collisions(self):
        # Non controllare le collisioni se stiamo saltando i controlli
        if hasattr(self, 'skip_checks') and self.skip_checks:
            return

        # Collisione proiettili giocatore con nemici
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.assets.play_sound("sounds/explosion.wav")  # Suono nemico colpito
                    self.score += 100  # Aggiungi 100 punti per ogni nemico ucciso
                    break
        
        # Collisione colpi nemici con giocatore
        for shot in self.enemy_shots[:]:
            if shot.rect.colliderect(self.player.rect):
                self.enemy_shots.remove(shot)
                self.lives -= 1
                if self.lives <= 0:
                    self.current_state = GameState.GAMEOVER
                break

    def _check_game_conditions(self):
        # Non controllare le condizioni se stiamo saltando i controlli
        if hasattr(self, 'skip_checks') and self.skip_checks:
            return
            
        # Vittoria: tutti i nemici eliminati
        if not self.enemies and self.current_state == GameState.PLAYING:
            self.current_state = GameState.VICTORY
            return
        
        # Game Over: nemici raggiungono il giocatore o vite esaurite
        player_line = self.player.rect.y
        for enemy in self.enemies:
            if enemy.rect.bottom >= player_line and self.current_state == GameState.PLAYING:
                self.current_state = GameState.GAMEOVER
                return

    # Renderizza elementi a schermo
    def render(self):
        """Renderizza tutti gli elementi del gioco in base allo stato corrente"""
        # Sfondo
        self.screen.blit(self.background, (0, 0))
        
        # Griglia di debug (se attiva)
        if self.DEBUG_MODE and self.grid_surface:
            self.screen.blit(self.grid_surface, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Render in base allo stato corrente
        if self.current_state == GameState.MENU:
            if not self.instructions_shown:
                # Logo del gioco
                if self.logo:
                    logo_rect = self.logo.get_rect(center=(self.screen_width//2, 120))
                    self.screen.blit(self.logo, logo_rect)
                
                # Bottoni del menu
                for button in self.menu_buttons:
                    button.check_hover(mouse_pos)
                    button.draw(self.screen)
            else:
                # Schermata delle istruzioni
                self._render_instructions()
                
        elif self.current_state == GameState.PLAYING:
            # Elementi di gioco
            self.player.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for bullet in self.bullets:
                bullet.draw(self.screen)
            for shot in self.enemy_shots:
                shot.draw(self.screen)
            
            # Sidebar con punteggio e vite
            self._draw_sidebar()
            
        elif self.current_state == GameState.VICTORY:
            # Messaggio di vittoria
            font = pygame.font.SysFont(None, 72)
            text = font.render("VICTORY!", True, (0, 255, 0))
            text_rect = text.get_rect(center=(self.screen_width//2, 150))
            self.screen.blit(text, text_rect)
            
            # Punteggio finale
            score_font = pygame.font.SysFont(None, 48)
            score_text = score_font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(self.screen_width//2, 220))
            self.screen.blit(score_text, score_rect)
            
            # Bottoni
            for button in self.victory_buttons:
                button.check_hover(mouse_pos)
                button.draw(self.screen)
                
        elif self.current_state == GameState.GAMEOVER:
            # Messaggio di game over
            font = pygame.font.SysFont(None, 72)
            text = font.render("GAME OVER", True, (255, 0, 0))
            text_rect = text.get_rect(center=(self.screen_width//2, 150))
            self.screen.blit(text, text_rect)
            
            # Punteggio finale
            score_font = pygame.font.SysFont(None, 48)
            score_text = score_font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(self.screen_width//2, 220))
            self.screen.blit(score_text, score_rect)
            
            # Bottoni
            for button in self.gameover_buttons:
                button.check_hover(mouse_pos)
                button.draw(self.screen)
        
        # Aggiornamento dello schermo
        pygame.display.flip()

    def _render_instructions(self):
        """Renderizza la schermata delle istruzioni"""
        # Titolo
        font = pygame.font.SysFont(None, 72)
        title = font.render("HOW TO PLAY", True, (255, 255, 0))
        title_rect = title.get_rect(center=(self.screen_width//2, 80))
        self.screen.blit(title, title_rect)
        
        # Istruzioni
        instructions = [
            "Use LEFT and RIGHT arrow keys to move",
            "Press SPACE to shoot",
            "Destroy all aliens to win",
            "Don't let them reach you!",
            "Avoid their shots to survive"
        ]
        
        font = pygame.font.SysFont(None, 36)
        for i, line in enumerate(instructions):
            text = font.render(line, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen_width//2, 180 + i * 40))
            self.screen.blit(text, text_rect)
        
        # Bottone per tornare indietro
        back_button = Button(
            self.screen_width//2 - 100, 400, 200, 50,
            "Back to Menu",
            color=(50, 50, 120),
            hover_color=(70, 70, 150),
            text_color=(255, 255, 255),
            action=self.return_to_menu
        )
        
        mouse_pos = pygame.mouse.get_pos()
        back_button.check_hover(mouse_pos)
        
        # Gestione degli eventi per il bottone back
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.is_hovered:
                    back_button.action()
        
        back_button.draw(self.screen)

    # Avvio del gioco
    def run(self):
        while self.running:
            self.handle_events()
            
            # Aggiorna solo se in stato PLAYING
            if self.current_state == GameState.PLAYING:
                self.update()
            
            self.render()
            self.clock.tick(60)
        
        pygame.quit()