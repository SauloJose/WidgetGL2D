from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from OpenGL.GL import *
from OpenGL.GL import shaders

from backBuffer2D import * 
from texture    import *


class GL2DWidget(QOpenGLWidget):
    '''
    A QOpenGLWidget-based rendering surface that simulates a Pygame-like drawing environment,
    enabling custom OpenGL-based 2D rendering for objects such as images, geometric shapes,
    and simulated graphic elements.

    This component is well-suited for visual simulation systems like VSSS, providing full
    control over rendering with high performance.

    Attributes:
        width (int): The width of the widget.
        height (int): The height of the widget.
        image (Image): An image object used for basic rendering (can be overridden).
        timer (QTimer): Timer responsible for triggering frame updates.

    Methods:
        initializeGL(): Sets up the initial OpenGL context.
        resizeGL(w, h): Adjusts the viewport and projection when the window is resized.
        paintGL(): Main rendering method (acts like the Pygame main loop).
        keyPressEvent(event): Handles keyboard events (example of input interaction).
    '''

    def __init__(self, parent=None, width=None, height=None):
        '''
            Initializes the widget, sets the width and height, loads the initial image,
            and configures the timer for regular updates.

            Args:
                parent (QWidget): Optional parent widget.
                width (int): Optional width of the widget.
                height (int): Optional height of the widget.
        '''
        print("[GL2DWidget]: Initializing widget.")
        super().__init__(parent)

        # Set view Dimensions
        self.view_width = max(1, width) if width is not None else 800
        self.view_height = max(1, height) if height is not None else 600
        self.setMinimumSize(self.view_width, self.view_height)

        # Initialize data structures
        self.back_buffer = BackBuffer2D()
        self.texture_cache = TextureCache(max_size_mb=50)

        # Framebuffer objects
        self.main_fbo = None 
        self.render_fbo = None 

        # Interaction
        self.click_position = None

        # Internal state
        self._is_initialized = False 
        self._shader_program =  None 

    def initializeGL(self):
        print("[GL2DWidget]: Initializing OpenGL context.")
        try:
            # Check if the OpenGL context is valid
            context = self.context()
            if not context or not context.isValid():
                raise RuntimeError("OpenGL context is not available or invalid. Ensure your system supports OpenGL.")

            # Initialize OpenGL functions
            self.gl = QOpenGLFunctions()
            self.gl.initializeOpenGLFunctions()

            # Set basic OpenGL state
            glClearColor(0, 0, 0, 1)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

            # Create framebuffer objects
            self._create_framebuffers()

            # Compile shaders
            self._compile_shaders()

            self._is_initialized = True
            print("[GL2DWidget]: OpenGL context initialized successfully.")
        except Exception as e:
            print(f"[Error][initializeGL]: Failed to initialize OpenGL context: {e}")
            self._is_initialized = False
            self.setEnabled(False)  # Disable the widget if initialization fails

    def _create_framebuffers(self):
        """Create the main and render framebuffer objects"""
        try:
            if not QOpenGLFramebufferObject.hasOpenGLFramebufferObjects():
                raise RuntimeError("FBOs not supported on this system")

            # Delete existing FBOs if they exist
            if self.main_fbo:
                self.main_fbo.release()
                del self.main_fbo

            if self.render_fbo:
                self.render_fbo.release()
                del self.render_fbo

            # Create new FBOs with current size
            size = self.size() * self.devicePixelRatio()
            format = QOpenGLFramebufferObjectFormat()
            format.setAttachment(QOpenGLFramebufferObject.CombinedDepthStencil)
            format.setSamples(4)  # Enable multisampling

            self.main_fbo = QOpenGLFramebufferObject(size.width(), size.height(), format)
            self.render_fbo = QOpenGLFramebufferObject(size.width(), size.height())

            if not self.main_fbo.isValid() or not self.render_fbo.isValid():
                raise RuntimeError("Failed to create framebuffer objects")

            print("[GL2DWidget]: Framebuffer objects created successfully.")
        except Exception as e:
            print(f"[Error][_create_framebuffers]: {e}")

    def _compile_shaders(self):
        """Compile basic shaders for rendering"""
        try:
            vertex_shader = """
            #version 330 core
            layout (location = 0) in vec2 position;
            layout (location = 1) in vec2 texCoord;
            layout (location = 2) in vec4 color;
            
            out vec2 TexCoord;
            out vec4 Color;
            
            uniform mat4 projection;
            
            void main()
            {
                gl_Position = projection * vec4(position, 0.0, 1.0);
                TexCoord = texCoord;
                Color = color;
            }
            """
            
            fragment_shader = """
            #version 330 core
            in vec2 TexCoord;
            in vec4 Color;
            out vec4 FragColor;
            
            uniform sampler2D texture1;
            uniform bool useTexture;
            
            void main()
            {
                if (useTexture) {
                    FragColor = texture(texture1, TexCoord) * Color;
                } else {
                    FragColor = Color;
                }
            }
            """
            
            try:
                self._shader_program = shaders.compileProgram(
                    shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
                    shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER)
                )  # Faltava este parêntese
            except Exception as e:
                print(f"Error compiling shaders: {e}")
                self._shader_program = None
                # Pode adicionar um fallback para shaders simples aqui
            print("[GL2DWidget]: Shaders compiled successfully.")
        except Exception as e:
            print(f"[Error][_compile_shaders]: Failed to compile shaders: {e}")
            self._shader_program = None
            
    def paintGL(self):
        if not self._is_initialized:
            print("[Error][paintGL]: OpenGL context is not initialized. Skipping paintGL.")
            return
            
        try:
            # First render to our FBO
            self.main_fbo.bind()
            
            # Clear the FBO
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            # Process all draw calls
            sorted_calls = sorted(self.back_buffer.get_calls(), key=lambda call: call.layer)
            for call in sorted_calls:
                self._process_draw_call(call)
            
            # Release the FBO
            self.main_fbo.release()
            
            # Now render the FBO to screen
            self._render_fbo_to_screen()
            print("[GL2DWidget]: Frame rendered successfully.")
            
        except Exception as e:
            print(f"[Error][paintGL]: {e}")
            self._check_gl_error("paintGL")


    def resizeGL(self, w, h):
        try:
            print(f"[GL2DWidget]: Resizing to {w}x{h}")
            
            # Update view dimensions
            self.view_width = w
            self.view_height = h
            
            # Recreate framebuffers with new size
            self._create_framebuffers()
            
            # Set viewport and projection
            glViewport(0, 0, w, h)
            
            # Update projection matrix
            if self._shader_program:
                glUseProgram(self._shader_program)
                projection = QMatrix4x4()
                projection.ortho(0, w, h, 0, -1, 1)
                loc = glGetUniformLocation(self._shader_program, "projection")
                glUniformMatrix4fv(loc, 1, GL_FALSE, projection.data())
                glUseProgram(0)
            print("[GL2DWidget]: Resize completed successfully.")
        except Exception as e:
            print(f"[Error][resizeGL]: {e}")

    def _render_fbo_to_screen(self):
        """Render the main FBO to the screen"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Bind the main FBO's texture
        glBindTexture(GL_TEXTURE_2D, self.main_fbo.texture())
        
        # Set up for rendering a full-screen quad
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width(), self.height(), 0, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Render the texture
        glEnable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(0, 0)
        glTexCoord2f(1, 0); glVertex2f(self.width(), 0)
        glTexCoord2f(1, 1); glVertex2f(self.width(), self.height())
        glTexCoord2f(0, 1); glVertex2f(0, self.height())
        glEnd()
        glDisable(GL_TEXTURE_2D)

    ## ====== Lógica de desenhos e sistema de layers ===
    def render_to_back_buffer(self):
        if not self._is_initialized:
            print("[render_to_back_buffer]: Widget not initialized.")
            return

        self.makeCurrent()
        try:
            # Use o FBO principal
            self.main_fbo.bind()
            glViewport(0, 0, self.view_width, self.view_height)

            glClearColor(0.2, 0.2, 0.2, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            sorted_calls = sorted(self.back_buffer.get_calls(), key=lambda call: call.layer)
            for call in sorted_calls:
                try:
                    self._process_draw_call(call)
                except Exception as e:
                    print(f"[Error][render_to_back_buffer]: Error processing draw call: {e}")

            self.main_fbo.release()
            self.update()  # Força a atualização do widget

        except Exception as e:
            print(f"[GL Error][render_to_back_buffer]: Error during render: {e}")
            self._check_gl_error("render_to_back_buffer")
        finally:
            self.doneCurrent()


    def _process_draw_call(self, call):
        """ Processa uma única draw call de forma segura """
        try:
            if call.draw_type == BackBuffer2D.DRAW_IMAGE:
                if call.obj:
                    self._render_image(call.obj, call.x, call.y, call.scale, call.angle, call.alpha)
                else:
                    print("[Aviso][_process_draw_call]: DRAW_IMAGE com objeto nulo.")

            elif call.draw_type == BackBuffer2D.DRAW_PRIMITIVE:
                if call.obj == "rect":
                    self._render_rect(call.x, call.y, call.scale_x, call.scale_y, call.color)
                elif call.obj == "rect_vbo":
                    self._render_rect_vbo(call.x, call.y, call.scale_x, call.scale_y, call.color, fill=call.fill)
                elif call.obj == "line":
                    self._render_line(call.x, call.y, call.end_x, call.end_y, call.color)
                                
                elif call.obj == "circle":
                    self._render_circle(call.x, call.y, call.radius, call.color)
                                
                elif call.obj == "polygon":
                    self._render_polygon(call.points, call.color)
                                
                elif call.obj == "arrow":
                    self._render_arrow(call.x, call.y, call.end_x, call.end_y, call.color)
                else:
                    print(f"[Aviso][_process_draw_call]: Objeto de primitiva desconhecido: {call.obj}")

            elif call.draw_type == BackBuffer2D.DRAW_TEXT:
                if isinstance(call.obj, str):
                    self._render_text(call.x, call.y, call.obj, call.color)
                else:
                    print("[Aviso][_process_draw_call]: DRAW_TEXT com objeto não textual.")
            
            else:
                print(f"[Aviso][_process_draw_call]: Tipo de draw_call desconhecido: {call.draw_type}")
            print(f"[GL2DWidget]: Processed draw call of type '{call.draw_type}' on layer {call.layer}.")
        except Exception as e:
            print(f"[Erro][_process_draw_call]: Erro ao processar draw call: {str(e)}")

    ## ======= FUNÇÕES DE DESENHAR NA TELA ======
    def update_widget(self):
        '''
            Método para forçar a atualização do widget
        '''
        self.update()

    def render_frame(self):
        '''
            Método único para ser chamado de fora. Atualizando o back_buffer e desenhando
            semelhante ao flip.
        '''
        if not self._is_initialized:
            return 
        self.render_to_back_buffer()
        self.update_widget()

    ## ====== FUNÇÕES DE RENDERIZAÇÃO =========
    ## ==== Classes básicas de render para desenhos primitivos
    # Substitua o método _safe_gl_render por:
    def _safe_gl_render(self, render_func, *args):
        """Wrapper seguro para funções de renderização (Core Profile compatible)"""
        if not self._is_initialized or not QOpenGLContext.currentContext():
            return
        
        self.makeCurrent()
        try:
            # Save relevant state
            blend_enabled = glIsEnabled(GL_BLEND)
            blend_src = glGetIntegerv(GL_BLEND_SRC_RGB)
            blend_dst = glGetIntegerv(GL_BLEND_DST_RGB)
            
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            # Usar VAOs e VBOs em vez do modo imediato
            render_func(*args)
            
        except Exception as e:
            print(f"Erro na renderização: {e}")
            self._check_gl_error("_safe_gl_render")
        finally:
            # Restore state
            if not blend_enabled:
                glDisable(GL_BLEND)
            glBlendFunc(blend_src, blend_dst)
            self.doneCurrent()


    def _render_rect(self, x, y, w, h, color, thickness=1, fill=False):
        """Desenha um retângulo, com a opção de preenchimento ou apenas a borda."""
        def _draw():
            glPushMatrix()
            glColor4f(*color)
            if fill:
                glBegin(GL_QUADS)
            else:
                glLineWidth(thickness)
                glBegin(GL_LINE_LOOP)
            
            glVertex2f(x, y)
            glVertex2f(x + w, y)
            glVertex2f(x + w, y + h)
            glVertex2f(x, y + h)
            glEnd()
            glPopMatrix()
        
        self._safe_gl_render(_draw)

    def _render_line(self, x1, y1, x2, y2, color, thickness=1):
        '''
            Método padrão para renderizar uma linha
        '''
        def _draw():
            glLineWidth(thickness)
            glColor4f(*color)
            glBegin(GL_LINES)
            glVertex2f(x1, y1)
            glVertex2f(x2, y2)
            glEnd()
        
        self._safe_gl_render(_draw)


    def _render_circle(self, x, y, radius, color, segments=32, thickness=1):
        '''
            Método padrão para renderizar círculos
        '''
        def _draw():
            # Pré-computa os vértices uma vez
            vertices = []
            for i in range(segments + 1):
                angle = 2.0 * np.pi * i / segments
                vertices.append((radius * np.cos(angle), radius * np.sin(angle)))
            
            glPushMatrix()
            glTranslatef(x, y, 0)
            glColor4f(*color)
            glLineWidth(thickness)
            glBegin(GL_LINE_LOOP)
            for dx, dy in vertices:
                glVertex2f(dx, dy)
            glEnd()
            glPopMatrix()
        
        self._safe_gl_render(_draw)


    def _render_polygon(self, points, color, thickness=1):
        if not points or len(points) < 3:
            return
        
        def _draw():
            glColor4f(*color)
            glLineWidth(thickness)
            glBegin(GL_LINE_LOOP)
            for x, y in points:
                glVertex2f(x, y)
            glEnd()
        
        self._safe_gl_render(_draw)




    def _render_text(self, x, y, text, color):
        # Verificação inicial consolidada
        if not text or not color or len(color)<4:
            return

        def _draw():
            # Geração de chave de cache mais robusta
            cache_key = f"text_{hash(text)}_{hash(color.tobytes())}"
            
            texture = self.texture_cache.get(cache_key)
            if not texture:
                # Criação otimizada da textura
                texture = self._create_text_texture(text, color)
                if texture:
                    self.texture_cache.add(cache_key, texture['id'], texture['size'])

            if texture:
                self._draw_textured_quad(x, y, texture['width'], texture['height'], texture['id'])

        self._safe_gl_render(_draw)

    # Criando texturas de texto
    def _create_text_texture(self, text, color):
        """Cria textura para texto de forma otimizada"""
        font = QFont("Arial", 14, QFont.Bold)
        metrics = QFontMetrics(font)
        margin = 2
        size = metrics.size(0, text)
        
        image = QImage(size.width() + margin*2, size.height() + margin*2, 
                    QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setPen(QColor.fromRgbF(*color))
        painter.setFont(font)
        painter.drawText(margin, margin + metrics.ascent(), text)
        painter.end()

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width(), image.height(),
                    0, GL_BGRA, GL_UNSIGNED_BYTE, image.bits())
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        
        return {
            'id': texture_id,
            'width': image.width(),
            'height': image.height(),
            'size': image.width() * image.height() * 4
        }

    def _render_arrow(self, x1, y1, x2, y2, color, width=1):
        """Renderiza uma seta usando NumPy para cálculos vetoriais"""
        def _draw():
            # Converte pontos para arrays NumPy
            start = np.array([x1, y1])
            end = np.array([x2, y2])
            
            # Vetor de direção e ângulo
            direction = end - start
            angle = np.arctan2(direction[1], direction[0])
            
            # Parâmetros da cabeça da seta
            head_length = 10 * width
            head_angle = np.pi / 6  # 30 graus
            
            # Renderiza a linha principal
            self._render_line(x1, y1, x2, y2, color, width)
            
            # Calcula os vértices da cabeça usando NumPy
            angles = np.array([angle - head_angle, angle + head_angle])
            head_vectors = head_length * np.column_stack([
                np.cos(angles),
                np.sin(angles)
            ])
            
            # Pontos da cabeça relativos à ponta
            left_point = end - head_vectors[0]
            right_point = end - head_vectors[1]
            
            # Renderização otimizada
            glBegin(GL_TRIANGLES)
            glVertex2f(*end)
            glVertex2f(*left_point)
            glVertex2f(*right_point)
            glEnd()
        
        self._safe_gl_render(_draw)

    def _render_direct(self):
        if not self._is_initialized:
            return

        self.makeCurrent()
        try:
            # Configuração básica do viewport e matrizes
            glViewport(0, 0, self.width(), self.height())
            
            # Só configura matrizes se não for Core Profile
            if not self.gl33:
                glMatrixMode(GL_PROJECTION)
                glLoadIdentity()
                glOrtho(0, self.width(), self.height(), 0, -1, 1)
                
                glMatrixMode(GL_MODELVIEW)
                glLoadIdentity()
            
            # Limpar buffers
            glClearColor(0.2, 0.2, 0.2, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            # Habilitar recursos necessários
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            # Processar draw calls
            sorted_calls = sorted(self.back_buffer.get_calls(), key=lambda x: x.layer)
            for call in sorted_calls:
                try:
                    self._process_draw_call(call)
                except Exception as e:
                    print(f"[_render_direct] Erro ao processar draw call: {e}")
                    continue
            
            glFlush()
            
        except Exception as e:
            print(f"[_render_direct] Erro crítico: {e}")
            self._check_gl_error("_render_direct")
        finally:
            self.doneCurrent()
            
    #Renderizando imagem
    def _render_image(self, image_obj: Image, x: float, y: float, 
                    scale: float = 1.0, angle: float = 0.0, alpha: float = 1.0) -> None:
        """
        Renderiza uma imagem com transformações, usando cache de texturas otimizado
        
        Args:
            image_obj: Objeto Image contendo os dados da imagem
            x, y: Posição na tela
            scale: Escala uniforme (1.0 = tamanho original)
            angle: Ângulo de rotação em graus
            alpha: Transparência (0.0 a 1.0)
        """
        # Validação inicial rápida
        if not self._is_initialized or not image_obj or not image_obj.is_valid():
            return

        def _draw():
            # Geração da chave de cache otimizada
            cache_key = self._generate_image_cache_key(image_obj)
            
            # Tentativa de obtenção do cache
            texture_id = self.texture_cache.get(cache_key)
            
            # Cache miss - criação da textura
            if texture_id is None:
                if not (prepared := image_obj._prepare_for_gl()):
                    return  # Falha na preparação
                
                # Cria nova textura e adiciona ao cache
                texture_data = self._create_gl_texture(prepared)
                if not texture_data:
                    return  # Falha na criação
                
                texture_id = texture_data['id']
                self.texture_cache.add(cache_key, texture_id, texture_data['size'])
            
            # Renderização otimizada
            w = image_obj.width * scale
            h = image_obj.height * scale
            
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glColor4f(1.0, 1.0, 1.0, alpha)
            
            glPushMatrix()
            glTranslatef(x, y, 0)
            glRotatef(angle, 0, 0, 1)
            
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(-w/2, -h/2)
            glTexCoord2f(1, 0); glVertex2f(w/2, -h/2)
            glTexCoord2f(1, 1); glVertex2f(w/2, h/2)
            glTexCoord2f(0, 1); glVertex2f(-w/2, h/2)
            glEnd()
            
            glPopMatrix()
            glDisable(GL_TEXTURE_2D)

        # Execução segura no contexto OpenGL
        self._safe_gl_render(_draw)
            
    def _draw_textured_quad(self, x, y, w, h, tex_id, angle=0.0, alpha=1.0):
        """Método compartilhado para renderização de quads texturizados"""
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glColor4f(1.0, 1.0, 1.0, alpha)
        
        glPushMatrix()
        glTranslatef(x, y, 0)
        glRotatef(angle, 0, 0, 1)
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(-w/2, -h/2)
        glTexCoord2f(1, 0); glVertex2f(w/2, -h/2)
        glTexCoord2f(1, 1); glVertex2f(w/2, h/2)
        glTexCoord2f(0, 1); glVertex2f(-w/2, h/2)
        glEnd()
        
        glPopMatrix()

    def _create_gl_texture(self, image_data):
        """
        Cria uma textura OpenGL a partir de dados de imagem preparados
        Args:
            image_data: Dict com:
                - 'data': bytes da imagem (formato RGBA)
                - 'size': (width, height)
        Returns:
            Dict com textura criada ou None em caso de erro
        """
        if not image_data or 'data' not in image_data or 'size' not in image_data:
            return None

        try:
            width, height = image_data['size']
            texture_id = glGenTextures(1)
            
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height,
                        0, GL_RGBA, GL_UNSIGNED_BYTE, image_data['data'])
            
            # Configurações padrão para filtragem
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
            
            return {
                'id': texture_id,
                'width': width,
                'height': height,
                'size': width * height * 4  # 4 bytes por pixel (RGBA)
            }
            
        except Exception as e:
            print(f"Erro ao criar textura OpenGL: {e}")
            if 'texture_id' in locals() and glIsTexture(texture_id):
                glDeleteTextures([texture_id])
            return None

    def _generate_image_cache_key(self, image_obj: Image) ->str:
        """
        Gera uma chave de cache única para uma imagem e suas transformações
        Args:
            image_obj: Instância da classe Image
        Returns:
            String hash única para a combinação imagem+transformações
        """
        if not image_obj or not image_obj.is_valid():
            return "invalid_0"

        # Usamos o caminho do arquivo ou dados do fallback como base
        content_id = image_obj._filepath or f"fallback_{id(image_obj._source)}"
        
        # Hash das transformações atuais (com precisão controlada)
        transform_hash = hash((
            round(image_obj._current_angle, 2),    # Ângulo com 2 casas decimais
            round(image_obj._current_scale, 4),    # Escala com 4 casas decimais
            image_obj._flip_x,
            image_obj._flip_y,
            image_obj.width,                       # Dimensões finais
            image_obj.height
        ))
        
        return f"img_{hash(content_id)}_{transform_hash}"
    

    ## ==== Métodos de interatividade =====
    def mousePressEvent(self, event):
        '''
        Captura o evento de clique do mouse, armazena a posição relativa ao widget.
        '''
        # Posição do clique no widget
        pos = event.pos()
        self.click_position = (pos.x(), pos.y())
        print(f"Click registrado em: {self.click_position}")

        # Opcional: você pode passar o evento adiante se precisar de outras funcionalidades.
        # super().mousePressEvent(event)

    def get_click_position(self):
        '''
        Retorna a posição do clique armazenada.
        Se não houver clique, retorna None.
        '''
        return self.click_position
    
    ## ==== Métodos de limpezad ==========
    def cleanup(self):
        """Clean up all OpenGL resources"""
        if not self.isValid():
            print("[GL2DWidget]: Widget is not valid for cleanup.")
            return

        self.makeCurrent()
        try:
            # Clean up FBOs
            if hasattr(self, 'main_fbo') and self.main_fbo:
                self.main_fbo.release()
                del self.main_fbo
                
            if hasattr(self, 'render_fbo') and self.render_fbo:
                self.render_fbo.release()
                del self.render_fbo
                
            # Clean up shaders
            if hasattr(self, '_shader_program') and self._shader_program:
                glDeleteProgram(self._shader_program)
                self._shader_program = None
            
            # Limpe todas as texturas do cache
            for entry in list(self.texture_cache.cache.values()):
                if glIsTexture(entry['id']):
                    glDeleteTextures([entry['id']])

            # Clean up texture cache
            if hasattr(self, 'texture_cache'):
                self.texture_cache.cache.clear()
                self.texture_cache.current_size = 0
                
            # Clear back buffer
            if hasattr(self, 'back_buffer'):
                self.back_buffer.clear()
                
            glFlush()
            glFinish()
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            self.doneCurrent()
            self._is_initialized = False
        print("[GL2DWidget]: Cleanup completed successfully.")

    def _check_gl_error(self, context=""):
        """Utility function to check for OpenGL errors"""
        error = glGetError()
        if error != GL_NO_ERROR:
            print(f"OpenGL error in {context}: {error}")
            return True
        return False

    def closeEvent(self,event):
        '''
        Quando fecahr a janela
        '''
        self.cleanup()
        super().closeEvent(event)