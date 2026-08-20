"""
8通道调试控制系统 - PyQt5 桌面版
基于 plan.md 设计规划，工业风工控UI操作界面
"""
import sys
import os
import json
import uuid
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QStackedWidget, QSplitter, QFrame, QRadioButton, QButtonGroup,
    QScrollArea, QMessageBox, QStatusBar, QSizePolicy, QSpacerItem,
    QCheckBox, QAbstractItemView, QStyleFactory
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QIntValidator, QDoubleValidator

import serial
import serial.tools.list_ports

import config_manager

# ═══════════════════════════════════════════════════════════════════════
# 全局样式表 — 简洁工业风：灰色系、扁平按钮、清晰边框
# ═══════════════════════════════════════════════════════════════════════
STYLE_SHEET = """
QMainWindow {
    background: #e8e8e8;
}
QWidget {
    font-family: "Microsoft YaHei", "PingFang SC", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: #333;
}

/* ── 按钮 ── */
QPushButton {
    background: #555;
    color: #fff;
    border: none;
    padding: 5px 14px;
    font-size: 12px;
    border-radius: 2px;
    min-height: 22px;
}
QPushButton:hover { background: #3a3a3a; }
QPushButton:pressed { background: #222; }
QPushButton:disabled { background: #c0c0c0; color: #999; }

/* 特殊按钮 */
QPushButton#btnSend {
    background: #455a64;
    padding: 8px 40px;
    font-size: 14px;
    font-weight: bold;
    letter-spacing: 3px;
}
QPushButton#btnSend:hover { background: #37474f; }
QPushButton#btnDanger { background: #c62828; }
QPushButton#btnDanger:hover { background: #b71c1c; }
QPushButton#btnNav {
    background: #e0e0e0;
    color: #333;
    border: 1px solid #bbb;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    padding: 8px 32px;
    font-size: 14px;
    font-weight: 600;
}
QPushButton#btnNav[active="true"] {
    background: #fff;
    border-bottom: 2px solid #555;
    color: #000;
}
QPushButton#btnNav:hover { background: #f0f0f0; }

/* ── 输入框 ── */
QLineEdit {
    border: 1px solid #bbb;
    border-radius: 2px;
    padding: 4px 6px;
    background: #fff;
    min-height: 24px;
}
QLineEdit:focus { border-color: #555; }
QLineEdit:disabled { background: #eee; color: #999; border-color: #ddd; }

/* ── 下拉框 ── */
QComboBox {
    border: 1px solid #bbb;
    border-radius: 2px;
    padding: 3px 8px;
    background: #fff;
    min-height: 24px;
}
QComboBox:focus { border-color: #555; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    border: 1px solid #ccc;
    selection-background-color: #555;
    selection-color: #fff;
}

/* ── 分组框 ── */
QGroupBox {
    border: 1px solid #ccc;
    border-radius: 4px;
    margin-top: 8px;
    padding: 16px 8px 8px;
    font-weight: 600;
    background: #fff;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    color: #333;
}

/* ── 表格 ── */
QTableWidget {
    border: 1px solid #ddd;
    gridline-color: #f0f0f0;
    background: #fff;
    selection-background-color: #e0e0e0;
    selection-color: #333;
}
QHeaderView::section {
    background: #f5f5f5;
    border: none;
    border-bottom: 1px solid #ddd;
    border-right: 1px solid #eee;
    padding: 6px 4px;
    font-weight: 600;
    color: #666;
    font-size: 12px;
}

/* ── 标签页 ── */
QTabWidget::pane {
    border: 1px solid #ccc;
    background: #fff;
    top: -1px;
}
QTabBar::tab {
    background: #e8e8e8;
    border: 1px solid #ccc;
    padding: 6px 20px;
    margin-right: 1px;
    font-size: 13px;
}
QTabBar::tab:selected {
    background: #fff;
    border-bottom: 2px solid #555;
    font-weight: 600;
}
QTabBar::tab:hover { background: #f0f0f0; }

/* ── 滚动区域 ── */
QScrollArea {
    border: none;
    background: transparent;
}

/* ── 分割器 ── */
QSplitter::handle {
    background: #ccc;
    width: 3px;
}

/* ── 状态栏 ── */
QStatusBar {
    background: #f5f5f5;
    border-top: 1px solid #ddd;
    font-size: 12px;
    color: #666;
}

/* ── 单选按钮 ── */
QRadioButton {
    spacing: 4px;
    font-size: 12px;
}

/* ── 复选框 ── */
QCheckBox {
    spacing: 4px;
    font-size: 12px;
}

/* ── 滚动条 ── */
QScrollBar:vertical {
    width: 8px;
    background: #f0f0f0;
    border: none;
}
QScrollBar::handle:vertical {
    background: #bbb;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── 当前参数面板 ── */
#currentParamsPanel {
    background: #fff;
    border: 1px solid #ccc;
    border-radius: 4px;
}
#currentParamsTitle {
    font-size: 14px;
    font-weight: 700;
    color: #333;
    padding: 8px 0;
    border-bottom: 1px solid #e0e0e0;
}
.current-ch-row {
    padding: 4px 0;
    border-bottom: 1px solid #f5f5f5;
}
.current-ch-name {
    font-size: 12px;
    color: #999;
}
.current-ch-value {
    font-size: 16px;
    font-weight: 700;
    color: #333;
}
.current-ch-placeholder {
    font-size: 16px;
    font-weight: 700;
    color: #ccc;
}
.current-ch-updated {
    color: #1565c0;
}

/* ── 接收日志 ── */
#rawLogArea {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 11px;
    background: #fafafa;
    border: 1px solid #ddd;
    border-radius: 2px;
    color: #555;
}

/* ── 提示框 ── */
QToolTip {
    background: #333;
    color: #fff;
    border: none;
    padding: 4px 8px;
    font-size: 12px;
}
"""

# ═══════════════════════════════════════════════════════════════════════
# 串口通信线程
# ═══════════════════════════════════════════════════════════════════════


class SerialWorker(QThread):
    """后台串口通信线程：发送指令 + 接收下位机上报数据，避免阻塞 UI"""
    connected = pyqtSignal(bool)
    error = pyqtSignal(str)
    send_done = pyqtSignal(int)
    data_received = pyqtSignal(dict)   # 解析后的通道参数 {ch_id: value, ...}
    raw_data = pyqtSignal(str)         # 原始接收数据（调试用）

    def __init__(self):
        super().__init__()
        self._serial: serial.Serial | None = None
        self._port = ""
        self._baudrate = 115200
        self._running = False
        self._pending_commands: list[str] = []
        self._recv_buffer = b""

    def set_pending(self, commands: list[str]):
        self._pending_commands = commands

    def connect_serial(self, port: str, baudrate: int):
        self._port = port
        self._baudrate = baudrate
        if not self._running:
            self._running = True
            self.start()

    def disconnect_serial(self):
        self._running = False
        if self._serial and self._serial.is_open:
            try:
                self._serial.close()
            except Exception:
                pass
        self._serial = None
        self.connected.emit(False)

    def run(self):
        """线程主循环：发送指令 + 持续读取下位机上报数据"""
        try:
            self._serial = serial.Serial(
                self._port, self._baudrate, timeout=0.05
            )
            self.connected.emit(True)
        except Exception as e:
            self.error.emit(str(e))
            self.connected.emit(False)
            self._running = False
            return

        self._recv_buffer = b""
        while self._running:
            # ── 发送待发指令 ──
            if self._pending_commands:
                cmd = self._pending_commands.pop(0)
                try:
                    self._serial.write(cmd.encode("utf-8"))
                    self.send_done.emit(1)
                except Exception as e:
                    self.error.emit(f"发送失败: {e}")

            # ── 读取下位机上报数据 ──
            try:
                if self._serial.in_waiting > 0:
                    chunk = self._serial.read(self._serial.in_waiting)
                    self._recv_buffer += chunk
                    # 按行解析
                    while b"\n" in self._recv_buffer:
                        line, self._recv_buffer = self._recv_buffer.split(b"\n", 1)
                        line_str = line.decode("utf-8", errors="replace").strip()
                        if line_str:
                            self.raw_data.emit(line_str)
                            parsed = self._parse_line(line_str)
                            if parsed:
                                self.data_received.emit(parsed)
            except Exception:
                pass

            self.msleep(30)

        if self._serial and self._serial.is_open:
            try:
                self._serial.close()
            except Exception:
                pass

    def _parse_line(self, line: str) -> dict | None:
        """尝试从接收行中解析通道参数。
        支持格式：
          - "CH0=100" / "CH0:100" / "CH0 100"
          - "CH0=100,CH1=200,..."
          - JSON: {"0": "100", "1": "200"}
        """
        result: dict = {}

        # 尝试 JSON 解析
        if line.startswith("{") and line.endswith("}"):
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        try:
                            result[int(k)] = str(v)
                        except (ValueError, TypeError):
                            pass
                    if result:
                        return result
            except json.JSONDecodeError:
                pass

        # 尝试逗号分隔的多通道格式 "CH0=100,CH1=200"
        if "," in line:
            parts = [p.strip() for p in line.split(",")]
        else:
            parts = [line]

        import re
        for part in parts:
            # 匹配 CH{n}=val, CH{n}:val, CH{n} val, n=val 等
            m = re.search(r'(?:CH\s*)?(\d+)\s*[=:>\s]\s*(-?[\d.]+)', part, re.IGNORECASE)
            if m:
                ch_id = int(m.group(1))
                val = m.group(2)
                if 0 <= ch_id <= 7:
                    result[ch_id] = val

        return result if result else None

    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def stop(self):
        self._running = False
        self.wait(1000)


# ═══════════════════════════════════════════════════════════════════════
# 通道卡片组件（调试面板用）
# ═══════════════════════════════════════════════════════════════════════


class ChannelCard(QFrame):
    """单个通道的调试卡片：CH标签、名称、数值输入、+/- 按钮、锁定标记"""

    value_changed = pyqtSignal(int, str)  # ch_id, value

    def __init__(self, ch_id: int, parent=None):
        super().__init__(parent)
        self.ch_id = ch_id
        self._step = 1.0
        self._max_val = None
        self._min_val = None
        self._locked = False
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("chCard")
        self.setStyleSheet("""
            #chCard {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 8px;
                background: #fafafa;
            }
            #chCard:hover { border-color: #aaa; }
        """)
        self.setFixedHeight(155)
        self.setMinimumWidth(150)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # 通道头部
        header = QHBoxLayout()
        self.lbl_id = QLabel(f"CH{self.ch_id}")
        self.lbl_id.setStyleSheet("color: #aaa; font-size: 10px;")
        header.addWidget(self.lbl_id)
        header.addStretch()
        self.lbl_name = QLabel("")
        self.lbl_name.setStyleSheet("font-weight: 600; font-size: 12px; color: #333;")
        header.addWidget(self.lbl_name)
        layout.addLayout(header)

        # 数值输入 (电压V)
        self.input_val = QLineEdit("")
        self.input_val.setAlignment(Qt.AlignCenter)
        self.input_val.setStyleSheet("font-size: 18px; font-weight: bold; min-height: 36px;")
        self.input_val.setPlaceholderText("--")
        self.input_val.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.input_val)

        # 电流显示 (仅显示, 不参与下发协议)
        # 第三个通道CH2: -9V→9A, 0V→0A   其他通道: -9V→1A, 0V→0A
        self.lbl_current = QLabel("电流: -- A")
        self.lbl_current.setAlignment(Qt.AlignCenter)
        self.lbl_current.setStyleSheet(
            "font-size: 11px; color: #1565c0; background: #eef4fb;"
            "border-radius: 2px; padding: 2px 4px;"
        )
        layout.addWidget(self.lbl_current)

        # 底部：+/- 按钮 + 锁定标记
        footer = QHBoxLayout()
        footer.setSpacing(4)

        self.btn_minus = QPushButton("−")
        self.btn_minus.setFixedSize(30, 26)
        self.btn_minus.setStyleSheet(
            "QPushButton{font-size:14px;font-weight:bold;border:1px solid #bbb;background:#fff;color:#333;}"
            "QPushButton:hover:!disabled{background:#555;color:#fff;}"
            "QPushButton:disabled{background:#eee;color:#ccc;}"
        )
        self.btn_minus.clicked.connect(lambda: self._adjust(-1))
        footer.addWidget(self.btn_minus)

        self.btn_plus = QPushButton("+")
        self.btn_plus.setFixedSize(30, 26)
        self.btn_plus.setStyleSheet(
            "QPushButton{font-size:14px;font-weight:bold;border:1px solid #bbb;background:#fff;color:#333;}"
            "QPushButton:hover:!disabled{background:#555;color:#fff;}"
            "QPushButton:disabled{background:#eee;color:#ccc;}"
        )
        self.btn_plus.clicked.connect(lambda: self._adjust(1))
        footer.addWidget(self.btn_plus)

        footer.addStretch()

        self.lbl_tag = QLabel("可调")
        self.lbl_tag.setFixedWidth(42)
        self.lbl_tag.setAlignment(Qt.AlignCenter)
        self.lbl_tag.setStyleSheet(
            "font-size: 10px; font-weight: 600; border-radius: 2px; padding: 2px 6px;"
        )
        footer.addWidget(self.lbl_tag)

        layout.addLayout(footer)

    def _on_text_changed(self, text: str):
        self.value_changed.emit(self.ch_id, text)
        self._update_current(text)

    def _update_current(self, text: str):
        """电压→电流换算 (仅显示, 不改下发协议)
        第三个通道 (CH2, 即第3通道): -9V→9A, 0V→0A → 电流 = -V
        其他通道: -9V→1A, 0V→0A → 电流 = -V/9
        """
        try:
            v = float(text) if text else 0.0
        except ValueError:
            self.lbl_current.setText("电流: -- A")
            return

        if self.ch_id == 2:
            cur = -v
        else:
            cur = -v / 9.0

        self.lbl_current.setText(f"电流: {cur:.3f} A")

    def _adjust(self, direction: int):
        try:
            val = float(self.input_val.text()) if self.input_val.text() else 0.0
        except ValueError:
            val = 0.0
        val += direction * self._step
        if self._min_val is not None:
            val = max(val, self._min_val)
        if self._max_val is not None:
            val = min(val, self._max_val)
        # 按步长取整
        if self._step and self._step > 0:
            val = round(val / self._step) * self._step
            # 避免浮点误差
            decimals = max(0, len(str(self._step).split(".")[-1]) if "." in str(self._step) else 0)
            val = round(val, decimals)
        self.input_val.setText(str(val))

    def set_name(self, name: str):
        self.lbl_name.setText(name)

    def set_value(self, value: str):
        self.input_val.blockSignals(True)
        self.input_val.setText(value)
        self.input_val.blockSignals(False)
        self._update_current(value)

    def get_value(self) -> str:
        return self.input_val.text()

    def set_locked(self, locked: bool, locked_value: str = ""):
        self._locked = locked
        self.input_val.setDisabled(locked)
        self.btn_plus.setDisabled(locked)
        self.btn_minus.setDisabled(locked)
        if locked:
            self.lbl_tag.setText("锁定")
            self.lbl_tag.setStyleSheet(
                "font-size:10px;font-weight:600;border-radius:2px;padding:2px 6px;"
                "background:#ffcdd2;color:#c62828;"
            )
            self.setStyleSheet(self.styleSheet() + "#chCard{background:#f5f5f5;}")
            if locked_value:
                self.set_value(locked_value)
        else:
            self.lbl_tag.setText("可调")
            self.lbl_tag.setStyleSheet(
                "font-size:10px;font-weight:600;border-radius:2px;padding:2px 6px;"
                "background:#c8e6c9;color:#2e7d32;"
            )

    def set_limits(self, max_val, min_val, step):
        self._max_val = max_val if max_val not in (None, "") else None
        self._min_val = min_val if min_val not in (None, "") else None
        self._step = float(step) if step not in (None, "", 0) else 1.0


# ═══════════════════════════════════════════════════════════════════════
# 主窗口
# ═══════════════════════════════════════════════════════════════════════


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("8通道调试控制系统")
        self.resize(1280, 800)
        self.setMinimumSize(1024, 680)

        # 数据
        self.config: dict = {}
        self.current_mode_id: str | None = None
        self._channel_cards: list[ChannelCard] = []
        self._editing_mode_id: str | None = None
        self._is_new_mode = False
        self._received_values: dict[int, str] = {}   # 下位机上报的当前参数 {ch_id: value}
        self._current_value_labels: list[QLabel] = []  # 当前参数显示标签
        self._raw_log_lines: list[str] = []           # 接收日志（保留最近 200 行）

        # 串口
        self._serial_worker = SerialWorker()
        self._serial_worker.connected.connect(self._on_serial_status)
        self._serial_worker.error.connect(self._on_serial_error)
        self._serial_worker.send_done.connect(self._on_send_done)
        self._serial_worker.data_received.connect(self._on_data_received)
        self._serial_worker.raw_data.connect(self._on_raw_data)

        # 定时刷新串口列表
        self._port_timer = QTimer(self)
        self._port_timer.timeout.connect(self._refresh_serial_ports)
        self._port_timer.start(2000)

        self._init_ui()
        self._load_config()
        self._refresh_serial_ports()
        self._update_received_display()

    # ────────────────────────── UI 构建 ──────────────────────────

    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── 顶部 Header ──
        self._build_header(root)

        # ── 导航栏 ──
        self._build_nav(root)

        # ── 内容区（QStackedWidget） ──
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_frontend_page())  # index 0
        self.stack.addWidget(self._build_backend_page())   # index 1
        root.addWidget(self.stack, 1)

        # ── 状态栏 ──
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 — 请连接串口后开始调试")

    def _build_header(self, root_layout: QVBoxLayout):
        header = QFrame()
        header.setStyleSheet("QFrame{background:#fff;border-bottom:1px solid #ccc;}")
        header.setFixedHeight(48)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 4, 16, 4)
        h_layout.setSpacing(10)

        # 标题
        title = QLabel("8通道调试控制系统")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #222;")
        h_layout.addWidget(title)

        h_layout.addStretch()

        # 串口选择
        lbl_port = QLabel("串口")
        lbl_port.setStyleSheet("font-size:12px;color:#666;")
        h_layout.addWidget(lbl_port)

        self.combo_port = QComboBox()
        self.combo_port.setMinimumWidth(130)
        self.combo_port.addItem("选择端口", "")
        h_layout.addWidget(self.combo_port)

        btn_refresh = QPushButton("刷新")
        btn_refresh.setFixedWidth(48)
        btn_refresh.clicked.connect(self._refresh_serial_ports)
        h_layout.addWidget(btn_refresh)

        lbl_baud = QLabel("波特率")
        lbl_baud.setStyleSheet("font-size:12px;color:#666;")
        h_layout.addWidget(lbl_baud)

        self.combo_baud = QComboBox()
        self.combo_baud.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.combo_baud.setCurrentText("115200")
        self.combo_baud.setFixedWidth(80)
        h_layout.addWidget(self.combo_baud)

        # 连接按钮
        self.btn_connect = QPushButton("连接")
        self.btn_connect.clicked.connect(self._toggle_serial)
        h_layout.addWidget(self.btn_connect)

        # 状态指示
        self.lbl_serial_status = QLabel("● 未连接")
        self.lbl_serial_status.setStyleSheet("font-size:12px;color:#999;")
        h_layout.addWidget(self.lbl_serial_status)

        root_layout.addWidget(header)

    def _build_nav(self, root_layout: QVBoxLayout):
        nav = QFrame()
        nav.setStyleSheet("QFrame{background:#e8e8e8;padding:0 20px;}")
        nav.setFixedHeight(38)
        n_layout = QHBoxLayout(nav)
        n_layout.setContentsMargins(20, 0, 20, 0)
        n_layout.setSpacing(2)
        n_layout.setAlignment(Qt.AlignLeft)

        self.btn_nav_front = QPushButton("前台")
        self.btn_nav_front.setObjectName("btnNav")
        self.btn_nav_front.setProperty("active", True)
        self.btn_nav_front.clicked.connect(lambda: self._switch_page(0))
        n_layout.addWidget(self.btn_nav_front)

        self.btn_nav_back = QPushButton("后台")
        self.btn_nav_back.setObjectName("btnNav")
        self.btn_nav_back.setProperty("active", False)
        self.btn_nav_back.clicked.connect(lambda: self._switch_page(1))
        n_layout.addWidget(self.btn_nav_back)

        n_layout.addStretch()
        root_layout.addWidget(nav)

    # ──────────────────────── 前台页面 ────────────────────────

    def _build_frontend_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 10, 16, 10)

        tabs = QTabWidget()
        tabs.addTab(self._build_debug_tab(), "调试面板")
        tabs.addTab(self._build_global_settings_tab(), "全局数值设置")
        layout.addWidget(tabs)
        return page

    def _build_debug_tab(self) -> QWidget:
        tab = QWidget()
        outer = QHBoxLayout(tab)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        # ═══ 左侧：当前参数（下位机上报） ═══
        left_panel = QFrame()
        left_panel.setObjectName("currentParamsPanel")
        left_panel.setFixedWidth(220)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 6, 10, 10)
        left_layout.setSpacing(2)

        title = QLabel("当前参数")
        title.setObjectName("currentParamsTitle")
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)

        self._current_value_labels = []
        for i in range(8):
            row_w = QWidget()
            row_w.setProperty("class", "current-ch-row")
            row_layout = QHBoxLayout(row_w)
            row_layout.setContentsMargins(4, 3, 4, 3)
            row_layout.setSpacing(6)

            # 通道标签
            ch_label = QLabel(f"CH{i}")
            ch_label.setStyleSheet("font-weight:600;font-size:12px;color:#888;min-width:28px;")
            row_layout.addWidget(ch_label)

            # 数值标签（下位机上报值）
            val_label = QLabel("--")
            val_label.setStyleSheet("font-size:16px;font-weight:700;color:#ccc;")
            val_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            row_layout.addWidget(val_label, 1)

            row_layout.addStretch()
            left_layout.addWidget(row_w)
            self._current_value_labels.append(val_label)

        # 分隔线 + 接收日志标题
        left_layout.addSpacing(8)
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#ddd;")
        left_layout.addWidget(sep)
        left_layout.addSpacing(4)

        log_header = QLabel("接收日志")
        log_header.setStyleSheet("font-size:11px;font-weight:600;color:#999;")
        left_layout.addWidget(log_header)

        # 原始接收日志
        self.raw_log = QLabel("等待下位机数据…")
        self.raw_log.setObjectName("rawLogArea")
        self.raw_log.setWordWrap(True)
        self.raw_log.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.raw_log.setMinimumHeight(60)
        self.raw_log.setStyleSheet(
            "font-family:'Consolas','Courier New',monospace;font-size:10px;"
            "background:#fafafa;border:1px solid #ddd;border-radius:2px;"
            "color:#888;padding:4px 6px;"
        )
        left_layout.addWidget(self.raw_log, 1)

        outer.addWidget(left_panel)

        # ═══ 右侧：调试控制 ═══
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        # 模式选择行
        top_row = QHBoxLayout()
        lbl_mode = QLabel("模式选择：")
        lbl_mode.setStyleSheet("font-weight:600;font-size:13px;")
        top_row.addWidget(lbl_mode)

        self.combo_mode = QComboBox()
        self.combo_mode.setMinimumWidth(280)
        self.combo_mode.addItem("-- 无模式（自由调试）--", "")
        self.combo_mode.currentIndexChanged.connect(self._on_mode_selected)
        top_row.addWidget(self.combo_mode)

        top_row.addStretch()

        self.btn_send = QPushButton("一键下发")
        self.btn_send.setObjectName("btnSend")
        self.btn_send.clicked.connect(self._send_debug_values)
        top_row.addWidget(self.btn_send)

        right_layout.addLayout(top_row)

        # 8通道网格：2行 × 4列
        grid_frame = QFrame()
        grid_frame.setStyleSheet("QFrame{background:#fff;border:1px solid #ccc;border-radius:4px;padding:12px;}")
        grid = QGridLayout(grid_frame)
        grid.setSpacing(10)

        self._channel_cards = []
        for i in range(8):
            card = ChannelCard(i)
            card.value_changed.connect(self._on_channel_value_changed)
            self._channel_cards.append(card)
            row, col = divmod(i, 4)
            grid.addWidget(card, row, col)

        right_layout.addWidget(grid_frame, 1)

        outer.addWidget(right_panel, 1)

        return tab

    def _build_global_settings_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)

        # 表格
        self.global_table = QTableWidget(8, 5)
        self.global_table.setHorizontalHeaderLabels(["通道", "名称", "最大值", "最小值", "步长"])
        self.global_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.global_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.global_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.global_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.global_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.global_table.setColumnWidth(0, 50)
        self.global_table.verticalHeader().setVisible(False)
        self.global_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.global_table.setSelectionMode(QAbstractItemView.NoSelection)

        layout.addWidget(self.global_table, 1)

        # 保存按钮
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_save_global = QPushButton("保存全局参数")
        btn_save_global.clicked.connect(self._save_global_settings)
        btn_row.addWidget(btn_save_global)
        layout.addLayout(btn_row)

        return tab

    # ──────────────────────── 后台页面 ────────────────────────

    def _build_backend_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(16, 10, 16, 10)

        # 工具栏
        toolbar = QHBoxLayout()
        btn_new = QPushButton("新建模式")
        btn_new.clicked.connect(self._new_mode)
        toolbar.addWidget(btn_new)

        self.btn_edit_mode = QPushButton("编辑")
        self.btn_edit_mode.clicked.connect(self._edit_mode)
        self.btn_edit_mode.setEnabled(False)
        toolbar.addWidget(self.btn_edit_mode)

        btn_delete = QPushButton("删除")
        btn_delete.setObjectName("btnDanger")
        btn_delete.clicked.connect(self._delete_mode)
        toolbar.addWidget(btn_delete)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # 左右分割器
        splitter = QSplitter(Qt.Horizontal)

        # 左侧：模式列表
        left_panel = QFrame()
        left_panel.setStyleSheet("QFrame{background:#fff;border:1px solid #ccc;border-radius:4px;}")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(8, 8, 8, 8)

        left_title = QLabel("模式列表")
        left_title.setStyleSheet("font-weight:600;font-size:13px;padding-bottom:4px;border-bottom:1px solid #ddd;")
        left_layout.addWidget(left_title)

        self.mode_list = QTableWidget(0, 4)
        self.mode_list.setHorizontalHeaderLabels(["一级", "二级", "三级", "锁定/可调"])
        self.mode_list.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.mode_list.verticalHeader().setVisible(False)
        self.mode_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.mode_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.mode_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.mode_list.itemSelectionChanged.connect(self._on_mode_list_selection)
        left_layout.addWidget(self.mode_list, 1)

        splitter.addWidget(left_panel)

        # 右侧：模式编辑器
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setStyleSheet("QScrollArea{background:#fff;border:1px solid #ccc;border-radius:4px;}")

        self.mode_editor = QWidget()
        self.mode_editor_layout = QVBoxLayout(self.mode_editor)
        self.mode_editor_layout.setContentsMargins(16, 16, 16, 16)
        self.mode_editor_layout.setSpacing(8)
        self._build_mode_editor_form()
        right_scroll.setWidget(self.mode_editor)

        splitter.addWidget(right_scroll)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter, 1)
        return page

    def _build_mode_editor_form(self):
        """构建模式编辑器表单（动态内容在 _populate_mode_editor 中填充）"""
        self.editor_widgets: dict = {}
        # 占位 label
        placeholder = QLabel("请选择一个模式或点击「新建模式」")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color:#bbb;font-size:14px;padding:40px;")
        self.editor_placeholder = placeholder
        self.mode_editor_layout.addWidget(placeholder)

        # 创建可折叠的编辑器区域（初始隐藏）
        self.editor_content = QWidget()
        self.editor_content_layout = QVBoxLayout(self.editor_content)
        self.editor_content_layout.setContentsMargins(0, 0, 0, 0)
        self.editor_content_layout.setSpacing(8)
        self.editor_content.hide()
        self.mode_editor_layout.addWidget(self.editor_content)

        # ── 基本信息 ──
        basic_group = QGroupBox("基本信息")
        basic_layout = QVBoxLayout(basic_group)
        for field, key in [("一级菜单 *", "l1"), ("二级菜单", "l2"), ("三级菜单", "l3")]:
            row = QHBoxLayout()
            lbl = QLabel(field)
            lbl.setFixedWidth(80)
            lbl.setStyleSheet("font-weight:normal;color:#666;")
            row.addWidget(lbl)
            edit = QLineEdit()
            edit.setPlaceholderText("必填" if key == "l1" else "可选")
            row.addWidget(edit)
            basic_layout.addLayout(row)
            self.editor_widgets[key] = edit
        self.editor_content_layout.addWidget(basic_group)

        # ── 通道锁定规则 ──
        ch_group = QGroupBox("通道锁定规则 & 限值")
        ch_layout = QVBoxLayout(ch_group)

        self._ch_editor_widgets: list[dict] = []
        for i in range(8):
            ch_row = QHBoxLayout()
            ch_row.setSpacing(6)

            lbl = QLabel(f"CH{i}")
            lbl.setFixedWidth(32)
            lbl.setStyleSheet("font-weight:600;color:#555;")
            ch_row.addWidget(lbl)

            # 锁定/可调 单选
            radio_locked = QRadioButton("锁定")
            radio_unlocked = QRadioButton("可调")
            radio_unlocked.setChecked(True)
            bg = QButtonGroup(self)
            bg.addButton(radio_locked, 0)
            bg.addButton(radio_unlocked, 1)
            ch_row.addWidget(radio_locked)
            ch_row.addWidget(radio_unlocked)

            # 锁定值
            edit_locked_val = QLineEdit()
            edit_locked_val.setPlaceholderText("锁定值")
            edit_locked_val.setFixedWidth(70)
            edit_locked_val.hide()
            ch_row.addWidget(edit_locked_val)

            # 限值（上限、下限、步长）
            edit_max = QLineEdit()
            edit_max.setPlaceholderText("上限")
            edit_max.setFixedWidth(60)
            ch_row.addWidget(edit_max)

            edit_min = QLineEdit()
            edit_min.setPlaceholderText("下限")
            edit_min.setFixedWidth(60)
            ch_row.addWidget(edit_min)

            edit_step = QLineEdit()
            edit_step.setPlaceholderText("步长")
            edit_step.setFixedWidth(60)
            ch_row.addWidget(edit_step)

            ch_row.addStretch()

            # 切换锁定/可调时显示/隐藏对应控件
            def make_toggle(lv_edit, max_e, min_e, step_e):
                def toggle(locked):
                    lv_edit.setVisible(locked)
                    max_e.setVisible(not locked)
                    min_e.setVisible(not locked)
                    step_e.setVisible(not locked)
                return toggle
            toggle_fn = make_toggle(edit_locked_val, edit_max, edit_min, edit_step)
            radio_locked.toggled.connect(lambda checked, fn=toggle_fn: fn(checked))

            ch_layout.addLayout(ch_row)

            self._ch_editor_widgets.append({
                "radio_locked": radio_locked,
                "radio_unlocked": radio_unlocked,
                "locked_val": edit_locked_val,
                "max": edit_max,
                "min": edit_min,
                "step": edit_step,
            })

        self.editor_content_layout.addWidget(ch_group)

        # ── 高级设置 ──
        adv_group = QGroupBox("高级设置")
        adv_layout = QVBoxLayout(adv_group)

        row_tpl = QHBoxLayout()
        lbl_tpl = QLabel("指令模板")
        lbl_tpl.setFixedWidth(80)
        lbl_tpl.setStyleSheet("font-weight:normal;color:#666;")
        row_tpl.addWidget(lbl_tpl)
        self.editor_widgets["template"] = QLineEdit()
        self.editor_widgets["template"].setPlaceholderText("留空使用全局模板：SET CH{n}={val}\\n")
        row_tpl.addWidget(self.editor_widgets["template"])
        adv_layout.addLayout(row_tpl)

        row_mmax = QHBoxLayout()
        lbl_mmax = QLabel("MCU上限")
        lbl_mmax.setFixedWidth(80)
        lbl_mmax.setStyleSheet("font-weight:normal;color:#666;")
        row_mmax.addWidget(lbl_mmax)
        self.editor_widgets["mcu_max"] = QLineEdit()
        self.editor_widgets["mcu_max"].setPlaceholderText("可选")
        row_mmax.addWidget(self.editor_widgets["mcu_max"])
        adv_layout.addLayout(row_mmax)

        row_mmin = QHBoxLayout()
        lbl_mmin = QLabel("MCU下限")
        lbl_mmin.setFixedWidth(80)
        lbl_mmin.setStyleSheet("font-weight:normal;color:#666;")
        row_mmin.addWidget(lbl_mmin)
        self.editor_widgets["mcu_min"] = QLineEdit()
        self.editor_widgets["mcu_min"].setPlaceholderText("可选")
        row_mmin.addWidget(self.editor_widgets["mcu_min"])
        adv_layout.addLayout(row_mmin)

        self.editor_content_layout.addWidget(adv_group)

        # ── 操作按钮 ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_save_mode = QPushButton("保存模式")
        self.btn_save_mode.clicked.connect(self._save_mode)
        btn_row.addWidget(self.btn_save_mode)
        btn_cancel_edit = QPushButton("取消")
        btn_cancel_edit.clicked.connect(self._cancel_edit)
        btn_row.addWidget(btn_cancel_edit)
        self.editor_content_layout.addLayout(btn_row)

        self.editor_content_layout.addStretch()

    # ═══════════════════════════════════════════════════════════════
    # 页面切换 & 配置加载
    # ═══════════════════════════════════════════════════════════════

    def _switch_page(self, index: int):
        self.stack.setCurrentIndex(index)
        self.btn_nav_front.setProperty("active", index == 0)
        self.btn_nav_back.setProperty("active", index == 1)
        # 强制刷新样式
        self.btn_nav_front.style().unpolish(self.btn_nav_front)
        self.btn_nav_front.style().polish(self.btn_nav_front)
        self.btn_nav_back.style().unpolish(self.btn_nav_back)
        self.btn_nav_back.style().polish(self.btn_nav_back)
        if index == 1:
            self._refresh_mode_list()

    def _load_config(self):
        self.config = config_manager.load_config()
        self._populate_mode_combo()
        self._populate_global_table()
        self._refresh_channel_cards()
        self._refresh_mode_list()
        self._update_received_display()

    def _save_config(self):
        config_manager.save_config(self.config)
        self.status_bar.showMessage("配置已保存", 3000)

    # ═══════════════════════════════════════════════════════════════
    # 串口管理
    # ═══════════════════════════════════════════════════════════════

    def _refresh_serial_ports(self):
        current = self.combo_port.currentData()
        self.combo_port.blockSignals(True)
        self.combo_port.clear()
        self.combo_port.addItem("选择端口", "")
        try:
            ports = serial.tools.list_ports.comports()
            for p in ports:
                self.combo_port.addItem(p.device, p.device)
        except Exception:
            pass
        # 恢复之前选择
        if current:
            idx = self.combo_port.findData(current)
            if idx >= 0:
                self.combo_port.setCurrentIndex(idx)
        self.combo_port.blockSignals(False)

    def _toggle_serial(self):
        if self._serial_worker.is_connected():
            self._serial_worker.disconnect_serial()
        else:
            port = self.combo_port.currentData()
            if not port:
                QMessageBox.warning(self, "提示", "请先选择串口")
                return
            try:
                baudrate = int(self.combo_baud.currentText())
            except ValueError:
                baudrate = 115200
            self.btn_connect.setEnabled(False)
            self.btn_connect.setText("连接中…")
            self._serial_worker.connect_serial(port, baudrate)

    def _on_serial_status(self, connected: bool):
        self.btn_connect.setEnabled(True)
        if connected:
            self.btn_connect.setText("断开")
            self.lbl_serial_status.setText("● 已连接")
            self.lbl_serial_status.setStyleSheet("font-size:12px;color:#4caf50;")
            self.status_bar.showMessage("串口已连接", 3000)
        else:
            self.btn_connect.setText("连接")
            self.lbl_serial_status.setText("● 未连接")
            self.lbl_serial_status.setStyleSheet("font-size:12px;color:#999;")
            self.status_bar.showMessage("串口已断开", 3000)

    def _on_serial_error(self, msg: str):
        QMessageBox.critical(self, "串口错误", msg)
        self.btn_connect.setEnabled(True)
        self.btn_connect.setText("连接")

    def _on_send_done(self, count: int):
        self.status_bar.showMessage(f"已发送 {count} 条指令", 3000)

    def _on_data_received(self, parsed: dict):
        """接收到下位机上报的通道参数"""
        updated = False
        for ch_id, val in parsed.items():
            if 0 <= ch_id <= 7:
                self._received_values[ch_id] = val
                updated = True
        if updated:
            self._update_received_display()
            self.status_bar.showMessage(
                f"收到下位机参数: {len(parsed)} 个通道", 2000
            )

    def _on_raw_data(self, line: str):
        """原始接收数据追加到日志区"""
        self._raw_log_lines.append(line)
        # 保留最近 200 行
        if len(self._raw_log_lines) > 200:
            self._raw_log_lines = self._raw_log_lines[-200:]
        self.raw_log.setText("\n".join(self._raw_log_lines[-20:]))
        # 自动滚动到底部（QLabel 用此方式简单处理）
        self.raw_log.setToolTip(
            "\n".join(self._raw_log_lines[-50:]) if len(self._raw_log_lines) > 20 else ""
        )

    def _update_received_display(self):
        """刷新左侧当前参数面板"""
        gs = self.config.get("global_settings", {})
        channels = gs.get("channels", [])
        for i, lbl in enumerate(self._current_value_labels):
            val = self._received_values.get(i, "")
            if val:
                lbl.setText(str(val))
                lbl.setStyleSheet("font-size:16px;font-weight:700;color:#1565c0;")
            else:
                gch = channels[i] if i < len(channels) else {}
                current = gch.get("current", "")
                lbl.setText(str(current) if current else "--")
                lbl.setStyleSheet(
                    "font-size:16px;font-weight:700;color:#ccc;" if not current
                    else "font-size:16px;font-weight:700;color:#333;"
                )

    # ═══════════════════════════════════════════════════════════════
    # 调试面板逻辑
    # ═══════════════════════════════════════════════════════════════

    def _populate_mode_combo(self):
        self.combo_mode.blockSignals(True)
        self.combo_mode.clear()
        self.combo_mode.addItem("-- 无模式（自由调试）--", "")
        for m in self.config.get("modes", []):
            path = self._mode_path(m)
            self.combo_mode.addItem(path, m["id"])
        self.combo_mode.blockSignals(False)
        self.current_mode_id = None

    def _mode_path(self, mode: dict) -> str:
        parts = [mode.get("level1", "")]
        if mode.get("level2"):
            parts.append(mode["level2"])
        if mode.get("level3"):
            parts.append(mode["level3"])
        return " > ".join(filter(None, parts))

    def _on_mode_selected(self, index: int):
        mode_id = self.combo_mode.currentData()
        self.current_mode_id = mode_id if mode_id else None
        self._refresh_channel_cards()

    def _refresh_channel_cards(self):
        gs = self.config.get("global_settings", {})
        channels = gs.get("channels", [])
        mode = None
        if self.current_mode_id:
            for m in self.config.get("modes", []):
                if m["id"] == self.current_mode_id:
                    mode = m
                    break

        for i, card in enumerate(self._channel_cards):
            gch = channels[i] if i < len(channels) else {}
            card.set_name(gch.get("name", ""))

            if mode:
                lock_rules = mode.get("lock_rules", [])
                locked_values = mode.get("locked_values", [])
                limits = mode.get("limits", [])

                rule = lock_rules[i] if i < len(lock_rules) else "unlocked"
                is_locked = (rule == "locked")

                if is_locked:
                    lv = locked_values[i] if i < len(locked_values) else ""
                    card.set_locked(True, str(lv) if lv else "")
                else:
                    card.set_locked(False)
                    val = gch.get("current", "")
                    card.set_value(str(val) if val else "")

                    lim = limits[i] if i < len(limits) else {}
                    card.set_limits(
                        lim.get("max") if lim else None,
                        lim.get("min") if lim else None,
                        lim.get("step") if lim else None,
                    )
            else:
                # 无模式：全部可调
                card.set_locked(False)
                val = gch.get("current", "")
                card.set_value(str(val) if val else "")
                card.set_limits(
                    gch.get("max") if gch.get("max") != "" else None,
                    gch.get("min") if gch.get("min") != "" else None,
                    gch.get("step") if gch.get("step") != "" else None,
                )

            # 应用 MCU 全局限位
            if mode and mode.get("mcu_limit"):
                mcu = mode["mcu_limit"]
                if mcu.get("max") not in (None, ""):
                    card._max_val = float(mcu["max"]) if card._max_val is None else min(
                        card._max_val, float(mcu["max"])
                    )
                if mcu.get("min") not in (None, ""):
                    card._min_val = float(mcu["min"]) if card._min_val is None else max(
                        card._min_val, float(mcu["min"])
                    )

    def _on_channel_value_changed(self, ch_id: int, value: str):
        """通道值变化时更新 config 中的 current"""
        gs = self.config.setdefault("global_settings", {})
        channels = gs.setdefault("channels", [])
        while len(channels) <= ch_id:
            channels.append({"ch_id": len(channels), "name": "", "current": "", "max": "", "min": "", "step": ""})
        channels[ch_id]["current"] = value

    def _send_debug_values(self):
        if not self._serial_worker.is_connected():
            QMessageBox.warning(self, "提示", "请先连接串口")
            return

        mode = None
        if self.current_mode_id:
            for m in self.config.get("modes", []):
                if m["id"] == self.current_mode_id:
                    mode = m
                    break

        commands = []
        template = self.config.get("global_command_template", "SET CH{n}={val}\\n")
        if mode and mode.get("command_template"):
            template = mode["command_template"]

        for i, card in enumerate(self._channel_cards):
            val = card.get_value()
            if mode and mode.get("lock_rules", []) and i < len(mode["lock_rules"]) and mode["lock_rules"][i] == "locked":
                locked_values = mode.get("locked_values", [])
                val = str(locked_values[i]) if i < len(locked_values) and locked_values[i] else ""
            if not val:
                continue
            cmd = template.replace("{n}", str(i)).replace("{val}", val)
            commands.append(cmd)

        if not commands:
            QMessageBox.warning(self, "提示", "没有可发送的通道值")
            return

        self._serial_worker.set_pending(commands)
        self.status_bar.showMessage(f"准备发送 {len(commands)} 条指令…", 2000)

    # ═══════════════════════════════════════════════════════════════
    # 全局参数表格
    # ═══════════════════════════════════════════════════════════════

    def _populate_global_table(self):
        gs = self.config.get("global_settings", {})
        channels = gs.get("channels", [])
        for i in range(8):
            # 通道号
            ch_label = QTableWidgetItem(f"CH{i}")
            ch_label.setFlags(Qt.ItemIsEnabled)
            self.global_table.setItem(i, 0, ch_label)

            gch = channels[i] if i < len(channels) else {}
            fields = ["name", "max", "min", "step"]
            for j, field in enumerate(fields):
                val = gch.get(field, "")
                # 使用 QLineEdit 嵌入表格
                edit = QLineEdit(str(val) if val else "")
                edit.setFrame(False)
                edit.setStyleSheet("QLineEdit{border:none;background:transparent;padding:4px 6px;min-height:26px;}QLineEdit:focus{border:1px solid #555;background:#fff;}")
                self.global_table.setCellWidget(i, j + 1, edit)

    def _save_global_settings(self):
        gs = self.config.setdefault("global_settings", {})
        channels = gs.setdefault("channels", [])
        while len(channels) < 8:
            channels.append({"ch_id": len(channels), "name": "", "current": "", "max": "", "min": "", "step": ""})

        for i in range(8):
            ch = channels[i]
            ch["ch_id"] = i
            # 保留 current
            current = ch.get("current", "")
            for j, field in enumerate(["name", "max", "min", "step"]):
                widget = self.global_table.cellWidget(i, j + 1)
                if widget:
                    ch[field] = widget.text()
            ch["current"] = current

        self._save_config()
        self._refresh_channel_cards()
        self.status_bar.showMessage("全局参数已保存", 3000)

    # ═══════════════════════════════════════════════════════════════
    # 模式管理（后台）
    # ═══════════════════════════════════════════════════════════════

    def _refresh_mode_list(self):
        modes = self.config.get("modes", [])
        self.mode_list.setRowCount(len(modes))
        for row, m in enumerate(modes):
            self.mode_list.setItem(row, 0, QTableWidgetItem(m.get("level1", "")))
            self.mode_list.setItem(row, 1, QTableWidgetItem(m.get("level2", "")))
            self.mode_list.setItem(row, 2, QTableWidgetItem(m.get("level3", "")))
            lock_count = sum(1 for r in m.get("lock_rules", []) if r == "locked")
            self.mode_list.setItem(row, 3, QTableWidgetItem(f"锁定{lock_count} / 可调{8 - lock_count}"))

    def _on_mode_list_selection(self):
        rows = self.mode_list.selectionModel().selectedRows()
        self.btn_edit_mode.setEnabled(len(rows) > 0)
        if rows and not self._is_new_mode:
            row = rows[0].row()
            modes = self.config.get("modes", [])
            if row < len(modes):
                self._editing_mode_id = modes[row]["id"]
                self._populate_mode_editor(modes[row])

    def _new_mode(self):
        self._is_new_mode = True
        self._editing_mode_id = None
        self.mode_list.clearSelection()
        self.btn_edit_mode.setEnabled(False)
        self._show_editor()
        self._clear_editor()

    def _edit_mode(self):
        rows = self.mode_list.selectionModel().selectedRows()
        if not rows:
            return
        row = rows[0].row()
        modes = self.config.get("modes", [])
        if row >= len(modes):
            return
        self._is_new_mode = False
        self._editing_mode_id = modes[row]["id"]
        self._show_editor()
        self._populate_mode_editor(modes[row])

    def _delete_mode(self):
        rows = self.mode_list.selectionModel().selectedRows()
        if not rows:
            QMessageBox.warning(self, "提示", "请先选择要删除的模式")
            return
        row = rows[0].row()
        modes = self.config.get("modes", [])
        if row >= len(modes):
            return
        mode = modes[row]
        path = self._mode_path(mode)
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除模式「{path}」吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            del modes[row]
            self._save_config()
            self._populate_mode_combo()
            self._refresh_channel_cards()
            self._refresh_mode_list()
            self._cancel_edit()
            self.status_bar.showMessage(f"已删除模式「{path}」", 3000)

    def _show_editor(self):
        self.editor_placeholder.hide()
        self.editor_content.show()

    def _clear_editor(self):
        self.editor_widgets["l1"].setText("")
        self.editor_widgets["l2"].setText("")
        self.editor_widgets["l3"].setText("")
        self.editor_widgets["template"].setText("")
        self.editor_widgets["mcu_max"].setText("")
        self.editor_widgets["mcu_min"].setText("")
        for ch_w in self._ch_editor_widgets:
            ch_w["radio_unlocked"].setChecked(True)
            ch_w["locked_val"].setText("")
            ch_w["max"].setText("")
            ch_w["min"].setText("")
            ch_w["step"].setText("")

    def _populate_mode_editor(self, mode: dict):
        self.editor_widgets["l1"].setText(mode.get("level1", ""))
        self.editor_widgets["l2"].setText(mode.get("level2", ""))
        self.editor_widgets["l3"].setText(mode.get("level3", ""))
        self.editor_widgets["template"].setText(mode.get("command_template", "") or "")
        mcu = mode.get("mcu_limit", {}) or {}
        self.editor_widgets["mcu_max"].setText(
            str(mcu.get("max")) if mcu.get("max") not in (None, "") else ""
        )
        self.editor_widgets["mcu_min"].setText(
            str(mcu.get("min")) if mcu.get("min") not in (None, "") else ""
        )

        lock_rules = mode.get("lock_rules", ["unlocked"] * 8)
        locked_values = mode.get("locked_values", [""] * 8)
        limits = mode.get("limits", [{} for _ in range(8)])

        for i, ch_w in enumerate(self._ch_editor_widgets):
            rule = lock_rules[i] if i < len(lock_rules) else "unlocked"
            if rule == "locked":
                ch_w["radio_locked"].setChecked(True)
                ch_w["locked_val"].setText(
                    str(locked_values[i]) if i < len(locked_values) and locked_values[i] else ""
                )
            else:
                ch_w["radio_unlocked"].setChecked(True)
                lim = limits[i] if i < len(limits) else {}
                ch_w["max"].setText(str(lim.get("max")) if lim.get("max") not in (None, "") else "")
                ch_w["min"].setText(str(lim.get("min")) if lim.get("min") not in (None, "") else "")
                ch_w["step"].setText(str(lim.get("step")) if lim.get("step") not in (None, "") else "")

    def _save_mode(self):
        l1 = self.editor_widgets["l1"].text().strip()
        if not l1:
            QMessageBox.warning(self, "提示", "一级菜单名称不能为空")
            return

        l2 = self.editor_widgets["l2"].text().strip()
        l3 = self.editor_widgets["l3"].text().strip()

        lock_rules = []
        locked_values = []
        limits = []
        for ch_w in self._ch_editor_widgets:
            if ch_w["radio_locked"].isChecked():
                lock_rules.append("locked")
                locked_values.append(ch_w["locked_val"].text())
                limits.append({"max": None, "min": None, "step": None})
            else:
                lock_rules.append("unlocked")
                locked_values.append("")
                limits.append({
                    "max": self._parse_float(ch_w["max"].text()),
                    "min": self._parse_float(ch_w["min"].text()),
                    "step": self._parse_float(ch_w["step"].text()),
                })

        tpl = self.editor_widgets["template"].text().strip() or None
        mmax = self._parse_float(self.editor_widgets["mcu_max"].text())
        mmin = self._parse_float(self.editor_widgets["mcu_min"].text())

        mode_data = {
            "id": self._editing_mode_id or f"m_{uuid.uuid4().hex[:12]}",
            "level1": l1,
            "level2": l2,
            "level3": l3,
            "lock_rules": lock_rules,
            "locked_values": locked_values,
            "limits": limits,
            "command_template": tpl,
            "mcu_limit": {"max": mmax, "min": mmin},
        }

        modes = self.config.setdefault("modes", [])
        if self._is_new_mode or not self._editing_mode_id:
            modes.append(mode_data)
        else:
            for i, m in enumerate(modes):
                if m["id"] == self._editing_mode_id:
                    modes[i] = mode_data
                    break

        self._save_config()
        self._is_new_mode = False
        self._editing_mode_id = mode_data["id"]
        self._populate_mode_combo()
        self._refresh_channel_cards()
        self._refresh_mode_list()
        self.status_bar.showMessage(f"模式「{self._mode_path(mode_data)}」已保存", 3000)

    def _cancel_edit(self):
        self._is_new_mode = False
        self._editing_mode_id = None
        self.editor_content.hide()
        self.editor_placeholder.show()
        self.mode_list.clearSelection()
        self.btn_edit_mode.setEnabled(False)

    @staticmethod
    def _parse_float(val: str):
        if not val or val.strip() == "":
            return None
        try:
            return float(val)
        except ValueError:
            return None

    # ═══════════════════════════════════════════════════════════════
    # 关闭处理
    # ═══════════════════════════════════════════════════════════════

    def closeEvent(self, event):
        self._port_timer.stop()
        self._serial_worker.stop()
        event.accept()


# ═══════════════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════════════

def main():
    # 确保工作目录在程序所在文件夹，以便找到 config.json
    os.chdir(Path(__file__).parent)

    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setStyleSheet(STYLE_SHEET)

    # 设置应用字体
    font = QFont("Microsoft YaHei", 9)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
