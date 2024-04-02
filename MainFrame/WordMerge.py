import os
import sys
import win32com.client as win32


# 合并多个word文档，应用模板里面的设置
class WordDocumentMerger:

    def __init__(self, root_directory, output_filename):#root_directory：文件夹路径 output_filename：输出的文件名
        self.root_directory = root_directory
        # self.output_filename = root_directory+"\\"+ output_filename
        self.output_filename = os.path.join(root_directory, output_filename)
        self.word = win32.gencache.EnsureDispatch('Word.Application')
        self.word.Visible = True
        self.template_path = None

        current_working_directory = os.getcwd()  # D:\Cache\ztzp-ttms\MainFrame
        # QMessageBox.information(None, '未打包之前word文档所在的根目录为：', current_working_directory)
        print(f"未打包之前的根目录为：{current_working_directory}")  # D:\Cache\ztzp-ttms\MainFrame
        self.template_path = "D:\Cache\ztzp-ConCaSys\WordTemplate\样式1.dotx"  # Word 模板的路径

        # 设置 Word 不显示警告
        self.word.DisplayAlerts = False
        # 如果输出文件已存在，则删除其中的内容，重新填入内容
        print(f"WordMerge:输出文件的全路径为：{output_filename}")
        if os.path.exists(self.output_filename):
            self.output_doc = self.word.Documents.Open(self.output_filename)
            # 清空文档内容
            self.output_doc.Content.Select()
            self.word.Selection.Delete()
            print("已存在的文档内容已清除。")
        else:
            print(f"WordMerge:文件不存在，从模板重新创建一个文档")
            # 如果文件不存在，创建一个新文档
            print(f"WordDocumentMerger：合并word文档的时候，模板文件的全路径为：{self.template_path}！！！end")
            self.output_doc = self.word.Documents.Add(Template=self.template_path)
            print(f"WordDocumentMerger 添加了一个文档：合并word文档的时候，模板文件的全路径为，：{self.template_path}！！！end")
            self.output_doc.SaveAs2(self.output_filename, FileFormat=win32.constants.wdFormatDocumentDefault)

        self.Main_Title = None  # 标题  文档标题为一级标题
        self.First_Title = None  # 二级标题
        self.Second_Title = None  # 三级标题
        self.Third_Title = None  # 四级标题
        self.Fourth_Title = None  # 五级标题
        self.Doc_Content= None #正文内容
        # 目前暂时用不到
        self.Fifth_Title = None  # 六级标题
        self.Sixth_Title = None  # 七级标题
        print(self.output_filename)

    def find_docx_files(self, directory):
        docx_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".docx"):
                    docx_files.append(os.path.join(root, file))
        return docx_files

    def Set_Main_Title(self, title):
        self.Main_Title = title

    def Type_Main_Title(self):
        self.word.Selection.EndKey(6)  # 6 表示移动到文档末尾
        self.word.Selection.TypeText(self.Main_Title)  # 在这里替换为你的标题文本
        self.word.Selection.Style = self.word.ActiveDocument.Styles("标题 1")  # 设置为一级标题的样式
        # 将当前段落设置为居中对齐
        self.word.Selection.ParagraphFormat.Alignment = 1  # 0:左对齐； 1:居中对齐；2:表居右对齐
        self.word.Selection.TypeParagraph()  # 添加一个段落换行（即“回车”），因为标题后通常是一个新的段落
    def Set_Doc_Content(self, Content):
        self.Doc_Content = Content
    def Type_Doc_Content(self):
        self.word.Selection.EndKey(6)  # 6 表示移动到文档末尾
        self.word.Selection.TypeText(self.Doc_Content)  # 在这里替换为你的标题文本
        self.word.Selection.Style = self.word.ActiveDocument.Styles("正文")  # 设置为一级标题的样式
        # 将当前段落设置为居中对齐
        self.word.Selection.ParagraphFormat.Alignment = 0  # 0:左对齐； 1:居中对齐；2:表居右对齐
        self.word.Selection.TypeParagraph()  # 添加一个段落换行（即“回车”），因为标题后通常是一个新的段落

    def Set_First_Title(self, title):
        self.First_Title = title

    def Type_First_Title(self):
        self.word.Selection.TypeText(self.First_Title)  # 在这里替换为你的标题文本
        self.word.Selection.Style = self.word.ActiveDocument.Styles("标题 2")  # 设置为一级标题的样式
        self.word.Selection.TypeParagraph()  # 添加一个段落换行（即“回车”），因为标题后通常是一个新的段落

    def Set_Second_Title(self, title):
        self.Second_Title = title

    def Type_Second_Title(self):
        self.word.Selection.TypeText(self.Second_Title)  # 在这里替换为你的标题文本
        self.word.Selection.Style = self.word.ActiveDocument.Styles("标题 3")  # 设置为一级标题的样式
        self.word.Selection.TypeParagraph()  # 添加一个段落换行（即“回车”），因为标题后通常是一个新的段落
        # self.word.Selection.InsertBreak(Type=7)  # 7 代表分页符，二级标题总是分页进行输出

    def Set_Third_Title(self, title):
        self.Third_Title = title

    def Type_Third_Title(self):
        self.word.Selection.TypeText(self.Third_Title)  # 在这里替换为你的标题文本
        self.word.Selection.Style = self.word.ActiveDocument.Styles("标题 4")  # 设置为一级标题的样式
        self.word.Selection.TypeParagraph()  # 添加一个段落换行（即“回车”），因为标题后通常是一个新的段落

    def Set_Fourth_Title(self, title):
        self.Fourth_Title = title

    def Type_Fourth_Title(self):
        if self.Fourth_Title != "标书内容":
            self.word.Selection.TypeText(self.Fourth_Title)  # 在这里替换为你的标题文本
            self.word.Selection.Style = self.word.ActiveDocument.Styles("标题 5")  # 设置为一级标题的样式
        else:
            pass  # 在这里替换为你的标题文本
        self.word.Selection.TypeParagraph()  # 添加一个段落换行（即“回车”），因为标题后通常是一个新的段落

    def Set_Fifth_Title(self, title):
        self.Fifth_Title = title

    def Set_Sixth_Title(self, title):
        self.Sixth_Title = title

    def quit_docs(self):
        self.output_doc.Close(False)

    #插入一张表格
    def insert_table(self, data, merge_info=None):
        self.word.Selection.EndKey(Unit=6)  # Move to end of the document
        self.word.Selection.TypeParagraph()  # Add a new paragraph

        rows, cols = len(data), max(len(row) for row in data)  # Determine number of rows and columns
        table = self.output_doc.Tables.Add(self.word.Selection.Range, rows, cols)  # Add the table

        for row in range(rows):  # Fill in the table data
            for col in range(len(data[row])):
                cell = table.Cell(row + 1, col + 1)
                cell.Range.Text = str(data[row][col])
                cell.Range.Font.Size = 10.5  # Set font size to 10.5 for each cell

        if merge_info:  # Handle merged cells
            for start_row, start_col, end_row, end_col in merge_info:
                table.Cell(start_row, start_col).Merge(table.Cell(end_row, end_col))

        # Set the table style and properties
        table.AllowAutoFit = True
        try:
            # Set the table style to "Grid" (this style name may vary based on your Word version)
            table.Style = '网格型'
        except Exception as e:
            print(f"Error setting table style: {e}")
            # If setting the grid style fails, fallback to manual border setting
            for row in table.Rows:
                row.AllowBreakAcrossPages = False
                row.Alignment = win32.constants.wdAlignRowCenter  # Center align table rows
                for cell in row.Cells:
                    # Set individual borders for clarity
                    borders = [cell.Borders(win32.constants.wdBorderLeft),
                               cell.Borders(win32.constants.wdBorderRight),
                               cell.Borders(win32.constants.wdBorderTop),
                               cell.Borders(win32.constants.wdBorderBottom),
                               cell.Borders(win32.constants.wdBorderHorizontal),
                               cell.Borders(win32.constants.wdBorderVertical)]
                    for border in borders:
                        border.LineStyle = win32.constants.wdLineStyleSingle  # Solid line
                        border.LineWidth = win32.constants.wdLineWidth100pt  # Adjust line width as needed
                        border.Color = win32.constants.wdColorBlack  # Black color
                    cell.Range.Font.Size = 10.5  # Set font size to 10.5 for each cell
        # Move to end of the document and add a new paragraph after the table
        self.word.Selection.EndKey(Unit=6)  # Move to end of the document
        self.word.Selection.TypeParagraph()  # Add a new paragraph after the table
    # 插入给定路径的一张图片


    def insert_image(self, image_path):
        """
        在Word文档中插入一张图片。
        Args:
            image_path (str): 图片文件的完整路径。
        """
        try:
            # 移动到文档末尾
            self.word.Selection.EndKey(Unit=6)
            # 插入图片
            self.word.Selection.InlineShapes.AddPicture(FileName=image_path, LinkToFile=False, SaveWithDocument=True)
            # 换行,准备插入下一个内容
            self.word.Selection.TypeParagraph()
        except Exception as e:
            print(f"Error inserting image '{image_path}': {e}")

def main():
    root_directory = r"D:\Cache\ztzp-ConCaSys\WordTemplate"
    output_filename = "计算书.docx"
    merger = WordDocumentMerger(root_directory, output_filename)
    merger.Set_Main_Title("基坑计算书")
    merger.Type_Main_Title()
    merger.Set_First_Title("标题1")
    merger.Type_First_Title()
    merger.Set_Second_Title("标题2")
    merger.Type_Second_Title()
    merger.Set_Third_Title("标题3")
    merger.Type_Third_Title()
    merger.Set_Fourth_Title("标题4")
    merger.Type_Fourth_Title()
    print(f"合并成功")


if __name__ == "__main__":
    main()
