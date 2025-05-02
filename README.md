# GL2DWidget: Widget de Renderização 2D com OpenGL e PyQt5

O `GL2DWidget` é um widget altamente personalizável baseado em `QOpenGLWidget` que oferece uma plataforma para renderização 2D de alta performance com OpenGL. Ideal para simulações visuais, como o VSSS, o widget permite desenhar objetos 2D, incluindo imagens, formas geométricas, texto e mais, com controle total sobre o processo de renderização. 

Este componente é perfeito para aplicações que exigem gráficos 2D de alto desempenho e flexibilidade, como jogos, simuladores ou sistemas interativos.

---

## ⚙️ Funcionalidades

- **Renderização 2D Personalizada**: Desenhe imagens, formas geométricas, linhas, círculos, texto, polígonos, setas e muito mais, com total controle sobre a renderização.
- **Desempenho Otimizado**: Suporte para cache de texturas e uso de Framebuffer Objects (FBOs) para renderizar em back buffers.
- **Controle Completo**: Integração com PyQt5, permitindo capturar eventos de teclado, mouse e customizar a interface.
- **Design Modular**: Estrutura modular para fácil personalização e extensão da funcionalidade do widget.

---

## 🎮 Demonstração

### Desenhando no Widget

O widget permite desenhar uma variedade de elementos gráficos em uma superfície 2D. Aqui está um exemplo de como ele pode ser utilizado:

1. **Retângulos**:
   ```python
   widget.draw_rect(x, y, width, height, color)
   ```

2. **Linhas**:
   ```python
   widget.draw_line(x1, y1, x2, y2, color)
   ```

3. **Círculos**:
   ```python
   widget.draw_circle(x, y, radius, color)
   ```

4. **Texto**:
   ```python
   widget.draw_text(x, y, "Texto de exemplo", color)
   ```

5. **Imagens**:
   ```python
   widget.draw_image(x, y, image)
   ```

---

## 📑 Instalação

### Requisitos

- Python 3.x
- PyQt5
- PyOpenGL
- NumPy (se necessário para cálculo de vetores e geometria)

### Como instalar

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/GL2DWidget.git
   cd GL2DWidget
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🛠️ Como Usar

1. **Inicializando o Widget**: O `GL2DWidget` pode ser adicionado facilmente a qualquer aplicação PyQt5. Basta instanciá-lo e adicionar à sua interface.

```python
from PyQt5.QtWidgets import QApplication, QMainWindow
from GL2DWidget import GL2DWidget

app = QApplication([])

# Criando uma janela principal
window = QMainWindow()
widget = GL2DWidget(window, 800, 600)  # Tamanho do widget
window.setCentralWidget(widget)

window.show()
app.exec_()
```

2. **Renderizando Conteúdo**: Após inicializar o widget, use o método `paintGL` para desenhar elementos gráficos. A renderização pode ser personalizada de acordo com as necessidades da sua aplicação.

---

## ⚡ Métodos Principais

- **`initializeGL()`**: Configura o contexto OpenGL inicial. Chamado uma vez ao inicializar o widget.
- **`resizeGL(width, height)`**: Ajusta o viewport e as projeções quando o widget é redimensionado.
- **`paintGL()`**: Método principal de renderização, equivalente ao loop do Pygame.
- **`render_to_back_buffer()`**: Renderiza a cena em um back buffer antes de exibir na tela, proporcionando maior controle sobre a renderização e melhor desempenho.

### Interatividade

- **Eventos de Teclado**: Capture entradas de teclado com o método `keyPressEvent(event)`, permitindo interação direta com o usuário.
- **Eventos de Mouse**: Os cliques podem ser capturados para manipulação de objetos desenhados ou para eventos específicos.

---

## 🛡️ Como Funciona?

### Estrutura de Renderização

O `GL2DWidget` usa uma combinação de OpenGL e PyQt5 para criar uma superfície de renderização 2D de alto desempenho. Ele utiliza:

- **Framebuffer Objects (FBOs)**: Para renderização eficiente, com renderização em back buffer.
- **Cache de Texturas**: Armazena texturas já renderizadas para evitar recriação desnecessária, economizando tempo de processamento.
- **Shaders OpenGL**: Personalização de renderização através de shaders para efeitos visuais avançados.

### Sistema de Camadas

O widget possui um sistema de camadas (layers) para desenhar objetos. Você pode desenhar objetos em diferentes camadas, controlando a ordem de exibição:

```python
# Exemplo de adição de uma chamada de desenho com camada
widget.back_buffer.add_call(BackBuffer2D.DRAW_RECT, x=10, y=10, width=100, height=100, color=(1, 0, 0, 1), layer=1)
```

---

## 📈 Desempenho

O `GL2DWidget` foi projetado para alta performance, com suporte a:

- **VBOs (Vertex Buffer Objects)**: Para renderização eficiente de geometria.
- **VAOs (Vertex Array Objects)**: Para otimização de chamadas de renderização.
- **Desenho Imediato (Immediate Mode)**: Desenha diretamente na tela quando necessário, com desempenho ajustável.

---

## 🛠️ Funcionalidades Avançadas

1. **Desenho com Primitivas**: 
   O widget oferece suporte a vários tipos de primitivas:
   - Retângulos
   - Linhas
   - Círculos
   - Polígonos
   - Setas

2. **Renderização de Imagens**:
   Suporta renderização de imagens em texturas, com controle sobre posição, escala, rotação e transparência.

3. **Texto com Textura**:
   O texto é convertido em texturas OpenGL para maior flexibilidade e desempenho.

---

## 📚 Exemplos de Código

### Exemplo de Desenho Simples

```python
# Criando o widget GL2DWidget
widget = GL2DWidget()

# Desenhando um retângulo vermelho
widget.draw_rect(50, 50, 200, 100, (1, 0, 0, 1))  # x, y, largura, altura, cor
```

### Exemplo de Desenho com Texto

```python
# Desenhando texto no widget
widget.draw_text(100, 100, "Texto Exemplo", (1, 1, 1, 1))  # x, y, texto, cor
```

---

## 🚀 Contribua

Este projeto é de código aberto! Se você deseja contribuir, por favor, siga as etapas abaixo:

1. Faça um fork do repositório.
2. Crie uma branch para a nova funcionalidade (`git checkout -b minha-nova-funcionalidade`).
3. Faça commit das suas alterações (`git commit -am 'Adiciona nova funcionalidade'`).
4. Envie para o repositório remoto (`git push origin minha-nova-funcionalidade`).
5. Abra um Pull Request.

---

## 📜 Licença

O `GL2DWidget` é distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🔗 Links

- [Repositório GitHub](https://github.com/SauloJose/WidgetGL2D)


---

Divirta-se com o `GL2DWidget` e explore as infinitas possibilidades para suas aplicações gráficas 2D!