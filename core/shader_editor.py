from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGraphicsView, 
                             QGraphicsScene, QGraphicsItem, QMenu, QAction, QToolBar,
                             QComboBox, QLabel, QSplitter, QTextEdit, QDockWidget,
                             QListWidget, QListWidgetItem, QPushButton, QColorDialog,
                             QDoubleSpinBox, QGroupBox, QFormLayout, QLineEdit, QCheckBox)
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal, QSize, QPoint
from PyQt5.QtGui import (QPainter, QColor, QPen, QBrush, QLinearGradient, 
                         QFont, QKeyEvent, QMouseEvent, QTextCursor, QSyntaxHighlighter,
                         QTextCharFormat, QTextFormat)
import json
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import re
import uuid

class ConnectionGraphicsItem(QGraphicsItem):
    """Графическое представление соединения между узлами"""
    def __init__(self, start_pos: QPointF, end_pos: QPointF, parent=None):
        super().__init__(parent)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = QColor(200, 200, 200)
        self.thickness = 2
        self.setZValue(-1)  # Под всеми узлами

    def boundingRect(self) -> QRectF:
        return QRectF(self.start_pos, self.end_pos).normalized().adjusted(-5, -5, 5, 5)

    def paint(self, painter: QPainter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self.color, self.thickness)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        # Рисуем кривую Безье для соединения
        path = self.create_bezier_path()
        painter.drawPath(path)

    def create_bezier_path(self):
        from PyQt5.QtGui import QPainterPath
        path = QPainterPath()
        path.moveTo(self.start_pos)
        
        # Контрольные точки для кривой Безье
        ctrl_offset = abs(self.end_pos.x() - self.start_pos.x()) * 0.5
        ctrl1 = QPointF(self.start_pos.x() + ctrl_offset, self.start_pos.y())
        ctrl2 = QPointF(self.end_pos.x() - ctrl_offset, self.end_pos.y())
        
        path.cubicTo(ctrl1, ctrl2, self.end_pos)
        return path

class GLSLHighlighter(QSyntaxHighlighter):
    """Подсветка синтаксиса GLSL"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlighting_rules = []
        
        # Ключевые слова
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(86, 156, 214))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "void", "float", "int", "bool", "vec2", "vec3", "vec4", "mat2", "mat3", "mat4",
            "uniform", "attribute", "varying", "in", "out", "inout", "const", "if", "else",
            "for", "while", "do", "return", "break", "continue", "discard", "struct"
        ]
        for word in keywords:
            pattern = r"\b" + word + r"\b"
            self.highlighting_rules.append((re.compile(pattern), keyword_format))
        
        # Типы
        type_format = QTextCharFormat()
        type_format.setForeground(QColor(78, 201, 176))
        types = [
            "sampler2D", "samplerCube", "bool", "int", "float", "vec2", "vec3", "vec4",
            "mat2", "mat3", "mat4"
        ]
        for word in types:
            pattern = r"\b" + word + r"\b"
            self.highlighting_rules.append((re.compile(pattern), type_format))
        
        # Функции
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(220, 220, 170))
        functions = [
            "sin", "cos", "tan", "asin", "acos", "atan", "pow", "exp", "log", "sqrt",
            "abs", "sign", "floor", "ceil", "fract", "mod", "min", "max", "clamp",
            "mix", "step", "smoothstep", "length", "distance", "dot", "cross", "normalize",
            "reflect", "refract", "texture2D", "textureCube"
        ]
        for word in functions:
            pattern = r"\b" + word + r"\b"
            self.highlighting_rules.append((re.compile(pattern), function_format))
        
        # Комментарии
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(87, 166, 74))
        self.highlighting_rules.append((re.compile(r"//[^\n]*"), comment_format))
        self.highlighting_rules.append((re.compile(r"/\*.*?\*/", re.DOTALL), comment_format))
        
        # Числа
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(181, 206, 168))
        self.highlighting_rules.append((re.compile(r"\b\d+\.?\d*\b"), number_format))
        
        # Препроцессор
        preprocessor_format = QTextCharFormat()
        preprocessor_format.setForeground(QColor(197, 134, 192))
        self.highlighting_rules.append((re.compile(r"#.*"), preprocessor_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)

class NodeLibrary:
    """Библиотека предустановленных узлов"""
    def __init__(self):
        self.nodes = self.create_default_nodes()
    
    def create_default_nodes(self) -> Dict[str, Dict]:
        return {
            "texture_2d": {
                "type": ShaderNodeType.TEXTURE,
                "title": "Texture 2D",
                "inputs": [],
                "outputs": [
                    {"name": "color", "type": SocketType.COLOR, "default": None}
                ],
                "parameters": {
                    "texture": {"type": "sampler2D", "default": None}
                }
            },
            "color": {
                "type": ShaderNodeType.COLOR,
                "title": "Color",
                "inputs": [],
                "outputs": [
                    {"name": "color", "type": SocketType.COLOR, "default": [1.0, 1.0, 1.0]}
                ],
                "parameters": {
                    "value": {"type": "color", "default": [1.0, 1.0, 1.0]}
                }
            },
            "add": {
                "type": ShaderNodeType.MATH,
                "title": "Add",
                "inputs": [
                    {"name": "a", "type": SocketType.FLOAT, "default": 0.0},
                    {"name": "b", "type": SocketType.FLOAT, "default": 0.0}
                ],
                "outputs": [
                    {"name": "result", "type": SocketType.FLOAT, "default": 0.0}
                ],
                "parameters": {}
            },
            "multiply": {
                "type": ShaderNodeType.MATH,
                "title": "Multiply",
                "inputs": [
                    {"name": "a", "type": SocketType.FLOAT, "default": 1.0},
                    {"name": "b", "type": SocketType.FLOAT, "default": 1.0}
                ],
                "outputs": [
                    {"name": "result", "type": SocketType.FLOAT, "default": 1.0}
                ],
                "parameters": {}
            },
            "time": {
                "type": ShaderNodeType.INPUT,
                "title": "Time",
                "inputs": [],
                "outputs": [
                    {"name": "time", "type": SocketType.FLOAT, "default": 0.0}
                ],
                "parameters": {}
            },
            "fragment_output": {
                "type": ShaderNodeType.OUTPUT,
                "title": "Fragment Output",
                "inputs": [
                    {"name": "color", "type": SocketType.COLOR, "default": [0.0, 0.0, 0.0]}
                ],
                "outputs": [],
                "parameters": {}
            }
        }
    
    def create_node_from_template(self, template_id: str, position: QPointF) -> ShaderNode:
        template = self.nodes.get(template_id)
        if not template:
            return None
            
        node_id = f"{template_id}_{uuid.uuid4().hex[:8]}"
        
        inputs = []
        for input_def in template["inputs"]:
            inputs.append(Socket(
                name=input_def["name"],
                socket_type=input_def["type"],
                is_input=True,
                default_value=input_def["default"]
            ))
            
        outputs = []
        for output_def in template["outputs"]:
            outputs.append(Socket(
                name=output_def["name"],
                socket_type=output_def["type"],
                is_input=False,
                default_value=output_def["default"]
            ))
            
        parameters = {}
        for param_name, param_def in template["parameters"].items():
            parameters[param_name] = param_def["default"]
            
        return ShaderNode(
            node_id=node_id,
            node_type=template["type"],
            position=position,
            title=template["title"],
            inputs=inputs,
            outputs=outputs,
            parameters=parameters
        )

class PropertyEditor(QWidget):
    """Редактор свойств выбранного узла"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_node = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel("No node selected")
        layout.addWidget(self.title_label)
        
        self.properties_group = QGroupBox("Properties")
        self.properties_layout = QFormLayout(self.properties_group)
        layout.addWidget(self.properties_group)
        
        layout.addStretch()
        
    def set_node(self, node: ShaderNode):
        self.current_node = node
        self.update_display()
        
    def update_display(self):
        # Очищаем предыдущие свойства
        while self.properties_layout.count():
            child = self.properties_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        if not self.current_node:
            self.title_label.setText("No node selected")
            return
            
        self.title_label.setText(f"Node: {self.current_node.title}")
        
        # Добавляем редакторы для параметров
        for param_name, param_value in self.current_node.parameters.items():
            label = QLabel(param_name.capitalize())
            
            if isinstance(param_value, list) and len(param_value) == 3:  # Цвет
                color_btn = QPushButton()
                color_btn.setFixedSize(60, 25)
                color_btn.setStyleSheet(f"background-color: rgb({param_value[0]*255}, {param_value[1]*255}, {param_value[2]*255})")
                color_btn.clicked.connect(lambda checked, p=param_name: self.change_color(p))
                self.properties_layout.addRow(label, color_btn)
                
            elif isinstance(param_value, (int, float)):
                spinbox = QDoubleSpinBox()
                spinbox.setRange(-1000, 1000)
                spinbox.setValue(float(param_value))
                spinbox.valueChanged.connect(lambda value, p=param_name: self.update_parameter(p, value))
                self.properties_layout.addRow(label, spinbox)
                
            elif isinstance(param_value, str):
                line_edit = QLineEdit(param_value)
                line_edit.textChanged.connect(lambda text, p=param_name: self.update_parameter(p, text))
                self.properties_layout.addRow(label, line_edit)
                
            elif isinstance(param_value, bool):
                checkbox = QCheckBox()
                checkbox.setChecked(param_value)
                checkbox.stateChanged.connect(lambda state, p=param_name: self.update_parameter(p, state == Qt.Checked))
                self.properties_layout.addRow(label, checkbox)
    
    def change_color(self, param_name: str):
        if not self.current_node:
            return
            
        current_color = self.current_node.parameters[param_name]
        qt_color = QColor(int(current_color[0]*255), int(current_color[1]*255), int(current_color[2]*255))
        
        color = QColorDialog.getColor(qt_color, self, "Select Color")
        if color.isValid():
            new_color = [color.redF(), color.greenF(), color.blueF()]
            self.current_node.parameters[param_name] = new_color
            self.update_display()
    
    def update_parameter(self, param_name: str, value):
        if self.current_node and param_name in self.current_node.parameters:
            self.current_node.parameters[param_name] = value

class ShaderEditorView(QGraphicsView):
    """Виджет для редактирования шейдерного графа"""
    node_moved = pyqtSignal(str, QPointF)
    connection_created = pyqtSignal(str, str, str, str)
    node_selected = pyqtSignal(ShaderNode)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        
        self.graph = ShaderGraph()
        self.dragging_connection = None
        self.selected_node = None
        self.connection_start = None
        self.connection_start_socket = None
        self.connection_start_is_input = False
        
        self.setBackgroundBrush(QBrush(QColor(40, 44, 52)))
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setSceneRect(-1000, -1000, 2000, 2000)
        
        # Контекстное меню
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def set_graph(self, graph: ShaderGraph):
        self.graph = graph
        self.update_display()
        
    def update_display(self):
        self.scene.clear()
        
        # Сначала рисуем соединения (чтобы они были под узлами)
        for from_node, from_socket, to_node, to_socket in self.graph.connections:
            self.draw_connection(from_node, from_socket, to_node, to_socket)
            
        # Затем рисуем узлы
        for node in self.graph.nodes.values():
            item = NodeGraphicsItem(node, self.graph)
            if node == self.selected_node:
                item.selected = True
            self.scene.addItem(item)
    
    def draw_connection(self, from_node: str, from_socket: str, to_node: str, to_socket: str):
        from_item = self.find_node_item(from_node)
        to_item = self.find_node_item(to_node)
        
        if from_item and to_item:
            from_pos = self.get_socket_position(from_item, from_socket, False)
            to_pos = self.get_socket_position(to_item, to_socket, True)
            
            connection_item = ConnectionGraphicsItem(from_pos, to_pos)
            self.scene.addItem(connection_item)
    
    def find_node_item(self, node_id: str) -> Optional[NodeGraphicsItem]:
        for item in self.scene.items():
            if isinstance(item, NodeGraphicsItem) and item.node.node_id == node_id:
                return item
        return None
    
    def get_socket_position(self, node_item: NodeGraphicsItem, socket_name: str, is_input: bool) -> QPointF:
        node = node_item.node
        sockets = node.inputs if is_input else node.outputs
        
        for i, socket in enumerate(sockets):
            if socket.name == socket_name:
                y = node_item.header_height + 10 + i * node_item.socket_spacing
                x = 0 if is_input else node_item.width
                return node_item.mapToScene(x, y)
                
        return node_item.mapToScene(node_item.width / 2, node_item.height / 2)
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # Проверяем, кликнули ли мы по сокету
            item = self.itemAt(event.pos())
            if isinstance(item, NodeGraphicsItem):
                # Преобразуем позицию в координаты сцены
                scene_pos = self.mapToScene(event.pos())
                # Преобразуем в локальные координаты узла
                local_pos = item.mapFromScene(scene_pos)
                
                # Проверяем входные сокеты
                for i, socket in enumerate(item.node.inputs):
                    y = item.header_height + 10 + i * item.socket_spacing
                    socket_rect = QRectF(0, y - item.socket_radius, 
                                       item.socket_radius * 2, item.socket_radius * 2)
                    if socket_rect.contains(local_pos):
                        self.start_connection(item.node, socket.name, True)
                        return
                
                # Проверяем выходные сокеты
                for i, socket in enumerate(item.node.outputs):
                    y = item.header_height + 10 + i * item.socket_spacing
                    socket_rect = QRectF(item.width - item.socket_radius * 2, y - item.socket_radius, 
                                       item.socket_radius * 2, item.socket_radius * 2)
                    if socket_rect.contains(local_pos):
                        self.start_connection(item.node, socket.name, False)
                        return
                
                # Выбираем узел
                self.select_node(item.node)
                
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging_connection:
            # Обновляем временное соединение
            self.update()
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.dragging_connection:
            # Завершаем создание соединения
            item = self.itemAt(event.pos())
            if isinstance(item, NodeGraphicsItem) and item.node != self.connection_start:
                scene_pos = self.mapToScene(event.pos())
                local_pos = item.mapFromScene(scene_pos)
                
                # Ищем сокет для соединения
                sockets = item.node.inputs if not self.connection_start_is_input else item.node.outputs
                for i, socket in enumerate(sockets):
                    y = item.header_height + 10 + i * item.socket_spacing
                    x = 0 if not self.connection_start_is_input else item.width
                    socket_rect = QRectF(x - item.socket_radius, y - item.socket_radius, 
                                       item.socket_radius * 2, item.socket_radius * 2)
                    if socket_rect.contains(local_pos):
                        self.finish_connection(item.node, socket.name)
                        return
            
            # Отменяем соединение
            self.cancel_connection()
            
        super().mouseReleaseEvent(event)
    
    def start_connection(self, node: ShaderNode, socket_name: str, is_input: bool):
        self.dragging_connection = True
        self.connection_start = node
        self.connection_start_socket = socket_name
        self.connection_start_is_input = is_input
        self.setCursor(Qt.CrossCursor)
    
    def finish_connection(self, end_node: ShaderNode, end_socket: str):
        if self.connection_start_is_input:
            # Соединяем выход -> вход
            self.graph.connect(end_node.node_id, end_socket, 
                             self.connection_start.node_id, self.connection_start_socket)
        else:
            # Соединяем выход -> вход
            self.graph.connect(self.connection_start.node_id, self.connection_start_socket,
                             end_node.node_id, end_socket)
        
        self.connection_created.emit(
            self.connection_start.node_id, self.connection_start_socket,
            end_node.node_id, end_socket
        )
        self.cancel_connection()
        self.update_display()
    
    def cancel_connection(self):
        self.dragging_connection = False
        self.connection_start = None
        self.connection_start_socket = None
        self.connection_start_is_input = False
        self.unsetCursor()
    
    def select_node(self, node: ShaderNode):
        self.selected_node = node
        self.node_selected.emit(node)
        self.update_display()
    
    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        add_node_menu = menu.addMenu("Add Node")
        
        # Добавляем категории узлов
        categories = {
            "Input": ["Texture", "Color", "Time", "Mouse Position"],
            "Math": ["Add", "Subtract", "Multiply", "Divide", "Sine", "Cosine"],
            "Vector": ["Combine", "Separate", "Dot Product", "Cross Product"],
            "Output": ["Fragment Output", "Vertex Output"]
        }
        
        for category, nodes in categories.items():
            cat_menu = add_node_menu.addMenu(category)
            for node_name in nodes:
                action = cat_menu.addAction(node_name)
                action.triggered.connect(lambda checked, n=node_name: self.add_node_from_context(n, self.mapToScene(pos)))
        
        menu.exec_(self.mapToGlobal(pos))
    
    def add_node_from_context(self, node_name: str, position: QPointF):
        node_lib = NodeLibrary()
        template_id = node_name.lower().replace(" ", "_")
        new_node = node_lib.create_node_from_template(template_id, position)
        
        if new_node:
            self.graph.add_node(new_node)
            self.update_display()
            self.select_node(new_node)

# Дополним класс ShaderEditor
class ShaderEditor(QWidget):
    """Главный редактор шейдеров"""
    def __init__(self):
        super().__init__()
        self.current_graph = ShaderGraph()
        self.node_library = NodeLibrary()
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        
        # Левая панель - библиотека узлов
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Поиск узлов
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search nodes...")
        search_layout.addWidget(self.search_edit)
        left_layout.addLayout(search_layout)
        
        # Список узлов
        self.node_list = QListWidget()
        self.populate_node_list()
        left_layout.addWidget(self.node_list)
        
        main_layout.addWidget(left_panel, 1)
        
        # Центральная панель - редактор графа
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        # Панель инструментов
        toolbar = QHBoxLayout()
        self.new_btn = QPushButton("New")
        self.save_btn = QPushButton("Save")
        self.load_btn = QPushButton("Load")
        self.compile_btn = QPushButton("Compile")
        
        toolbar.addWidget(self.new_btn)
        toolbar.addWidget(self.save_btn)
        toolbar.addWidget(self.load_btn)
        toolbar.addWidget(self.compile_btn)
        toolbar.addStretch()
        
        center_layout.addLayout(toolbar)
        
        # Редактор графа
        self.graph_editor = ShaderEditorView()
        self.graph_editor.set_graph(self.current_graph)
        center_layout.addWidget(self.graph_editor)
        
        main_layout.addWidget(center_panel, 3)
        
        # Правая панель - свойства и код
        right_panel = QSplitter(Qt.Vertical)
        
        # Редактор свойств
        self.property_editor = PropertyEditor()
        right_panel.addWidget(self.property_editor)
        
        # Редактор кода
        code_group = QGroupBox("Generated Code")
        code_layout = QVBoxLayout(code_group)
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 10))
        
        # Добавляем подсветку синтаксиса
        self.highlighter = GLSLHighlighter(self.code_editor.document())
        
        code_layout.addWidget(self.code_editor)
        right_panel.addWidget(code_group)
        
        right_panel.setSizes([300, 200])
        main_layout.addWidget(right_panel, 1)
        
        # Подключаем сигналы
        self.new_btn.clicked.connect(self.new_shader)
        self.save_btn.clicked.connect(self.save_shader)
        self.load_btn.clicked.connect(self.load_shader)
        self.compile_btn.clicked.connect(self.compile_shader)
        self.node_list.itemDoubleClicked.connect(self.add_selected_node)
        self.graph_editor.node_selected.connect(self.property_editor.set_node)
        self.search_edit.textChanged.connect(self.filter_node_list)
        
    def populate_node_list(self):
        """Заполняем список доступных узлов"""
        self.node_list.clear()
        
        categories = {
            "Input Nodes": ["texture_2d", "color", "time"],
            "Math Nodes": ["add", "multiply", "subtract", "divide"],
            "Vector Nodes": ["combine", "separate"],
            "Output Nodes": ["fragment_output"]
        }
        
        for category, node_ids in categories.items():
            category_item = QListWidgetItem(category)
            category_item.setFlags(Qt.NoItemFlags)
            category_item.setBackground(QColor(60, 60, 70))
            category_item.setForeground(QColor(255, 255, 255))
            self.node_list.addItem(category_item)
            
            for node_id in node_ids:
                node_template = self.node_library.nodes.get(node_id)
                if node_template:
                    item = QListWidgetItem(f"  {node_template['title']}")
                    item.setData(Qt.UserRole, node_id)
                    self.node_list.addItem(item)
    
    def filter_node_list(self, text):
        """Фильтрация списка узлов"""
        for i in range(self.node_list.count()):
            item = self.node_list.item(i)
            # Пропускаем категории
            if not item.data(Qt.UserRole):
                continue
                
            item.setHidden(text.lower() not in item.text().lower())
    
    def add_selected_node(self, item):
        """Добавляем выбранный узел в граф"""
        node_id = item.data(Qt.UserRole)
        if not node_id:
            return
            
        # Позиция в центре редактора
        center_pos = self.graph_editor.mapToScene(self.graph_editor.viewport().rect().center())
        new_node = self.node_library.create_node_from_template(node_id, center_pos)
        
        if new_node:
            self.current_graph.add_node(new_node)
            self.graph_editor.update_display()
            self.graph_editor.select_node(new_node)
    
    def new_shader(self):
        """Создать новый шейдер"""
        self.current_graph = ShaderGraph()
        self.graph_editor.set_graph(self.current_graph)
        self.property_editor.set_node(None)
        self.code_editor.clear()
    
    def save_shader(self):
        """Сохранить шейдер в файл"""
        # TODO: Реализовать сохранение
        pass
    
    def load_shader(self):
        """Загрузить шейдер из файла"""
        # TODO: Реализовать загрузку
        pass
    
    def compile_shader(self):
        """Скомпилировать шейдер"""
        code = self.current_graph.generate_glsl_code()
        self.code_editor.setPlainText(code)

# Плагин шейдерного редактора
class ShaderEditorPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.name = "Shader Editor"
        self.version = "1.0.0"
        self.description = "Visual node-based shader editor"
        
    def initialize(self, app):
        self.editor = ShaderEditor()
        
        shader_dock = QDockWidget("Shader Editor", app)
        shader_dock.setWidget(self.editor)
        app.addDockWidget(Qt.RightDockWidgetArea, shader_dock)
        
        # Добавляем тестовые узлы
        self.editor.new_shader()
        
        # Создаем простой шейдер по умолчанию
        texture_node = self.editor.node_library.create_node_from_template("texture_2d", QPointF(100, 100))
        color_node = self.editor.node_library.create_node_from_template("color", QPointF(100, 200))
        output_node = self.editor.node_library.create_node_from_template("fragment_output", QPointF(300, 150))
        
        if texture_node and color_node and output_node:
            self.editor.current_graph.add_node(texture_node)
            self.editor.current_graph.add_node(color_node)
            self.editor.current_graph.add_node(output_node)
            
            # Соединяем узлы
            self.editor.current_graph.connect(texture_node.node_id, "color", output_node.node_id, "color")
            
            self.editor.graph_editor.update_display()