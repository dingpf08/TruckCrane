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
        """
        更新对话框数据和实例
        Args:
            prodata: 项目数据字典，包含所有对话框的数据
        """
        print(f"开始更新对话框数据，数据内容：{prodata}")
        try:
            self.m_dialog_data_map = prodata  # 更新标签页对话框的数据
            
            # 清理现有的对话框实例
            for dialog in self.m_dialog_uuid_map.values():
                if hasattr(dialog, 'close'):
                    dialog.close()
            self.m_dialog_uuid_map.clear()
            
            # 根据数据重新创建对话框实例
            for uuid, dialog_data in self.m_dialog_data_map.items():
                if hasattr(dialog_data, 'conCalType'):
                    print(f"处理UUID为{uuid}的对话框数据，类型为：{dialog_data.conCalType}")
                    
                    if dialog_data.conCalType == Conct.SOIL_EMBANKMENT_CALCULATION:
                        # 土方边坡计算
                        dialog_instance = EarthSlopeDialog(uuid, dialog_data)
                    elif dialog_data.conCalType == Conct.HYDRAULIC_CRANE_CALCULATION:
                        # 液压起重机计算
                        from Hoisting_Engineering.HydraulicCraneDialog import HydraulicCraneDialog
                        dialog_instance = HydraulicCraneDialog(uuid, dialog_data)
                    # 在这里添加其他类型的对话框处理...
                    else:
                        print(f"未知的对话框类型：{dialog_data.conCalType}")
                        continue
                    
                    # 存储新创建的对话框实例
                    self.m_dialog_uuid_map[uuid] = dialog_instance
                    print(f"成功创建并存储对话框实例，UUID：{uuid}")
                else:
                    print(f"对话框数据缺少conCalType属性：{dialog_data}")
                    
        except Exception as e:
            print(f"更新对话框数据时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            
        print("完成对话框数据更新")

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

        elif action==close_otheraction:#关闭其他
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
        """
        移除指定索引和UUID的标签页，但保留对话框实例
        Args:
            index: 标签页索引
            tab_uuid: 标签页UUID
        """
        print(f"移除tab页面，索引：{index}，UUID：{tab_uuid}")
        # 使用这个UUID作为键来从字典中获取对应的对话框对象
        dialog = self.m_dialog_uuid_map.get(tab_uuid, None)
        # 检查是否找到了对话框
        if dialog is not None:  # 对话框存在
            try:
                # 检查对话框是否有保存状态属性
                if hasattr(dialog, 'IsSave'):
                    issave = dialog.IsSave  # 是否保存
                    if not issave:  # 对话框数据没有保存，提示是否保存
                        retval = self.ShowMessageBox("操作提示", "保存当前所有更改的设置吗？",
                                                   QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
                        # 判断用户点击了哪个按钮，并进行相应处理
                        if retval == QMessageBox.Yes:
                            # 保存对话框的当前数据
                            if hasattr(dialog, 'updateCalculationData'):
                                dialog_data = dialog.updateCalculationData()
                                if dialog_data:
                                    self.m_dialog_data_map[tab_uuid] = dialog_data
                            
                            self.uuid_set.discard(tab_uuid)  # 从显示集合中移除UUID
                            self.removeTab(index)  # 移除标签页
                            dialog.hide()  # 隐藏对话框而不是关闭
                            print("用户选择了'是'，对话框数据已保存")
                            
                        elif retval == QMessageBox.No:
                            self.uuid_set.discard(tab_uuid)  # 从显示集合中移除UUID
                            self.removeTab(index)  # 移除标签页
                            dialog.hide()  # 隐藏对话框而不是关闭
                            print("用户选择了'否'，对话框已隐藏")
                            
                        elif retval == QMessageBox.Cancel:
                            print("用户选择了'取消'")
                            return
                    else:  # 已保存
                        if hasattr(dialog, 'updateCalculationData'):
                            dialog_data = dialog.updateCalculationData()
                            if dialog_data:
                                self.m_dialog_data_map[tab_uuid] = dialog_data
                        
                        self.uuid_set.discard(tab_uuid)  # 从显示集合中移除UUID
                        self.removeTab(index)  # 移除标签页
                        dialog.hide()  # 隐藏对话框而不是关闭
                else:
                    # 对话框没有保存状态属性，直接隐藏
                    self.uuid_set.discard(tab_uuid)  # 从显示集合中移除UUID
                    self.removeTab(index)  # 移除标签页
                    dialog.hide()  # 隐藏对话框而不是关闭
                
                # 保持对话框实例在映射中，不再移除
                print(f"对话框实例已保存在映射中，UUID：{tab_uuid}")
                
            except Exception as e:
                print(f"移除标签页时发生错误: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print(f"找不到UUID为{tab_uuid}的对话框")
    #根据uuid找到对应的索引
    def findTabIndexByUuid(self, struuid):
        for index in range(self.count()):
            tab = self.widget(index)
            if tab.property("uuid") == struuid:
                return index
        return -1  # 如果没有找到匹配的uuid，返回-1表示不存在
    # region 添加新的标签页
        #strName为标签的名字，dialog为QWidget对话框，如何对话框存在，则切换对话框，如果对话框不存在，则新添一个对话框
    def AddNewLable(self,strName,dialog,struuid=None):
        """
        添加新的标签页或切换到已存在的标签页
        Args:
            strName: 标签页名称
            dialog: 对话框实例
            struuid: 对话框的UUID
        Returns:
            新添加的标签页索引或已存在标签页的索引
        """
        print(f"开始AddNewLable，对话框名字为{strName}，对话框uuid为：{struuid}")
        
        if not isinstance(dialog, QWidget):
            print(f"错误：对话框必须是QWidget类型，当前类型为：{type(dialog)}")
            return -1
            
        try:
            # 检查是否已有此对话框实例
            existing_dialog = self.m_dialog_uuid_map.get(struuid)
            if existing_dialog:
                print(f"找到已存在的对话框实例，UUID：{struuid}")
                dialog = existing_dialog  # 使用已存在的实例
            
            if struuid in self.uuid_set:  # 显示的对话框中有这个元素
                print(f"Table已经添加了ID为：{struuid}，名字为{strName}的对话框")
                # 查找已存在的标签页
                index = self.findTabIndexByUuid(struuid)
                if index != -1:
                    print(f"找到已存在的标签页，索引为：{index}")
                    if not dialog.isVisible():
                        dialog.show()
                    self.m_index = index
                    self.setCurrentIndex(index)  # 显示当前的标签页
                    return index
                    
            # 创建新的标签页
            print(f"创建新标签页，ID为：{struuid}，名字为：{strName}")
            tab = QWidget()  # 定义一个标签
            tab.setProperty("uuid", struuid)  # 给标签设置uuid属性
            
            # 确保对话框可见
            if not dialog.isVisible():
                dialog.show()
            
            tab_layout = QVBoxLayout()  # 定义一个竖直的布局
            tab_layout.addWidget(dialog)  # 竖向布局添加对应的对话框
            tab.setLayout(tab_layout)  # 标签添加对应的布局
            
            # 添加新标签页
            index = self.addTab(tab, strName)
            if index >= 0:
                print(f"成功添加新标签页，ID为：{index}")
                self.uuid_set.add(struuid)  # 给标签页添加对应的str_uuid
                self.m_dialog_uuid_map[struuid] = dialog  # 存储uuid和对应的对话框实例
                self.m_index = index
                self.setCurrentIndex(index)  # 显示当前的标签页
                return index
            else:
                print("错误：添加标签页失败")
                return -1
                
        except Exception as e:
            print(f"添加标签页时发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return -1
            
        finally:
            print(f"结束AddNewLable，对话框类型为：{type(dialog)}，对话框uuid为：{struuid}")
            
    def removeTab(self, index):
        """
        重写removeTab方法，隐藏对话框而不是销毁它
        """
        tab = self.widget(index)
        if tab:
            uuid = tab.property("uuid")
            if uuid:
                # 从显示集合中移除UUID
                self.uuid_set.discard(uuid)
                # 获取对话框实例并隐藏它
                dialog = self.m_dialog_uuid_map.get(uuid)
                if dialog:
                    dialog.hide()  # 隐藏对话框而不是关闭
                # 保持对话框实例在映射中，不再移除
        super().removeTab(index)
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

    def find_tab_by_uuid(self, target_uuid):
        """
        根据UUID查找对应的标签页索引
        Args:
            target_uuid: 要查找的UUID
        Returns:
            找到的标签页索引，如果没找到返回-1
        """
        for i in range(self.count()):
            widget = self.widget(i)
            if widget and widget.property("uuid") == target_uuid:
                return i
        return -1

def main():
    import sys
    app = QApplication(sys.argv)
    mainWindow = ECSTabWidget()
    mainWindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()