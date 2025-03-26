import sys
import os
from PyQt5.QtWidgets import QWidget, QDockWidget, QListWidget, QListWidgetItem, QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QPushButton
from WordMerge import WordDocumentMerger as WordMer#输出word文档
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
        self.m_name = "侧边停靠栏"
        self.main_widget = QWidget()
        self.setWidget(self.main_widget)

        # 创建垂直布局
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # 创建并添加QListWidget到布局
        self.dock_widget_contents = QListWidget()
        self.layout.addWidget(self.dock_widget_contents)

        # 设置无停靠窗口特性
        self.setFeatures(QDockWidget.NoDockWidgetFeatures)

        # 连接双击信号到槽函数
        self.dock_widget_contents.itemDoubleClicked.connect(self.on_item_double_clicked)

        # 创建并添加按钮到布局
        button_texts = ["设计计算", "施工方案", "计算交底"]
        self.buttons = []  # 用于存储按钮，便于将来访问
        for text in button_texts:
            btn = QPushButton(text)
            btn.setEnabled(False)
            self.buttons.append(btn)
            self.layout.addWidget(btn)
        #为按钮连接信号到槽函数（示例）
        self.buttons[0].clicked.connect(self.onDesignCalculationClicked)#设计计算
        self.buttons[1].clicked.connect(self.onConstructionSchemeClicked)#施工方案
        self.buttons[2].clicked.connect(self.onCalculationDisclosureClicked)#计算交底
    #返回按钮标题为text的按钮
    def get_button_by_text(self, text):
        """
        根据按钮文本查找按钮。
        如果找到文本匹配的按钮，则返回该按钮，否则返回None。
        """
        for btn in self.buttons:
            if btn.text() == text:
                return btn  # 返回找到的按钮
        return None  # 如果没有找到，返回None
    #禁用或者启用某个按钮
    def Set_ButtonEnable_Bytext(self, text,bool):
        for btn in self.buttons:
            if btn.text() == text:
                btn.setEnabled(bool)
    #用户选择存储文件的路径
    def select_destination_folder(self):
        # 创建一个应用程序实例
        app = QApplication([])
        # 打开文件夹选择对话框
        folder_path = QFileDialog.getExistingDirectory(None, 'Select Folder')
        # 使用 exec_() 方法堵塞进程，直到对话框关闭
        app.exec_()
        return folder_path

    def get_or_create_qapplication(self):
        """
            获取或创建一个QApplication实例。

            本函数首先尝试获取当前实例，如果不存在，则创建一个新的QApplication实例。

            参数:
            self - 对象的自引用。

            返回值:
            返回QApplication的实例。
            """
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        return app
    def choose_directory_path(self):
        app = self.get_or_create_qapplication()
        # 设置对话框的起始目录，你可以根据需要更改它
        # "" 表示当前目录，用户可以从这里开始浏览他们的文件系统
        options = QFileDialog.Options()
        # 调用 getExistingDirectory 方法打开文件夹选择对话框
        directory = QFileDialog.getExistingDirectory(None,
                                                     "选择文件夹",
                                                     "",
                                                     options=options)
        if directory:
            print(f"用户选择的文件夹路径是：{directory}")
            return directory
        else:
            print("用户没有选择文件夹路径。")
            return None
    def onDesignCalculationClicked(self, item):  # 设计计算
        try:
            parent_dialog = self.parent()#MainWindow
            # 检查是否真的有父窗口
            if parent_dialog:  #
                #获取tab窗口
                Tab_dialog = parent_dialog.m_ECST#标签页
                currentdata = Tab_dialog.GetCurrentDialogData()  # 获取到了当前选择的tab对话框的数据
                if currentdata is None:
                    print("还没有要计算的数据")
                    return
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
                        soil_type = currentdata.basic_parameters.soil_type  # 坑壁土的类型
                        γ = currentdata.basic_parameters.unit_weight  # 坑壁土的重度

                        slope_angle_in_degrees = currentdata.basic_parameters.internal_friction_angle  # 坑壁土的内摩擦角 角度
                        slope_angle_in_radians = math.radians(45 - slope_angle_in_degrees / 2)# 坑壁土的内摩擦角 弧度
                        c = currentdata.basic_parameters.cohesion  # 坑壁土粘聚力
                        q = currentdata.slope_top_load.uniform_load  # 坡顶护道均布荷载
                        k = 1.25  # K - -安全系数（一般用1.25 ）
                        Hmax = 2 * c / (k * γ * math.tan(slope_angle_in_radians)) - q / γ
                        Hmax_rounded = round(Hmax, 2)  # 保留两位小数
                        # 输出试算结果
                        #注释Ω
                        print(f"1.设计计算：坑壁土方立直壁最大开挖高度为{Hmax_rounded}m。")

                        #region 输出计算结果到word文档
                        # 调用函数并获取用户选择的文件夹路径
                        #destination_file = self.select_destination_folder()
                        destination_file = self.choose_directory_path()#这种方式可以
                        print(f"返回计算书目录：{destination_file}")
                        output_filename="土方直立壁开挖深度计算.docx"
                        content=None#正文内容
                        if destination_file is None:
                            print(f"没有选择存储路径")
                            return
                        merger = WordMer(destination_file,output_filename )
                        merger.Set_Main_Title("土方直立壁开挖深度计算")
                        #region
                        doc=merger.output_doc
                        #endregion

                        merger.Type_Main_Title()
                        content="计算依据：\n" \
                                "1、《建筑基坑支护技术规程》JGJ120 - 2012\n" \
                                "2、《建筑施工计算手册》江正荣编著\n" \
                                "3、《实用土木工程手册》第三版杨文渊编著\n" \
                                "4、《施工现场设施安全设计计算手册》谢建民编著\n" \
                                "5、《地基与基础》第三版"
                        merger.Set_Doc_Content(content)
                        merger.Type_Doc_Content()
                        content=f"本工程，基坑土质为{soil_type}，且地下水位低于基坑底面标高，挖方边坡可以做成直立壁不加支撑。最大允许直壁高度按以下方法计算。"
                        merger.Set_Doc_Content(content)
                        merger.Type_Doc_Content()

                        merger.Set_First_Title("一、参数信息")
                        merger.Type_First_Title()
                        table_data = [
                            ["坑壁土类型", soil_type, "坑壁土的重度γ(kN/m³)", γ],
                            ["坑壁土的内摩擦角φ(°)", slope_angle_in_degrees, "坑壁土粘聚力c(kN/m²)", c],
                            ["坑顶护道上均布荷载q(kN/m²)", q, "", ""]
                        ]
                        merge_info = [(3, 3, 3, 4)]#合并第三行的第三列和第四列
                        # 合并信息，每个元组代表一个合并的范围 (开始行, 开始列, 结束行, 结束列)
                        merger.insert_table(table_data,merge_info)

                        merger.Set_First_Title("二、土方直立壁开挖高度计算:")
                        merger.Type_First_Title()

                        content="土方最大直壁开挖高度按以下公式计算 ：" \
                                "\nhmax = 2×c / (K×γ×tan(45°-φ / 2))-q / γ\
                                \n其中，hmax - -土方最大直壁开挖高度\
                                \nq—坡顶护道均布荷载\
                                \nγ - -坑壁土的重度(kN/m3)\
                                \nφ - -坑壁土的内摩擦角(°)\
                                \nc - -坑壁土粘聚力(kN / m2)\
                                \nK - -安全系数（一般用1.25 ）"
                        merger.Set_Doc_Content(content)
                        merger.Type_Doc_Content()

                        # 添加公式
                        formula_text = f"Hmax = (2*{c})/({k}*{γ}*tan(45° - {slope_angle_in_degrees}^°)-{q}/{γ}={Hmax:.2f}m"
                        # 将根号符号替换为带有上方一横的Unicode字符

                        #merger.insert_formula(formula_text)
                        merger.insert_formula(c,k,γ, slope_angle_in_degrees, q, Hmax)
                        #content = (
                        #    f"Hmax = 2 * {c} / ({k} * {γ} * tan(45° - {slope_angle_in_degrees}° / 2)) - {q} / {γ}"
                        #   f" = {Hmax:.2f}m"#结果 Hmax 被四舍五入到小数点后两位，并添加了单位（米）
                        # )
                        #merger.Set_Doc_Content(content)
                        #merger.Type_Doc_Content()
                        content = f"\n本工程的基坑土方立直壁最大开挖高度为{Hmax:.2f}m。"
                        merger.Set_Doc_Content(content)
                        merger.Type_Doc_Content()
                        # 获取当前工作目录
                        current_dir = os.path.dirname(os.path.abspath(__file__))
                        # 构建相对于当前文件的图片路径
                        image_path = os.path.join(current_dir, "..", "DrawGraphinsScene", "slope - word.png")
                        
                        # 检查图片是否存在
                        if os.path.exists(image_path):
                            try:
                                merger.insert_image(image_path)
                            except Exception as e:
                                print(f"插入图片时出错: {str(e)}")
                        else:
                            print(f"警告：找不到图片文件: {image_path}")
                            
                        # endregion 输出计算结果到word文档
                        pass
                    elif currentdata.verification_project.project_type == "基坑安全边坡计算":
                        print("基坑安全边坡计算")
                        soil_type = currentdata.basic_parameters.soil_type  # 坑壁土的类型
                        γ = currentdata.basic_parameters.unit_weight  # 坑壁土的重度

                        φ = currentdata.basic_parameters.internal_friction_angle  # 坑壁土的内摩擦角φ(°)
                        φ_Radians = math.radians(φ)  # 坑壁土的内摩擦角φ(°)

                        c = currentdata.basic_parameters.cohesion  # 坑壁土粘聚力

                        θ = currentdata.basic_parameters.slope_angle  # 边坡的坡度角
                        θ_Radians = math.radians(θ)  # 边坡的坡度角弧度
                        #v：土的重度（kN/m³）：【0.1，40】包括0，包括40
                        # Φ：坑壁土的内摩擦角φ(°)：【0，90）包括0，不包括90
                        # c：土粘聚力(kN/㎡)：【0，50】包括0，包括50
                        # Θ：边坡的坡度角(°)：（0，90】不包括0，包括90

                        #1、如果  θ=φ=45°，边坡高度不受限制。
                        #2、如果  θ>φ=45°，c≠0
                        # 为陡坡 h=2csinθcosφ/(γsin2((θ-φ)/2))=2×10×sin46×cos45/(20×sin2((46-45)/2))=6679.368m。土坡允许最大高度为6679.368m。
                        #3、θ  > φ = 45°，c = 0 挖方边坡任何高度都不稳定。
                        #4、θ=44°<φ=45°，c≠0或者c=0，为缓坡。
                        # h=2csinθcosφ/(γsin2((θ-φ)/2))=2×1×sin44×cos45/(20×sin2((44-45)/2))=645.019m。土坡允许最大高度为645.019m。


                        # region 输出计算结果到word文档
                        # 调用函数并获取用户选择的文件夹路径
                        # destination_file = self.select_destination_folder()
                        destination_file = self.choose_directory_path()  # 这种方式可以
                        output_filename = "基坑安全边坡计算.docx"
                        content = None  # 正文内容
                        if destination_file is None:
                            print(f"没有选择存储路径")
                            return
                        merger = WordMer(destination_file, output_filename)
                        merger.Set_Main_Title("基坑安全边坡计算")
                        merger.Type_Main_Title()
                        content = "计算依据：\n" \
                                  "1、《建筑基坑支护技术规程》JGJ120 - 2012\n" \
                                  "2、《建筑施工计算手册》江正荣编著\n" \
                                  "3、《实用土木工程手册》第三版杨文渊编著\n" \
                                  "4、《施工现场设施安全设计计算手册》谢建民编著\n" \
                                  "5、《地基与基础》第三版"
                        merger.Set_Doc_Content(content)
                        merger.Type_Doc_Content()
                        content = f"本工程基坑壁需进行放坡，以保证边坡稳定和施工操作安全。基坑挖方安全边坡按以下方法计算。"
                        merger.Set_Doc_Content(content)
                        merger.Type_Doc_Content()

                        merger.Set_First_Title("一、参数信息")
                        merger.Type_First_Title()
                        table_data = [
                            ["坑壁土类型", soil_type, "坑壁土的重度γ(kN/m³)", γ],
                            ["坑壁土的内摩擦角φ(°)", φ, "坑壁土粘聚力c(kN/m²)", c],
                            ["边坡的坡度角θ(°)", θ, "", ""]
                        ]
                        merge_info = [(3, 3, 3, 4)]  # 合并第三行的第三列和第四列，word合并初始从1开始合并
                        # 合并信息，每个元组代表一个合并的范围 (开始行, 开始列, 结束行, 结束列)
                        merger.insert_table(table_data, merge_info)
                        merger.Set_First_Title("二、挖方安全边坡计算:")
                        merger.Type_First_Title()
                        content = ("暂定，根据计算结果确定")
                        if abs(θ-φ)==0:
                            content =f"θ=φ={θ}°，边坡高度不受限制。"
                        elif (θ-φ>0) and(c != 0):
                            Hight = 2 * c * math.sin(θ_Radians) * math.cos(φ_Radians) / (
                                    γ * math.sin((θ_Radians - φ_Radians) / 2) ** 2)
                            Hight_rounded = round(Hight, 3)  # 保留两位小数
                            content =f"θ={θ}>φ={φ}，c≠0为陡坡。\n" \
                                     f"h=2csinθcosφ/(γsin²((θ-φ)/2))=2x{c}xsin{θ}xcos{φ}/({γ}xsin²(({θ}-{φ})/2)={Hight_rounded}\n" \
                                     f"土坡允许最大高度为{Hight_rounded}m\n"

                        elif (θ-φ>0) and(c == 0):
                            content = f"θ={θ}>φ={φ}，c=0。\n" \
                                      "挖方边坡任何高度都不稳定\n"
                        elif (θ-φ<0):
                            Hight = 2 * c * math.sin(θ_Radians) * math.cos(φ_Radians) / \
                                    (γ * math.sin((θ_Radians - φ_Radians) / 2) ** 2)
                            Hight_rounded = round(Hight, 3)  # 保留两位小数
                            content = f"θ={θ}<φ={φ}，为缓坡。\n" \
                                      f"h=2csinθcosφ/(γsin²((θ-φ)/2))=2x{c}xsin{θ}xcos{φ}/({γ}xsin²(({θ}-{φ})/2)={Hight_rounded}\n"\
                                      f"土坡允许最大高度为{Hight_rounded}m\n"

                        merger.Set_Doc_Content(content)
                        merger.Type_Doc_Content()
                        # 获取当前工作目录
                        current_dir = os.path.dirname(os.path.abspath(__file__))
                        # 构建相对于当前文件的图片路径
                        image_path = os.path.join(current_dir, "..", "DrawGraphinsScene", "slope_2 - word.png")
                        
                        # 检查图片是否存在
                        if os.path.exists(image_path):
                            try:
                                merger.insert_image(image_path)
                            except Exception as e:
                                print(f"插入图片时出错: {str(e)}")
                        else:
                            print(f"警告：找不到图片文件: {image_path}")
                            
                        # endregion 输出计算结果到word文档
                        pass

            print("设计计算结束")
        except Exception as e:
            print(f"计算过程中出错: {str(e)}")
            import traceback
            traceback.print_exc()
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