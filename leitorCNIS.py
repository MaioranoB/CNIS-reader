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

    if pdf_path[-4:] != '.pdf':
        print(pdf_path)
        print('Arquivo Inválido!')
        return

    id_filiado,seqs = readPDF(pdf_path)
    if id_filiado == False:
        print('Não foi possível ler o pdf\nExtrato Previdenciário não encontrado!')
        return

    saveasfilename = filedialog.asksaveasfilename()
    to_exel(id_filiado,seqs,saveasfilename)

    
if __name__ == '__main__':
    main()

#FAZER A PARADA DA BARRA DE PROGRESSO?