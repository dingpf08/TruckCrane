import win32com.client as win32

def create_word_table():
    # Start Microsoft Word
    word = win32.gencache.EnsureDispatch('Word.Application')
    word.Visible = True  # Make Word visible to the user
    doc = word.Documents.Add()  # Add a new document

    # Define the data for the table
    data = [
        ["坑壁土类型", "粘性土", "坑壁土的重度γ(kN/m³)", "20"],
        ["坑壁土的内摩擦角φ(°)", "15", "坑壁土粘聚力c(kN/m²)", "12"],
        ["坑顶护道上均布荷载q(kN/m²)", "2", "", ""]
    ]

    # Add a table to the document
    table = doc.Tables.Add(Range=doc.Range(0, 0), NumRows=len(data), NumColumns=4)
    table.Style = 'Table Grid'  # Apply the 'Table Grid' style which includes borders for cells

    # Fill in the table with data
    for row_idx, row_data in enumerate(data, start=1):
        for col_idx, text in enumerate(row_data, start=1):
            cell = table.Cell(Row=row_idx, Column=col_idx)
            cell.Range.Text = text
            # Set the cell borders (optional, if you need specific border settings)
            cell.Borders.Enable = True  # Enable borders for the current cell

    # Save the document
    file_path = r'C:\table.docx'  # Change to your desired file path
    doc.SaveAs2(FileName=file_path)

    # Optionally, you can close the document
    # doc.Close()

if __name__ == "__main__":
    create_word_table()
