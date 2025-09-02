import pygame
from pathlib import Path

class AssetManager:
    def __init__(self, base_path="assets"):
        """
        Gestisce il caricamento di tutti gli asset del gioco
        - base_path: percorso base degli asset (default 'assets')
        """
        self.base_path = Path(__file__).parent.parent / base_path
        self._images = {}
        self._fonts = {}
        self._sounds = {}  # Dizionario per i suoni brevi
        self._music = None  # Percorso della musica corrente
        
        # Inizializza il mixer audio
        pygame.mixer.init()
        
    def load_image(self, relative_path, size=None, keep_aspect_ratio=False):
        """Carica un'immagine con opzioni avanzate di ridimensionamento"""
        try:
            full_path = self.base_path / relative_path
            image = pygame.image.load(str(full_path)).convert_alpha()
            
            if size:
                if keep_aspect_ratio:
                    # Calcola il rapporto di scala mantenendo le proporzioni
                    scale = min(size[0]/image.get_width(), size[1]/image.get_height())
                    new_size = (int(image.get_width() * scale), 
                            int(image.get_height() * scale))
                    return pygame.transform.scale(image, new_size)
                else:
                    return pygame.transform.scale(image, size)
            return image
        except Exception as e:
            print(f"Errore nel caricamento dell'immagine {relative_path}: {e}")
            # Crea un fallback visibile
            surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.rect(surf, (255, 0, 0), (0, 0, 50, 50), 2)
            return surf
    
    def get_image(self, relative_path):
        """Recupera un'immagine già caricata"""
        return self._images.get(relative_path)
    
    def load_background(self, relative_path, screen_size):
        """Carica uno sfondo già scalato alla dimensione dello schermo"""
        bg = self.load_image(relative_path)
        return pygame.transform.scale(bg, screen_size)
    
    # Metodi per la gestione dell'audio
    def load_sound(self, relative_path, volume=0.5):
        """Carica un effetto sonoro"""
        try:
            full_path = self.base_path / relative_path
            sound = pygame.mixer.Sound(str(full_path))
            sound.set_volume(volume)
            self._sounds[relative_path] = sound
            return sound
        except Exception as e:
            print(f"Errore nel caricamento del suono {relative_path}: {e}")
            return None
    
    def play_sound(self, relative_path):
        """Riproduce un effetto sonoro"""
        if relative_path in self._sounds:
            self._sounds[relative_path].play()
    
    def load_music(self, relative_path, volume=0.5):
        """Carica una traccia musicale"""
        try:
            full_path = self.base_path / relative_path
            pygame.mixer.music.load(str(full_path))
            pygame.mixer.music.set_volume(volume)
            self._music = relative_path
            return True
        except Exception as e:
            print(f"Errore nel caricamento della musica {relative_path}: {e}")
            return False
    
    def play_music(self, loops=-1):
        """Riproduce la musica (loops=-1 per ripetere all'infinito)"""
        if self._music:
            pygame.mixer.music.play(loops)
    
    def stop_music(self):
        """Ferma la riproduzione musicale"""
        pygame.mixer.music.stop()
    
    def set_music_volume(self, volume):
        """Imposta il volume della musica (0.0 - 1.0)"""
        pygame.mixer.music.set_volume(volume)
    
    def set_sound_volume(self, relative_path, volume):
        """Imposta il volume di un effetto sonoro specifico"""
        if relative_path in self._sounds:
            self._sounds[relative_path].set_volume(volume)