from sys import float_repr_style
import pandas as pd

# On définit les largeur des colonnes pour la colonne L et les colonnes B à F
WIDTHS = {
    'L:L' : 20,
    'B:F' : 9
}

# On crée une fonction qui ajuste les colonnes de la feuille excel selon nos paramètres
def set_widths(pair, writer):
    worksheet = writer.sheets[pair]
    for k,v in WIDTHS.items():
        worksheet.set_column(k, v)


# Ceci est la fonction de création du chart
def get_line_chart(book, start_row, end_row, labels_col, data_col, title, sheetname):
    # add_chart permet de créer le graphe type : line
    chart = book.add_chart({'type' : 'line'})
    # add_series permet de définir les infos pour l'abscisse (categorie) et ordonné(values)
    chart.add_series({
        'categories' : [sheetname, start_row, labels_col, end_row, labels_col],
        'values' : [sheetname, start_row, data_col, end_row, data_col],
        'line' : {'color' : 'blue'}
    })

    # On définit le nom du graphe et si on veut une légende
    chart.set_title({'name' : title})
    chart.set_legend({'none' : True})

    return chart

def add_chart(pair, cross, df, writer):
    # On crée un workbook et un worksheet 
    # Ceci définit la zone de travail et le tableau qui sera utilisé
    workbook = writer.book
    worksheet = writer.sheets[pair]

    # On crée un line chart en entrant les infos sur le chart
    # On a le workbook, la ligne de début et la ligne de fin (df.shape[0])
    # On a la colonne de début et la colonne de fin
    # Le nom du graphe
    # le nom de la feuille excel
    chart = get_line_chart(workbook, 1, df.shape[0], 11, 12,
                           f"GAIN_C for {pair} {cross}", pair)
    chart.set_size({'x_scale' :  2.5, 'y_scale': 2.5})

    # La première valeur correpond à la ligne où sera placé le graphique
    # la deuxième c'est la colonne où elle sera placée
    # la dernière c'est le chart qu'on veut afficher
    worksheet.insert_chart(1, 14, chart)


def add_pair_charts(df_ma_res, df_ma_trades, writer):
    # On définit les colonnes du nouveau tableau excel
    cols = ['time', 'GAIN_C']
    # On crée un dataframe à partir du premier trade dans les données générales
    df_temp = df_ma_res.drop_duplicates(subset="pair")

    # On extrait du dataframe des données détaillées les données correspondantes au trade sélectionné précédemment
    for _, row in df_temp.iterrows():
        dft = df_ma_trades[(df_ma_trades.cross == row.cross)&
                           (df_ma_trades.pair == row.pair)]
        
        # On peut ajouter le nouveau dataframe dans le fichier excel
        # La colonne 11 correspond au time
        dft[cols].to_excel(
                    writer, 
                    sheet_name=row.pair, 
                    index=False,
                    startrow=0,
                    startcol=11
                    )
        
        # Définition de la largeur des colonnes (pour éviter les ####)
        set_widths(row.pair, writer)
        # On ajoute le chart créé ici
        add_chart(row.pair, row.cross, dft, writer)
    
def add_pair_sheets(df_ma_res, writer):
    # Ajouter les données générales sur les trades par paire de devises
    # Chaque paire correspondant à une feuille excel
    for p in df_ma_res.pair.unique():
        tdf = df_ma_res[df_ma_res.pair == p]
        tdf.to_excel(writer, sheet_name=p, index=False)

def prepare_data(df_ma_res, df_ma_trades):
    # On classe les données par paire de devise et le total de gain
    df_ma_res.sort_values(
        by=['pair', 'total_gain'], 
        ascending=[True, False],
        inplace=True)
    # On supprime les infos sur la time zone dans la coonne time du dataframe détaillé
    df_ma_trades['time'] = [x.replace(tzinfo=None) for x in df_ma_trades['time']]

def process_data(df_ma_res, df_ma_trades, writer):
    # On classe les données des trades
    prepare_data(df_ma_res, df_ma_trades)
    # On les ajoute dans le fichier excel par pair de devises
    add_pair_sheets(df_ma_res, writer)
    # On ajoute le dataframe des gains cumulés à chaque période de temps
    add_pair_charts(df_ma_res, df_ma_trades, writer)

def create_excel(df_ma_res, df_ma_trades, granularity):
    # Création du fichir excel
    # le wrtier définit le nom du fichier et le logiciel (Excel)
    filename = f"ma_sim_{granularity}.xlsx"
    writer = pd.ExcelWriter(filename, engine="xlsxwriter")

    # Ajout des données dans les fichiers
    process_data(
        df_ma_res[df_ma_res.granularity == granularity].copy(),
        df_ma_trades[df_ma_trades.granularity == granularity].copy(),
        writer)

    writer.close()

def create_ma_res(granularity):
    df_ma_res = pd.read_pickle("./data/ma_res.pkl")
    df_ma_trades = pd.read_pickle("./data/ma_trades.pkl")
    create_excel(df_ma_res, df_ma_trades, granularity)


if __name__ == "__main__":

    df_ma_res = pd.read_pickle("../data/ma_res.pkl")
    df_ma_trades = pd.read_pickle("../data/ma_trades.pkl")

    # Exécution de la fonction de création pour chacune des granularités
    create_excel(df_ma_res, df_ma_trades, "H1")
    create_excel(df_ma_res, df_ma_trades, "H4")
