import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from PIL import Image, ImageTk
import datetime
import os
import sys

# Caminhos para a logo e a assinatura
if getattr(sys, 'frozen', False):
    # Se o aplicativo estiver sendo executado a partir de um executável
    base_path = sys._MEIPASS  # Obtenha o caminho temporário onde os arquivos são extraídos
else:
    # Se estiver sendo executado em um ambiente de desenvolvimento
    base_path = os.path.dirname(os.path.abspath(__file__))

# Variáveis para armazenar os caminhos da logo e da assinatura
logo_path = os.path.join(base_path, "logo.png")
assinatura_path = os.path.join(base_path, "assinatura.png")

# Função para selecionar uma nova logo
def selecionar_logo():
    global logo_path
    logo_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if logo_path:
        exibir_imagem(logo_path, label_logo)

# Função para selecionar uma nova assinatura
def selecionar_assinatura():
    global assinatura_path
    assinatura_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if assinatura_path:
        exibir_imagem(assinatura_path, label_assinatura)

# Função para exibir a imagem (logo ou assinatura) no label correspondente
def exibir_imagem(image_path, label):
    if image_path and os.path.exists(image_path):
        image = Image.open(image_path)
        image.thumbnail((100, 50))
        photo = ImageTk.PhotoImage(image)
        label.config(image=photo)
        label.image = photo  # Manter a referência da imagem

# Função para gerar o recibo em PDF
def gerar_recibo():
    # Obter valores dos campos
    try:
        valor = float(entry_valor.get())
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira um valor numérico para o campo 'Valor'")
        return
    
    pagador = entry_pagador.get()
    cpf_pagador = entry_cpf_pagador.get()
    referente = entry_referente.get()
    emissor = entry_emissor.get()
    cpf_emissor = entry_cpf_emissor.get()
    cidade = entry_cidade.get()
    data_pagamento = entry_data.get()
    forma_pagamento = pagamento_var.get()
    banco = entry_banco.get()

    # Escolher o caminho para salvar o PDF
    pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not pdf_path:  # Se o usuário cancelar, não fazer nada
        return
    
    # Criar arquivo PDF
    pdf_file = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    
    # Definir margens
    margem_esquerda = 2 * cm
    margem_direita = width - 2 * cm
    line_height = 0.5 * cm  # Espaçamento entre linhas
    current_y = height - 6 * cm  # Posição inicial do texto
    
    # Adicionar logo, se carregada
    if logo_path and os.path.exists(logo_path):
        pdf_file.drawImage(logo_path, margem_esquerda, height - 4 * cm, width=3 * cm, height=2 * cm)
    
    # Título do recibo
    pdf_file.setFont("Helvetica-Bold", 14)
    pdf_file.drawCentredString(width / 2, height - 2 * cm, "Recibo de Pagamento")

    # Valor em destaque
    pdf_file.setFont("Helvetica-Bold", 12)
    pdf_file.drawString(margem_direita - 3 * cm, height - 4 * cm, f"R$ {valor:,.2f}".replace('.', ','))

    # Texto do recibo
    pdf_file.setFont("Helvetica", 10)
    texto_recibo = (
        f"Recebi de {pagador} - CPF {cpf_pagador}, a importância de R$ {valor:.2f}, referente ao {referente}. Para maior clareza, firmo o presente recibo, que comprova o recebimento integral do valor mencionado, concedendo quitação plena, geral e irrevogável pela quantia recebida."
    )
    
    # Quebra de texto
    def quebra_texto(texto, largura_maxima):
        linhas = []
        palavras = texto.split(' ')
        linha_atual = ''
        
        for palavra in palavras:
            if len(linha_atual) + len(palavra) + 1 <= largura_maxima:
                linha_atual += ' ' + palavra if linha_atual else palavra
            else:
                linhas.append(linha_atual)
                linha_atual = palavra
        
        if linha_atual:
            linhas.append(linha_atual)
        
        return linhas

    linhas_texto = quebra_texto(texto_recibo, 110)  # 80 caracteres como limite
    for linha in linhas_texto:
        pdf_file.drawString(margem_esquerda, current_y, linha)
        current_y -= line_height

    # Informações de pagamento
    current_y -= line_height  # Espaço extra antes das informações de pagamento
    pdf_file.drawString(margem_esquerda, current_y, f"Pagamento recebido por {emissor} através da chave Pix: {cpf_emissor}, {banco}")
    current_y -= line_height
    pdf_file.drawString(margem_esquerda, current_y, f"{cidade}, {data_pagamento}")
    current_y -= line_height * 2  # Espaço extra antes da assinatura

    # Assinatura e dados do emissor centralizados
    if assinatura_path and os.path.exists(assinatura_path):
        pdf_file.drawImage(assinatura_path, width / 2 - 3 * cm, current_y - 2 * cm, width=6 * cm, height=1 * cm)
    current_y -= line_height * 6  # Ajustar o espaçamento abaixo da assinatura
    pdf_file.setFont("Helvetica-Bold", 10)
    pdf_file.drawCentredString(width / 2, current_y, f"{emissor}")
    pdf_file.setFont("Helvetica", 8)
    current_y -= line_height
    pdf_file.drawCentredString(width / 2, current_y, f"CPF: {cpf_emissor}")

    # Salvar o PDF
    pdf_file.save()
    messagebox.showinfo("Sucesso", f"Recibo gerado com sucesso em:\n{pdf_path}")

# Configuração da Interface Gráfica
root = tk.Tk()
root.title("Gerador de Recibos")
root.geometry("600x600")  # Tamanho da janela

# Estilizar com ttk
style = ttk.Style()
style.configure('TButton', font=('Arial', 10), padding=5)
style.configure('TLabel', font=('Arial', 10), padding=5)
style.configure('TEntry', font=('Arial', 10), padding=5)
style.configure('TFrame', background="#f0f0f0")
root.configure(bg="#f0f0f0")

# Criar um Frame para organizar os widgets
frame = ttk.Frame(root, padding=10)
frame.pack(fill=tk.BOTH, expand=True)

# Carregar e exibir logo, com botão para alterar
label_logo = ttk.Label(frame)
label_logo.grid(row=0, column=1, pady=10)
if logo_path and os.path.exists(logo_path):
    exibir_imagem(logo_path, label_logo)
ttk.Button(frame, text="Selecionar Logo", command=selecionar_logo).grid(row=0, column=0, pady=5)

# Campos do recibo
ttk.Label(frame, text="Valor").grid(row=1, column=0, sticky=tk.W, padx=5)
entry_valor = ttk.Entry(frame)
entry_valor.grid(row=1, column=1, padx=5)

ttk.Label(frame, text="Pagador").grid(row=2, column=0, sticky=tk.W, padx=5)
entry_pagador = ttk.Entry(frame)
entry_pagador.grid(row=2, column=1, padx=5)

ttk.Label(frame, text="CPF ou CNPJ do Pagador").grid(row=3, column=0, sticky=tk.W, padx=5)
entry_cpf_pagador = ttk.Entry(frame)
entry_cpf_pagador.grid(row=3, column=1, padx=5)

ttk.Label(frame, text="Referente").grid(row=4, column=0, sticky=tk.W, padx=5)
entry_referente = ttk.Entry(frame)
entry_referente.grid(row=4, column=1, padx=5)

ttk.Label(frame, text="Nome do Emissor").grid(row=5, column=0, sticky=tk.W, padx=5)
entry_emissor = ttk.Entry(frame)
entry_emissor.grid(row=5, column=1, padx=5)

ttk.Label(frame, text="CPF ou CNPJ do Emissor").grid(row=6, column=0, sticky=tk.W, padx=5)
entry_cpf_emissor = ttk.Entry(frame)
entry_cpf_emissor.grid(row=6, column=1, padx=5)

# Campo "Cidade"
ttk.Label(frame, text="Cidade").grid(row=7, column=0, sticky=tk.W, padx=5)
entry_cidade = ttk.Entry(frame)
entry_cidade.grid(row=7, column=1, padx=5)

# Campo "Banco" (linha seguinte)
ttk.Label(frame, text="Banco").grid(row=8, column=0, sticky=tk.W, padx=5)
entry_banco = ttk.Entry(frame)
entry_banco.grid(row=8, column=1, padx=5)

# Campo "Data do Pagamento" (ajuste a linha para 9 para evitar conflito)
ttk.Label(frame, text="Data do Pagamento").grid(row=9, column=0, sticky=tk.W, padx=5)
entry_data = ttk.Entry(frame)
entry_data.insert(0, datetime.datetime.today().strftime('%d/%m/%Y'))
entry_data.grid(row=9, column=1, padx=5)


# Forma de pagamento
pagamento_var = tk.StringVar(value="Dinheiro")
ttk.Label(frame, text="Forma de Pagamento").grid(row=10, column=0, sticky=tk.W, padx=5)
ttk.Radiobutton(frame, text="Dinheiro", variable=pagamento_var, value="Dinheiro").grid(row=10, column=1, sticky="w")
ttk.Radiobutton(frame, text="Pix", variable=pagamento_var, value="Pix").grid(row=10, column=2, sticky="w")
ttk.Radiobutton(frame, text="Cheque", variable=pagamento_var, value="Cheque").grid(row=10, column=3, sticky="w")
ttk.Radiobutton(frame, text="Transferência/Depósito", variable=pagamento_var, value="Transferência/Depósito").grid(row=11, column=1, sticky="w")
ttk.Radiobutton(frame, text="Cartão de Crédito/Débito", variable=pagamento_var, value="Cartão de Crédito/Débito").grid(row=11, column=2, sticky="w")

# Carregar e exibir assinatura, com botão para alterar
label_assinatura = ttk.Label(frame)
label_assinatura.grid(row=12, column=1, pady=10)
if assinatura_path and os.path.exists(assinatura_path):
    exibir_imagem(assinatura_path, label_assinatura)
ttk.Button(frame, text="Selecionar Assinatura", command=selecionar_assinatura).grid(row=12, column=0, pady=5)

# Botão para gerar o recibo
button_generate = ttk.Button(frame, text="Gerar Recibo", command=gerar_recibo)
button_generate.grid(row=13, column=1, pady=20)

# Iniciar a aplicação
root.mainloop()
