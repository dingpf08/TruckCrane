from PyQt5.QtWidgets import QWidget,QDockWidget, QListWidget, QListWidgetItem, QApplication, QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QPushButton
import math
from DataStruDef.CalculateType import ConstructionCalculationType as CCType#计算类型
#父窗口为MainFrame.py中的class MainWindow(QMainWindow):
class CalculateDockWidget(QDockWidget):
    def __init__(self, title, parent=None):
        super(CalculateDockWidget, self).__init__(title, parent)
        self.m_dialog_data_map = {}  # 新增：存储每个对话框的数据，键为对话框的UUID，值为字典类型的数据，关闭标签且选择，
        # 这个数据在反序列化的时候，会给到CalculateDockWidget的self.m_dialog_data_map = {}  # 新增：存储每个对话框的数据，键为对话框的UUID，值为字典类型的数据，关闭标签且选择
        self.init_ui()

    def init_ui(self):
        # 使用QWidget作为停靠窗口的主内容
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)

        # 创建垂直布局
        layout = QVBoxLayout()
        self.main_widget.setLayout(layout)

        # 创建并添加QListWidget到布局
        self.dock_widget_contents = QListWidget()
        layout.addWidget(self.dock_widget_contents)

        # 设置无停靠窗口特性
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)

        # 连接双击信号到槽函数
        self.dock_widget_contents.itemDoubleClicked.connect(self.on_item_double_clicked)

        # 创建并添加按钮到布局
        button_texts = ["设计计算", "施工方案", "计算交底"]
        self.buttons = []  # 用于存储按钮，便于将来访问
        for text in button_texts:
            btn = QPushButton(text)
            self.buttons.append(btn)
            layout.addWidget(btn)
        #为按钮连接信号到槽函数（示例）
        self.buttons[0].clicked.connect(self.onDesignCalculationClicked)#设计计算
        self.buttons[1].clicked.connect(self.onConstructionSchemeClicked)#施工方案
        self.buttons[2].clicked.connect(self.onCalculationDisclosureClicked)#计算交底

    def onDesignCalculationClicked(self, item):  # 设计计算
        parent_dialog = self.parent()#MainWindow
        # 检查是否真的有父窗口
        if parent_dialog:  #
            #获取tab窗口
            Tab_dialog = parent_dialog.m_ECST#标签页
            currentdata = Tab_dialog.GetCurrentDialogData()  # 获取到了当前选择的tab对话框的数据
            conCalType = currentdata.conCalType
            if conCalType == CCType.SOIL_EMBANKMENT_CALCULATION:  # 土方边坡计算
                print("开始土方边坡计算")
                if currentdata.verification_project.project_type == "土方直立壁开挖深度计算":
                    print("土方直立壁开挖深度计算")
                    # hmax = 2×c/(K×γ×tan(45°-φ/2))-q/γ
                    # 其中，hmax - -土方最大直壁开挖高度
                    # q - -坡顶护到均布荷载
                    # γ - -坑壁土的重度(kN/m3)
                    # φ - -坑壁土的内摩擦角(°)
                    # c - -坑壁土粘聚力(kN/m2)
                    # K - -安全系数（一般用1.25 ）
                    # hmax = 2×12.0/(1.25×20.00×tan(45°-15.0°/2))-2.0/20.00=1.15m；
                    # 将角度转换为弧度
                    c = currentdata.basic_parameters.cohesion  # 坑壁土粘聚力
                    k = 1.25  # K - -安全系数（一般用1.25 ）
                    γ = currentdata.basic_parameters.unit_weight  # 坑壁土的重度
                    q = currentdata.slope_top_load.uniform_load  # 坡顶护道均布荷载
                    slope_angle_in_degrees = currentdata.basic_parameters.slope_angle
                    slope_angle_in_radians = math.radians(45 - slope_angle_in_degrees / 2)
                    Hmax = 2 * c / (k * γ * math.tan(slope_angle_in_radians)) - q / γ
                    Hmax_rounded = round(Hmax, 2)  # 保留两位小数
                    # 输出试算结果
                    print(f"1.设计计算：坑壁土方立直壁最大开挖高度为{Hmax_rounded}m。")
                    #输出计算结果到word文档
                    pass
                elif currentdata.verification_project.project_type == "基坑安全边坡计算":
                    print("基坑安全边坡计算")
                    c = currentdata.basic_parameters.cohesion  # 坑壁土粘聚力
                    θ = currentdata.basic_parameters.slope_angle  # 边坡的坡度角
                    θ_Radians = math.radians(θ)  # 边坡的坡度角弧度
                    φ = currentdata.basic_parameters.internal_friction_angle  # 坑壁土的内摩擦角φ(°)
                    φ_Radians = math.radians(φ)  # 坑壁土的内摩擦角φ(°)
                    γ = currentdata.basic_parameters.unit_weight  # 坑壁土的重度
                    θγ_Radians = (θ - φ) / 2
                    Hight = 2 * c * math.sin(θ_Radians) * math.cos(φ_Radians) / (γ * math.sin(θγ_Radians) ** 2)
                    Hight_rounded = round(Hight, 2)  # 保留两位小数
                    # 输出试算结果
                    print(f"1.设计计算：土坡允许最大高度为为{Hight_rounded}m。")
                    # 输出计算结果到word文档
                    pass

        print("设计计算结束")
    def onConstructionSchemeClicked(self, item):  # 施工方案
        print("施工方案")
    def onCalculationDisclosureClicked(self, item):#计算交底
        print("计算交底")
    def on_item_double_clicked(self, item):
        # 获取关联的UUID
        struuid = item.data(Qt.UserRole)
        mainframe=self.parent()#获取父窗口
        if mainframe:
            Table_bar=mainframe.m_ECST#获取Table_Bar
            dialog=Table_bar.get_dialog_by_uuid(struuid)#根据uuid获取对话框
            dialogname=None
            if dialog:
                dialogname=dialog.m_name
                print(f"双击的对话框名字为：{dialogname}")
            if dialogname:
                index = Table_bar.AddNewLable(dialogname, dialog, struuid)  # 给上面添加标签页

        # 双击的时候如果已经附件了对话框 就不要重复添加了

        #通过标签页对话框获取uuid对应的对话框 然后将对话框附加到标签页 self.m_dialog_uuid_map = {}  # 存储对话框的uuid和对应的对话框实例的字典


    #给根目录下添加节点
    def add_item_by_name(self, item_name,struuid):
        item = QListWidgetItem(item_name)
        # 关联UUID到列表项，使用Qt.UserRole来存储自定义数据
        item.setData(Qt.UserRole, struuid)
        self.dock_widget_contents.addItem(item)

    def refresh_project_tree(self):
        """使用self.m_dialog_data_map中的数据刷新项目树。"""
        self.dock_widget_contents.clear()  # 首先清空当前的项目树列表

        for struuid, dialog_data in self.m_dialog_data_map.items():
            # 假设dialog_data字典中有一个"name"键，我们用它来作为项目树中显示的名称
            item_name =dialog_data.caltypename
            self.add_item_by_name(item_name, struuid)
def main():
    import sys
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    calculate_dock_widget = CalculateDockWidget("测试悬浮", main_window)
    main_window.addDockWidget(Qt.LeftDockWidgetArea, calculate_dock_widget)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()