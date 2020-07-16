def main():
    import tkinter as tk
    from tkinter import filedialog
    from lerPDF import readPDF,to_exel

    root = tk.Tk()
    root.withdraw()

    pdf_path = filedialog.askopenfilename(
        title = 'Selecione o arquivo pdf',
        filetypes = (('arquivos pdf','*.pdf'),('todos os arquivos','*.*'))
        #initialdir='/home/bernardo/Área de Trabalho',
    ) 

    if pdf_path == ():
        return
    elif pdf_path[-4:] != '.pdf':
        print(pdf_path)
        print('Arquivo Inválido!')
        return

    id_filiado,seqs = readPDF(pdf_path)
    if id_filiado == False:
        print('Não foi possível ler o pdf\nExtrato Previdenciário não encontrado!')
        return

    while True:
        saveasfilename = filedialog.asksaveasfilename(filetypes = (('*.xlsx','*.xlsx'),('todos os arquivos','*.*')))
        
        if '.xls' in saveasfilename:
            to_exel(id_filiado,seqs,saveasfilename)
            break
        elif saveasfilename == '' or saveasfilename == ():
            break
        else:
            print('Formato inválido. Escolha uma extensão .xlsx ou .xls')
    

    
if __name__ == '__main__':
    main()
