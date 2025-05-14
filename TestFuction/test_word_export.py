import pythoncom
import win32com.client as win32

def main():
    pythoncom.CoInitialize()
    word = win32.Dispatch('Word.Application')
    word.Visible = False
    doc = word.Documents.Add()
    word.Selection.TypeText("Hello, Word!")
    doc.SaveAs(r"C:\Users\CN\Desktop\test.docx")
    doc.Close()
    word.Quit()

if __name__ == "__main__":
    main()