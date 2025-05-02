from OpenGL.GL import * 
import numpy as np 

class TextureCache:
    def __init__(self, max_size_mb=50):
        self.cache = {}
        self.max_size = max_size_mb * 1024 * 1024
        self.current_size = 0
        self.access_counter = 0

    def get(self, key):
        """Obtém textura do cache com LRU"""
        if key in self.cache:
            entry = self.cache[key]
            if glIsTexture(entry['id']):
                entry['last_used'] = self.access_counter
                self.access_counter += 1
                return entry['id']
            self._remove(key)
        return None

    def add(self, key, tex_id, size):
        """Adiciona textura ao cache com gerenciamento automático de tamanho"""
        if self.current_size + size > self.max_size:
            self._cleanup()
        
        self.cache[key] = {
            'id': tex_id,
            'size': size,
            'last_used': self.access_counter
        }
        self.current_size += size
        self.access_counter += 1

    def _cleanup(self):
        """Remove as texturas menos usadas recentemente"""
        entries = sorted(self.cache.items(), key=lambda x: x[1]['last_used'])
        for key, entry in entries[:len(entries)//2]:
            self._remove(key)

    def _remove(self, key):
        """Remove uma textura específica"""
        if key in self.cache:
            glDeleteTextures([self.cache[key]['id']])
            self.current_size -= self.cache[key]['size']
            del self.cache[key]

