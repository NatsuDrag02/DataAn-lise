import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk

# Configuração do tema dark para matplotlib
plt.style.use('dark_background')

# Variáveis globais para os DataFrames
vendas_2020_df = vendas_2021_df = vendas_2022_df = None
devolucoes_df = clientes_df = lojas_df = produtos_df = None
vendas_df = None

#projeto da facul
# ====================================================
# Funções de Geração de Gráficos
# ====================================================

def graph_produtos_vendidos():
    grupo = vendas_df.groupby('SKU')['Quantidade'].sum().reset_index()
    grupo = grupo.merge(produtos_df[['SKU', 'Produto', 'Custo Unitario', 'PDV']], on='SKU', how='left')
    prod_mais = grupo.loc[grupo['Quantidade'].idxmax()]
    prod_menos = grupo.loc[grupo['Quantidade'].idxmin()]

    # Cria figura com tema dark
    fig, ax = plt.subplots(figsize=(12, 8), facecolor='#1a1a1a')
    ax.set_facecolor('#2d2d2d')

    categorias = ['Mais Vendido', 'Menos Vendido']
    quantidades = [prod_mais['Quantidade'], prod_menos['Quantidade']]

    # Cores mais profissionais para o tema dark
    bars = ax.bar(categorias, quantidades, color=['#4CAF50', '#FF5252'], width=0.5)

    # Adiciona título e rótulo do eixo y com cores claras
    ax.set_title("Comparativo: Produto Mais vs. Menos Vendido", fontsize=14, color='#e0e0e0')
    ax.set_ylabel("Quantidade Vendida", fontsize=12, color='#e0e0e0')

    # Ajusta cor dos ticks do eixo
    ax.tick_params(axis='x', colors='#e0e0e0')
    ax.tick_params(axis='y', colors='#e0e0e0')

    # Adiciona grade sutil
    ax.grid(True, linestyle='--', alpha=0.2, color='#888888')

    # Função para quebrar texto em múltiplas linhas se for muito grande
    def quebrar_texto(texto, max_chars=15):
        if len(texto) <= max_chars:
            return texto

        palavras = texto.split()
        linhas = []
        linha_atual = ""

        for palavra in palavras:
            if len(linha_atual) + len(palavra) <= max_chars:
                if linha_atual:
                    linha_atual += " " + palavra
                else:
                    linha_atual = palavra
            else:
                linhas.append(linha_atual)
                linha_atual = palavra

        if linha_atual:
            linhas.append(linha_atual)

        return '\n'.join(linhas)

    # Nome do produto mais vendido - na parte superior da figura
    ax.text(0, -0.1, quebrar_texto(prod_mais['Produto']),
            ha='center', va='top', fontweight='bold', fontsize=11,
            transform=ax.get_xaxis_transform(), color='#e0e0e0')

    # Nome do produto menos vendido - na parte superior da figura
    ax.text(1, -0.1, quebrar_texto(prod_menos['Produto']),
            ha='center', va='top', fontweight='bold', fontsize=11,
            transform=ax.get_xaxis_transform(), color='#e0e0e0')

    # Informações dentro das barras
    ax.text(0, quantidades[0] / 2,
            f"Custo: {prod_mais['Custo Unitario']}\nPDV: {prod_mais['PDV']}\nQtd: {prod_mais['Quantidade']}",
            ha='center', va='center', fontsize=10, color='#ffffff', fontweight='bold')

    # Para a barra menor, coloca as informações dentro (se tiver espaço) ou logo acima
    if quantidades[1] > (max(quantidades) * 0.2):  # Se a barra tiver pelo menos 20% do tamanho da maior
        pos_y = quantidades[1] / 2
        va = 'center'
    else:
        pos_y = quantidades[1] + (max(quantidades) * 0.05)
        va = 'bottom'

    ax.text(1, pos_y,
            f"Custo: {prod_menos['Custo Unitario']}\nPDV: {prod_menos['PDV']}\nQtd: {prod_menos['Quantidade']}",
            ha='center', va=va, fontsize=10, color='#ffffff', fontweight='bold')

    # Remove bordas do frame
    for spine in ax.spines.values():
        spine.set_color('#444444')

    # Aumenta o espaço abaixo do gráfico para acomodar os nomes
    plt.subplots_adjust(bottom=0.25)

    return fig


def graph_lojas_vendas():
    vendas_loja = vendas_df.groupby('ID Loja')['Quantidade'].sum().reset_index()
    top_lojas = vendas_loja.sort_values(by='Quantidade', ascending=False).head(5)

    dados_tabela = []
    for _, loja in top_lojas.iterrows():
        id_loja = loja['ID Loja']
        total_loja = loja['Quantidade']
        dados_loja = lojas_df.loc[lojas_df['ID Loja'] == id_loja].iloc[0]
        nome_loja = dados_loja['Nome da Loja']
        endereco = "N/A"

        vendas_loja_df = vendas_df[vendas_df['ID Loja'] == id_loja]
        grupo_prod = vendas_loja_df.groupby('SKU')['Quantidade'].sum().reset_index()
        if grupo_prod.empty:
            continue
        prod_top = grupo_prod.loc[grupo_prod['Quantidade'].idxmax()]
        prod_info = produtos_df[produtos_df['SKU'] == prod_top['SKU']].iloc[0]
        nome_prod = prod_info['Produto']
        qtd = prod_top['Quantidade']
        lucro = prod_info['PDV'] - prod_info['Custo Unitario']

        dados_tabela.append([nome_loja, total_loja, nome_prod, qtd, lucro])

    fig, ax = plt.subplots(figsize=(10, 3), facecolor='#1a1a1a')
    ax.set_facecolor('#2d2d2d')
    ax.axis('tight')
    ax.axis('off')

    cabecalho = ["Loja", "Total Vendas", "Prod Mais Vendido", "Qtd", "Lucro"]

    # Criação da tabela com tema escuro
    tabela = ax.table(cellText=[cabecalho] + dados_tabela,
                      loc='center',
                      cellLoc='center',
                      cellColours=[['#333333'] * len(cabecalho)] + [['#2d2d2d'] * len(cabecalho)] * len(dados_tabela))

    # Estiliza a tabela
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(10)

    # Configurações de cores para a tabela
    for (i, j), cell in tabela.get_celld().items():
        if i == 0:  # Cabeçalho
            cell.set_text_props(color='white', fontweight='bold')
            cell.set_facecolor('#444444')
        else:  # Células normais
            cell.set_text_props(color='#e0e0e0')
            if j == 4:  # Coluna de lucro
                cell.set_text_props(color='#7FFF7F' if float(cell.get_text().get_text()) > 0 else '#FF7F7F')

    ax.set_title("Top 5 Lojas e Produto Mais Vendido", fontweight="bold", color='#e0e0e0')
    return fig


def graph_devolucoes_info():
    # Primeiro somamos o total de devoluções por SKU
    total_por_produto = devolucoes_df.groupby('SKU')['Qtd Devolvida'].sum().reset_index()

    # Ordenamos pelo total de devoluções (decrescente) e pegamos os 10 maiores
    top_produtos = total_por_produto.sort_values(by='Qtd Devolvida', ascending=False).head(10)

    # Agora para cada produto, encontramos o motivo mais comum
    resultado = []
    for _, produto in top_produtos.iterrows():
        sku = produto['SKU']
        qtd_total = produto['Qtd Devolvida']

        # Filtra só as devoluções deste SKU
        devs_deste_sku = devolucoes_df[devolucoes_df['SKU'] == sku]

        # Agrupa por motivo e encontra o mais comum
        motivo_group = devs_deste_sku.groupby('Motivo Devolução')['Qtd Devolvida'].sum().reset_index()
        motivo_principal = motivo_group.loc[motivo_group['Qtd Devolvida'].idxmax()]['Motivo Devolução']

        # Busca o nome do produto
        nome_produto = "Desconhecido"
        if sku in produtos_df['SKU'].values:
            nome_produto = produtos_df.loc[produtos_df['SKU'] == sku, 'Produto'].iloc[0]

        resultado.append({'SKU': sku, 'Produto': nome_produto,
                          'Qtd Devolvida': qtd_total,
                          'Motivo Principal': motivo_principal})

    # Converte para DataFrame para facilitar o trabalho
    resultado_df = pd.DataFrame(resultado)
    resultado_df = resultado_df.sort_values(by='Qtd Devolvida', ascending=True)  # Para o gráfico horizontal

    fig, ax = plt.subplots(figsize=(8, 6), facecolor='#1a1a1a')
    ax.set_facecolor('#2d2d2d')

    # Uso de uma cor mais suave para tema dark
    bars = ax.barh(resultado_df['Produto'], resultado_df['Qtd Devolvida'], color='#ff7043')

    max_devolucoes = resultado_df['Qtd Devolvida'].max()
    ax.set_xlim(0, max_devolucoes * 1.3)  # Mais espaço para a esquerda

    ax.set_title("Produtos com Mais Devoluções", loc='center', fontsize=14, color='#e0e0e0')
    ax.set_xlabel("Quantidade Devolvida", fontsize=12, color='#e0e0e0')

    # Ajusta cor dos ticks do eixo
    ax.tick_params(axis='x', colors='#e0e0e0')
    ax.tick_params(axis='y', colors='#e0e0e0')

    # Adiciona grade sutil
    ax.grid(True, axis='x', linestyle='--', alpha=0.2, color='#888888')

    # Remove bordas do frame
    for spine in ax.spines.values():
        spine.set_color('#444444')

    # Adiciona o motivo principal e quantidade nas barras
    for i, (_, row) in enumerate(resultado_df.iterrows()):
        motivo_texto = row['Motivo Principal']
        if len(motivo_texto) > 20:  # Trunca se for muito longo
            motivo_texto = motivo_texto[:18] + "..."

        ax.text(row['Qtd Devolvida'] / 2, i,
                f"{motivo_texto}: {int(row['Qtd Devolvida'])}",
                va='center', ha='center', fontsize=9,
                color='#222222', fontweight='bold')

    fig.tight_layout()
    fig.subplots_adjust(left=0.25, right=0.9)

    return fig


def graph_genero_produtos():
    dados = vendas_df.merge(clientes_df[['ID Cliente', 'Genero', 'Primeiro Nome', 'Sobrenome']], on='ID Cliente',
                            how='left')
    total_por_genero = dados.groupby('Genero')['Quantidade'].sum().reset_index()

    # Cria figura com tema dark
    fig, axs = plt.subplots(1, 2, figsize=(16, 8), facecolor='#1a1a1a')
    axs[0].set_facecolor('#2d2d2d')

    # Cores mais modernas e adequadas ao tema dark
    cores = []
    for gen in total_por_genero['Genero']:
        if gen.lower() in ['masculino', 'm']:
            cores.append('#4e79a7')  # Azul mais suave
        elif gen.lower() in ['feminino', 'f']:
            cores.append('#f28e2b')  # Rosa/Laranja mais suave
        else:
            cores.append('#76b7b2')  # Verde-água para outros

    axs[0].bar(total_por_genero['Genero'], total_por_genero['Quantidade'], color=cores)
    axs[0].set_title("Total de Vendas por Gênero", fontsize=14, color='#e0e0e0')
    axs[0].set_ylabel("Quantidade Vendida", fontsize=12, color='#e0e0e0')
    axs[0].tick_params(axis='both', colors='#e0e0e0', labelsize=10)

    # Adiciona grade sutil
    axs[0].grid(True, axis='y', linestyle='--', alpha=0.2, color='#888888')

    # Remove bordas do frame
    for spine in axs[0].spines.values():
        spine.set_color('#444444')

    # Prepara tabela com tema dark
    axs[1].set_facecolor('#2d2d2d')
    axs[1].axis('tight')
    axs[1].axis('off')

    info = []
    generos = total_por_genero['Genero'].unique()
    col_labels = ["Gênero", "Total Vendas", "Prod Mais Comprado", "Qtd Prod", "Cliente", "Qtd Cliente"]

    # Reorganizando os dados para formato vertical
    table_data = []
    for i, label in enumerate(col_labels):
        row_data = [label]
        for genero in generos:
            dados_gen = dados[dados['Genero'] == genero]
            total_vendido = dados_gen['Quantidade'].sum()
            prod_group = dados_gen.groupby('SKU')['Quantidade'].sum().reset_index()
            if not prod_group.empty:
                prod_max = prod_group.loc[prod_group['Quantidade'].idxmax()]
                prod_info = produtos_df[produtos_df['SKU'] == prod_max['SKU']]
                prod_nome = prod_info.iloc[0]['Produto'] if not prod_info.empty else prod_max['SKU']
                qtd_prod = prod_max['Quantidade']
            else:
                prod_nome, qtd_prod = "N/A", "N/A"
            cliente_group = dados_gen.groupby('ID Cliente')['Quantidade'].sum().reset_index()
            if not cliente_group.empty:
                cliente_max = cliente_group.loc[cliente_group['Quantidade'].idxmax()]
                cliente_info = clientes_df[clientes_df['ID Cliente'] == cliente_max['ID Cliente']]
                if not cliente_info.empty:
                    nome_cliente = cliente_info.iloc[0]['Primeiro Nome'] + " " + cliente_info.iloc[0]['Sobrenome']
                else:
                    nome_cliente = str(cliente_max['ID Cliente'])
                qtd_cliente = cliente_max['Quantidade']
            else:
                nome_cliente, qtd_cliente = "N/A", "N/A"

            if i == 0:
                row_data.append(genero)
            elif i == 1:
                row_data.append(total_vendido)
            elif i == 2:
                row_data.append(prod_nome)
            elif i == 3:
                row_data.append(qtd_prod)
            elif i == 4:
                row_data.append(nome_cliente)
            elif i == 5:
                row_data.append(qtd_cliente)

        table_data.append(row_data)

    # Cores para as células da tabela
    cell_colors = []
    for i in range(len(table_data)):
        row_colors = ['#444444']
        for j in range(1, len(generos) + 1):
            row_colors.append('#2d2d2d')
        cell_colors.append(row_colors)

    table = axs[1].table(cellText=table_data, loc='center', cellLoc='center',
                         cellColours=cell_colors)

    # Ajusta cores do texto da tabela
    for (i, j), cell in table.get_celld().items():
        if j == 0:  # Primeira coluna
            cell.set_text_props(fontweight='bold', color='white')
        else:
            cell.set_text_props(color='#e0e0e0')

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    axs[1].set_title("Detalhes por Gênero", fontweight="bold", fontsize=14, color='#e0e0e0')

    fig.suptitle(
        f"Análise por Gênero - Maior Volume: {total_por_genero.loc[total_por_genero['Quantidade'].idxmax()]['Genero']}",
        fontsize=16, color='#e0e0e0')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


# ====================================================
# Função para Atualizar as Abas (agora com ordem corrigida)
# ====================================================

def atualizar_abas():
    # Atualiza a Aba Produtos
    for widget in produtos_frame.winfo_children():
        widget.destroy()
    fig1 = graph_produtos_vendidos()
    canvas1 = FigureCanvasTkAgg(fig1, master=produtos_frame)
    canvas1.draw()
    canvas1.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

    # Atualiza a Aba Lojas
    for widget in lojas_frame.winfo_children():
        widget.destroy()
    fig2 = graph_lojas_vendas()
    canvas2 = FigureCanvasTkAgg(fig2, master=lojas_frame)
    canvas2.draw()
    canvas2.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

    # Atualiza a Aba Devolucoes
    for widget in devolucoes_frame.winfo_children():
        widget.destroy()
    fig3 = graph_devolucoes_info()
    canvas3 = FigureCanvasTkAgg(fig3, master=devolucoes_frame)
    canvas3.draw()
    canvas3.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

    # Atualiza a Aba Genero
    for widget in genero_frame.winfo_children():
        widget.destroy()
    fig4 = graph_genero_produtos()
    canvas4 = FigureCanvasTkAgg(fig4, master=genero_frame)
    canvas4.draw()
    canvas4.get_tk_widget().pack(fill=ctk.BOTH, expand=True)


# ====================================================
# Função para Carregar os Dados (ao clicar no botão)
# ====================================================

def carregar_dados():
    global vendas_2020_df, vendas_2021_df, vendas_2022_df, devolucoes_df
    global clientes_df, lojas_df, produtos_df, vendas_df

    status_label.configure(text="Carregando dados...")

    caminho_diretorio = r'C:\Users\Alysson Rodrigues\Downloads\Data'
    vendas_2020_df = pd.read_excel(f'{caminho_diretorio}\\baseVendas2020.xlsx')
    vendas_2021_df = pd.read_excel(f'{caminho_diretorio}\\baseVendas2021.xlsx')
    vendas_2022_df = pd.read_excel(f'{caminho_diretorio}\\baseVendas2022.xlsx')
    devolucoes_df = pd.read_excel(f'{caminho_diretorio}\\baseDevolucoes.xlsx')
    clientes_df = pd.read_excel(f'{caminho_diretorio}\\cadastroClientes.xlsx')
    lojas_df = pd.read_excel(f'{caminho_diretorio}\\cadastroLojas.xlsx')
    produtos_df = pd.read_excel(f'{caminho_diretorio}\\cadastroProdutos.xlsx')

    vendas_df = pd.concat([vendas_2020_df, vendas_2021_df, vendas_2022_df], ignore_index=True)

    status_label.configure(text="Dados carregados com sucesso!")
    atualizar_abas()


# ====================================================
# Interface com CustomTkinter
# ====================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Análise de Vendas")
root.geometry("1000x700")
root.configure(fg_color="#1a1a1a")  # Background mais escuro

top_frame = ctk.CTkFrame(root, fg_color="#2d2d2d")
top_frame.pack(fill=ctk.X, padx=10, pady=10)
carregar_btn = ctk.CTkButton(top_frame, text="Carregar Dados", command=carregar_dados,
                             fg_color="#3498db", hover_color="#2980b9")
carregar_btn.pack(side=ctk.LEFT, padx=(0, 10))
status_label = ctk.CTkLabel(top_frame, text="Dados não carregados", text_color="#e0e0e0")
status_label.pack(side=ctk.LEFT)

tab_control = ctk.CTkTabview(root, fg_color="#1a1a1a", segmented_button_fg_color="#2d2d2d",
                             segmented_button_selected_color="#3498db",
                             segmented_button_selected_hover_color="#2980b9",
                             segmented_button_unselected_color="#2d2d2d")
tab_control.pack(expand=1, fill='both', padx=10, pady=10)

tab_control.add("Produtos")
produtos_frame = tab_control.tab("Produtos")
produtos_frame.configure(fg_color="#1a1a1a")

tab_control.add("Lojas")
lojas_frame = tab_control.tab("Lojas")
lojas_frame.configure(fg_color="#1a1a1a")

tab_control.add("Devolucoes")
devolucoes_frame = tab_control.tab("Devolucoes")
devolucoes_frame.configure(fg_color="#1a1a1a")

tab_control.add("Genero")
genero_frame = tab_control.tab("Genero")
genero_frame.configure(fg_color="#1a1a1a")

root.mainloop()