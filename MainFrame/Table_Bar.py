#标签页，管理地基、吊装、等等对话框
import pickle
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QLabel, QTextEdit, QListWidget, QMenu, QApplication, \
    QMessageBox, QMainWindow
from PyQt5.QtCore import QEvent
from PyQt5.QtGui import QMouseEvent
#父窗口是class MainWindow(QMainWindow)
from Foundation_Engineering.EarthSlopeDialog import EarthSlopeDialog#边坡计算对话框
from Tab1_SelectMajorInterface import  EngineerFuctionSelPage as EFSP
from DataStruDef.CalculateType import ConstructionCalculationType as Conct#对话框类型

#序列化文件的后缀为ZtzpCCS
#这里还会存储新建的计算工程对话框实例和对应的uuid，和左侧项目树共用同一个uuid
#每个标签页都添加一个uuid，tab.setProperty("uuid", struuid)
class ECSTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super(ECSTabWidget, self).__init__(parent)
        self.m_Name="标签页管理对话框"
        self.m_dialog_uuid_map = {}  # 存储对话框的uuid和对应的对话框对象实例,都放到内存里面，从项目树移除的时候，也从数据结构里面移除
        self.uuid_set = set()#标签页上的对话框对应的uuid,不可以放入重复的元素，从标签页移除的时候，也从数据结构移除
        self.m_dialog_data_map = {}  # 新增：存储每个对话框的uuid和对应的对话框数据，键为对话框的UUID，值为字典类型的数据，关闭标签且选择保存的时候，将对话框数据存储到这个变量
        self.m_index=None#当前的标签页
        self.m_CurrentData=None#当前标签页对应的数据
        # 连接标签页切换的信号到自定义的槽函数
        self.currentChanged.connect(self.onTabChanged)#切换标签页
        self.init_ui()
        #获取当前标签页的
    def GetCurrentDialogData(self):
        print(f"开始：GetCurrentDialogData")
        self.m_CurrentData=self.CurrentDialogData(self.m_index)
        print(f"结束：GetCurrentDialogData")
        return self.m_CurrentData
    #切换标签页
    def CurrentDialogData(self,index):
        # 处理标签页变化的逻辑
        print(f"切换到了标签页: {index}")
        # 获取当前激活的标签页的UUID
        current_tab = self.widget(index)  # 获取当前选中的标签页对应的widget
        if current_tab:  # 检查是否获取到了标签页
            print(f"当前标签页有效")
            uuid = current_tab.property("uuid")  # 获取这个标签页对应的UUID
            print(f"当前标签页的UUID为：{str(uuid)}")
            if uuid:  # 数据保存了，且存储在self.m_dialog_data_map
                print(f"uuid有效")
                dialog_instance = self.m_dialog_uuid_map.get(uuid)  # 对话框实例
                print(f"dialog_instance有效")
                if dialog_instance is None:
                    print(f"找不到UUID为 {uuid} 的对话框实例。")
                    return
                print(f"开始获取dialog_data")
                dialog_data = dialog_instance.updateCalculationData()  # ABC(这个函数需要抽象出来)这个#==#函数需要每个对话框类都一样
                print(f"结束获取dialog_data")
                if dialog_data:
                    print(f"开始设置对话框数据 {dialog_data} ")
                    self.m_CurrentData=dialog_data#不同的对话框这个类型是不一样的
                    print(f"结束设置对话框数据 {dialog_data} ")
                    return dialog_data
            else:  # 数据还没有存储，没关系 从对话框钟直接获取
                dialog_instance = self.m_dialog_uuid_map.get(uuid)  # 对话框实例
                if dialog_instance is None:
                    print(f"找不到UUID为 {uuid} 的对话框实例。")
                    return
                # 假设对话框实例有一个方法updateCalculationData()来获取当前数据
                dialog_data = dialog_instance.updateCalculationData()  # ABC(这个函数需要抽象出来)这个#==#函数需要每个对话框类都一样
                if dialog_data is None:
                    print(f"对话框实例UUID为 {uuid} 无法提供当前数据。")
                    return
                else:#获取到数据
                    return dialog_data
                    print(f"从对话框实例UUID为 {uuid} 成功获取数据。")

                print(f"标签页 {index} 没有设置UUID。")
        else:
            print(f"没有找到标签页 {index} 对应的widget。")

    def onTabChanged(self, index):
        print(f"开始onTabChanged切换标签页，其索引值为{index}")
        self.m_index=index#设置当前标签页
        print(f"开始CurrentDialogData")
        self.m_CurrentData=self.CurrentDialogData(index)
        print(f"结束CurrentDialogData")
        print(f"输出self.m_CurrentData：{self.m_CurrentData}")
        self.handleCurrentData()

    def handleCurrentData(self):
        print(f"开始handleCurrentData")
        try:
            if self.m_CurrentData is None:
                print("m_CurrentData is None")
                # Design calculation button can be disabled
                parentDialog = self.parent()
                if parentDialog:
                    print(f"Parent dialog exists: {type(parentDialog)}")
                    # Ensure the parent is the expected type, e.g., MainWindow
                    if isinstance(parentDialog, QMainWindow):
                        caldock = parentDialog.m_CalDock
                        if caldock:
                            caldock.Set_ButtonEnable_Bytext("设计计算", False)
            elif hasattr(self.m_CurrentData, 'conCalType'):
                print(f"Current data type: {self.m_CurrentData.conCalType}")
                if self.m_CurrentData.conCalType == Conct.SOIL_EMBANKMENT_CALCULATION:
                    print("Foundation calculation data type")
                    # Design calculation button can be enabled
                    parentDialog = self.parent()
                    if parentDialog:
                        # Ensure the parent is the expected type, e.g., MainWindow
                        if isinstance(parentDialog, QMainWindow):
                            caldock = parentDialog.m_CalDock
                            if caldock:
                                caldock.Set_ButtonEnable_Bytext("设计计算", True)
                else:
                    print(f"Other calculation type: {self.m_CurrentData.conCalType}")
            else:
                print("m_CurrentData does not have conCalType attribute")
        except Exception as e:
            print(f"Error in handleCurrentData: {str(e)}")
            import traceback
            traceback.print_exc()

    def serialize_dialog_data_map(self, file_name):
        """将对话框数据字典序列化到指定的文件中。"""
        try:
            # 序列化数据到指定的文件
            with open(file_name, 'wb') as file:
                pickle.dump(self.m_dialog_data_map, file)
            print(f"数据已成功保存到{file_name}")
        except Exception as e:
            print(f"保存数据时发生错误: {e}")

    def setCurrentIndex(self, index):
        super(ECSTabWidget, self).setCurrentIndex(index)
        # 更新所有标签的样式
        self.updateTabStyles()

    def UpdataDialogData(self, prodata):
        self.m_dialog_data_map = prodata  # 标签页对话框的数据更新
        #更新uuid和对应的对话框实体
        for uuid, dialog_data in self.m_dialog_data_map.items():
            if dialog_data.conCalType == Conct.SOIL_EMBANKMENT_CALCULATION:#土方边坡计算
                dialog_instance = EarthSlopeDialog(uuid,dialog_data)
                self.m_dialog_uuid_map[uuid] = dialog_instance


    def updateTabStyles(self):
        for i in range(self.count()):
            if i == self.currentIndex():
                # 将当前选中的标签颜色设置为浅蓝色
                self.tabBar().setTabTextColor(i, Qt.blue)  # 设置文字颜色为蓝色
                self.tabBar().setStyleSheet(f"QTabBar::tab:selected {{background-color: lightblue;}}")  # 设置选中的标签背景色为浅蓝色
            else:
                # 其他标签使用默认颜色
                self.tabBar().setTabTextColor(i, Qt.black)  # 设置未选中的标签文字颜色为黑色
                # 如果需要，也可以为未选中的标签设置特定的背景色
    #根据uuid获取内存中的对话框
    def get_dialog_by_uuid(self, uuid):
        """
        根据提供的UUID，从字典中找到并返回对应的对话框实例。
        如果找不到，返回None。
        """
        dialog = self.m_dialog_uuid_map.get(uuid)
        if dialog:
            return dialog
        else:
            print(f"找不到UUID为 {uuid} 的对话框。")
            return None
    #region 初始化函数
    def init_ui(self):
        # 标签1
        efsp=EFSP(self)#模块选择对话框
        struuid=str(efsp.uuid)#模块的uuid
        self.AddNewLable("模块选择",efsp,struuid )#添加第一个标签页
        #self.setStyleSheet("background-color: lightblue;")#标签页的背景颜色
    # endregion 初始化函数

    #region 鼠标按下操作
    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:#鼠标右键
            index = self.tabBar().tabAt(event.pos())
            if index >= 0:
                self.showContextMenu(event.globalPos(), index)
        super(ECSTabWidget, self).mousePressEvent(event)
    # endregion 鼠标按下操作

    # region 弹出右键菜单
    def showContextMenu(self, position, index):
        menu = QMenu()
        close_action = menu.addAction("关闭")
        close_otheraction=menu.addAction("关闭其它")
        tab_uuid =self.widget(index).property("uuid")
        if index==0:#模块选择,不能关闭模块选择
            close_action.setEnabled(False)

        action = menu.exec_(position)
        if action == close_action:#关闭标签页
            self.removeTabByIndexAnduuid(index,tab_uuid)

        elif action==close_otheraction:#
            self.remove_other_tabs()
    #endregion 弹出右键菜单
    #移除table节点和节点与uuid的对应关系
    #弹出提示框
    def ShowMessageBox(self,title,text,buttons, default_button):
        """
            显示一个自定义的消息框。
            参数:
            title -- 对话框的标题。
            text -- 对话框显示的文本。
            buttons -- 要在对话框中显示的按钮（QMessageBox标准按钮）。
            default_button -- 对话框的默认按钮（QMessageBox标准按钮）。

            返回:
            用户点击的按钮。
            """
        msgBox = QMessageBox()
        msgBox.setWindowTitle(title)  # 设置窗口标题
        msgBox.setIcon(QMessageBox.Information)  # 设置对话框图标为信息图标
        msgBox.setText(text)  # 设置对话框的提示文本
        msgBox.setStandardButtons(buttons)  # 设置按钮
        msgBox.setDefaultButton(default_button)  # 设置默认按钮

        # 显示消息框并等待用户响应
        retval = msgBox.exec_()

        # 返回用户点击的按钮
        return retval
    def removeTabByIndexAnduuid(self,index,tab_uuid):
        print("移除tab页面")
        # 使用这个UUID作为键来从字典中获取对应的对话框对象
        dialog = self.m_dialog_uuid_map.get(tab_uuid, None)
        # 检查是否找到了对话框
        if dialog is not None:#对话框存在
            if isinstance(dialog, EarthSlopeDialog):
                issave=dialog.IsSave#是否保存
                if not issave:#对话框数据没有保存，提示是否保存
                    retval =self.ShowMessageBox("操作提示","保存当前所有更改的设置吗？",
                                                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,QMessageBox.Yes)
                    # 判断用户点击了哪个按钮，并进行相应处理
                    if retval == QMessageBox.Yes:
                        # 保存对话框的当前数据，更新数据库
                        #1、获取对话框的数据
                        slopedata=dialog.updateCalculationData()#获取对话框的数据
                        #2、将uuid和对话框的数据存储到self.m_dialog_data_map = {}
                        self.m_dialog_data_map[tab_uuid] = slopedata#如果没有就添加，如果存在旧的 则用新的覆盖
                        self.uuid_set.discard(tab_uuid)  # 移除标签页中显示的uuid
                        self.removeTab(index)#移除标签页
                        dialog.IsSave=True#对话框是否已经保存为True
                        #更新数据库的数据
                        print("用户选择了'是'")
                        #重新序列化话数据
                    elif retval == QMessageBox.No:
                        self.uuid_set.discard(tab_uuid)  # 移除标签页中显示的uuid
                        self.removeTab(index)
                        #不保存对话框的当前数据，不更新数据库
                        dialog.IsSave = True
                        #不更新数据库的数据
                        print("用户选择了'否'")
                    elif retval == QMessageBox.Cancel:
                        #返回对话框
                        print("用户选择了'取消'")
                elif issave :#保存了
                    self.uuid_set.discard(tab_uuid)  # 移除标签页中显示的uuid
                    # 1、获取对话框的数据
                    slopedata = dialog.updateCalculationData()  # 获取对话框的数据
                    # 2、将uuid和对话框的数据存储到self.m_dialog_data_map = {}
                    self.m_dialog_data_map[tab_uuid] = slopedata  # 如果没有就添加，如果存在旧的 则用新的覆盖
                    self.removeTab(index)
            # 对话框被找到，可以进行进一步的操作
    #根据uuid找到对应的索引
    def findTabIndexByUuid(self, struuid):
        for index in range(self.count()):
            tab = self.widget(index)
            if tab.property("uuid") == struuid:
                return index
        return -1  # 如果没有找到匹配的uuid，返回-1表示不存在
    # region 添加新的标签页
        #strName为标签的名字，dialog为QWidget对话框，如何对话框存在，则切换对话框，如果对话框不存在，则新添一个对话框
    def AddNewLable(self,strName,dialog,struuid=None):#默认添加的是QWidget
        #移除标签页中的对话框，从self.uuid_list中移除对应的uuid
        #双击左侧项目树的节点：获取uuid，如果self.uuid_list中有对应的uuid，找到uuid对应的标签索引，显示这个索引
        #如果如果self.uuid_list没有对应的uuid，添加对应的标签页和对话框，对话框从self.m_dialog_uuid_map.get(struuid)获取
        print(f"开始AddNewLable，对话框名字为{strName}，对话框uuid为：{struuid}")
        if isinstance(dialog, QWidget):
            if struuid in self.uuid_set:#显示的对话框中有这个元素
                print(f"Table已经添加了ID为：{struuid}，名字为{strName}的对话框")
                # 根据uuid查找对应的对话框
                dialog = self.m_dialog_uuid_map.get(struuid)
                if dialog is not None:
                    index=self.findTabIndexByUuid(struuid)
                    if index is not -1:
                        self.m_index=index
                        self.setCurrentIndex(index)  # 显示当前的标签页
                else:
                    return
                #让tab页面切换到对应的对话框
            else:#显示的页面没有这个对话框
                print(f"Table未添加ID为：{struuid}，名字为：{strName}的对话框")
                tab = QWidget()#定义一个标签
                tab.setProperty("uuid", struuid)#给标签设置uuid属性
                tab_layout = QVBoxLayout()#定义一个竖直的布局
                tab_label = dialog#定义附件的控件或者对话框的类型
                tab_layout.addWidget(tab_label)#竖向布局添加对应的对话框
                tab.setLayout(tab_layout)#变迁添加对应的布局
                index=self.addTab(tab, strName)#将标签添加到
                print(f"标签页的ID为：{index}")
                self.uuid_set.add(struuid)#给标签页添加对应的str_uuid
                print(f"uuid_set添加了struuid：{struuid}")
                self.m_dialog_uuid_map[struuid] = dialog  # 存储uuid和对应的对话框实例
                print(f"m_dialog_uuid_map添加了dialog：{struuid}")
                if index:
                    print(f"新添加的标签页ID为：{index}")
                    self.m_index=index
                    print(f"开始：设置{index}为当前的ID")
                    self.setCurrentIndex(index)  # 显示当前的标签页
                    print(f"结束：设置{index}为当前的ID")
        print(f"结束AddNewLable，对话框类型为：{type(dialog)}，对话框uuid为：{struuid}")
    # endregion 添加新的标签页

    # region 根据索引移除标签页
    #移除特定标签页，根据索引来移除，index是要移除的标签的索引。标签页的索引从开始计数。
    def removeTabByIndex(self, index):

        self.removeTab(index)
    # endregion
    #移除其它的标签页
    def remove_other_tabs(self):
        count = self.count()
        for i in range(count - 1, -1, -1):
            if i != 0:
                self.removeTab(i)
    #region 根据名字移除标签页
    def removeTabByName(self, tabName):
        for index in range(self.count()):
            if self.tabText(index) == tabName:
                self.removeTab(index)
                break
    # endregion

def main():
    import sys
    app = QApplication(sys.argv)
    mainWindow = ECSTabWidget()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()