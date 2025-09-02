import pygame
import time
from common.shoot import Shoot
#from common.asset_manager import AssetManager

PLAYER_SHOT_COOLDOWN = 0.5
PLAYER_BULLET_SPEED = 10

class Player:
    def __init__(self, x, y, width, height, screen_width, asset_manager):
        """
        Inizializza il giocatore con:
        - x, y: posizione iniziale
        - width, height: dimensioni del rettangolo di collisione
        - screen_width: larghezza dello schermo
        - asset_manager: riferimento all'AssetManager per caricare le immagini
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.screen_width = screen_width
        self.asset_manager = asset_manager
        self.original_x = x
        self.speed = 5
        self.moving = {"left": False, "right": False}
        self.shoot_cooldown = 0
        self.last_shot_time = 0
        self.cell_size = 0
        self.sidebar_width = 0
        self.screen_height = 0
        
        # Inizializzazione immagine del giocatore
        self.image = self._load_player_image(width, height)
        self.color = (0, 128, 255)  # Colore di fallback

    def _load_player_image(self, width, height):
        """Carica e ridimensiona l'immagine del giocatore mantenendo le proporzioni"""
        try:
            original_img = self.asset_manager.load_image("images/player.png")
            
            # Calcola il rapporto di scala mantenendo le proporzioni
            scale = min(width/original_img.get_width(), height/original_img.get_height())
            new_width = int(original_img.get_width() * scale)
            new_height = int(original_img.get_height() * scale)
            
            img = pygame.transform.scale(original_img, (new_width, new_height))
            
            # Calcola offset per centrare l'immagine
            self.image_offset_x = (width - new_width) // 2
            self.image_offset_y = (height - new_height) // 2
            
            return img
        except Exception as e:
            print(f"Errore nel caricamento dell'immagine del player: {e}")
            # Crea un fallback grafico
            surf = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.polygon(surf, self.color, [
                (width//2, 0), 
                (0, height),
                (width, height)
            ])
            return surf

    def set_moving(self, direction, active):
        """Imposta lo stato di movimento (left/right)"""
        self.moving[direction] = active

    def update(self):
        """Aggiorna la posizione del giocatore (per controllo continuo)"""
        if self.moving["left"]:
            new_x = self.rect.x - self.speed
            self.rect.x = max(0, new_x)
        if self.moving["right"]:
            new_x = self.rect.x + self.speed
            self.rect.x = min(self.screen_width - self.rect.width, new_x)
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move_left(self):
        """Muove il giocatore a sinistra di una cella (per input discreto)"""
        self.rect.x = max(0, self.rect.x - self.cell_size)
        
    def move_right(self):
        """Muove il giocatore a destra di una cella (per input discreto)"""
        max_x = (self.screen_width - self.sidebar_width) - self.rect.width
        self.rect.x = min(max_x, self.rect.x + self.cell_size)

    def shoot(self):
        """Crea un nuovo proiettile se il cooldown lo permette"""
        current_time = time.time()
        if current_time - self.last_shot_time >= PLAYER_SHOT_COOLDOWN:
            self.last_shot_time = current_time
            bullet = Shoot(self.rect.centerx - 2, self.rect.top)
            bullet.speed = PLAYER_BULLET_SPEED
            return bullet
        return None

    def draw(self, surface):
        """Disegna il giocatore sullo schermo"""
        if self.image:
            # Disegna l'immagine centrata nel rettangolo di collisione
            surface.blit(self.image, 
                       (self.rect.x + self.image_offset_x, 
                        self.rect.y + self.image_offset_y))
        else:
            # Fallback grafico
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, (0, 0, 0), self.rect, 2)
        
        # DEBUG: mostra il rettangolo di collisione
        if hasattr(self, 'debug_mode') and self.debug_mode:
            pygame.draw.rect(surface, (255, 0, 0), self.rect, 1)

    def reset(self):
        self.rect.x = self.original_x
        self.rect.y = self.screen_height - 60
        self.moving = {"left": False, "right": False}
        self.shoot_cooldown = 0
    