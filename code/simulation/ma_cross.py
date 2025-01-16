import pandas as pd
import os.path
from infrastructure.instrument_collection import instrumentCollection as ic
from simulation.ma_excel import create_ma_res


class MAResult:
    def __init__(self, df_trades, pairname, ma_l, ma_s, granularity):
        self.pairname = pairname
        self.df_trades = df_trades
        self.ma_s = ma_s
        self.ma_l = ma_l
        self.granularity = granularity
        self.result = self.result_ob()

    def __repr__(self):
        return str(self.result)

    def result_ob(self):
        return dict(
            pair = self.pairname,
            num_trades = self.df_trades.shape[0],
            total_gain = int(self.df_trades.GAIN.sum()),
            mean_gain = int(self.df_trades.GAIN.mean()),
            min_gain = int(self.df_trades.GAIN.min()),
            max_gain = int(self.df_trades.GAIN.max()),
            ma_l = self.ma_l,
            ma_s = self.ma_s,
            cross = f"{self.ma_s}_{self.ma_l}",
            granularity = self.granularity
        )

BUY = 1
SELL = -1
NONE = 0
# Cette valeur servira à récupérer la colonne correspondant à une période donnée
get_ma_col = lambda x: f"MA_{x}"
# Cette valeur servira à créer la colonne pour retrouver le point de contact
add_cross = lambda x: f"{x.ma_s}_{x.ma_l}"

def is_trade(row):
    if row.DELTA >= 0 and row.DELTA_PREV < 0:
        return BUY
    elif row.DELTA < 0 and row.DELTA_PREV >= 0:
        return SELL
    return NONE


def load_price_data(pair, granularity, ma_list):
    df = pd.read_pickle(f"./data/{pair}_{granularity}.pkl")
    # Calcul de la moyenne périodique
    for ma in ma_list:
        df[get_ma_col(ma)]= df.mid_c.rolling(window=ma).mean()
    # On efface les valeurs nulles en début du tableau
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def get_trades(df_analysis, instrument, granularity):
    df_trades = df_analysis[df_analysis.TRADE != NONE].copy()
    # On décale les différences de prix et on supprime les valeurs vides (en début de tableau)
    df_trades["DIFF"] = df_trades.mid_c.diff().shift(-1)
    df_trades.fillna(0, inplace=True)
    # Les gains se mesurent en pips
    df_trades["GAIN"] = df_trades.DIFF / instrument.pipLocation
    # On définit la valuer des gains en fonction de si on est dans un buy ou sell
    df_trades["GAIN"] = df_trades["GAIN"] * df_trades["TRADE"]
    # Le timing du trade
    df_trades["granularity"] = granularity
    # Les devises
    df_trades["pair"] = instrument.name
    # Le gain final c'est la somme des valeurs de la colonne gain
    df_trades["GAIN_C"] = df_trades["GAIN"].cumsum()
    return df_trades

def assess_pair(price_data, ma_l, ma_s, instrument, granularity):
    # On récupère le dataframe des prix
    df_analysis = price_data.copy()
    # On calcule la différence entre les 2 courbes des moyennes
    df_analysis["DELTA"] = df_analysis[ma_s] - df_analysis[ma_l]
    # DELTA_PREV permet de savoir s'il y a eu contact entre les 2 courbes
    # On le verifie par le changement de signe entre DELTA et DELTA PREV
    df_analysis["DELTA_PREV"] = df_analysis["DELTA"].shift(1)
    # On utilise apply pour créer une nouvelle colonne à partir d'une fonction
    # l'entrée de la fonction sera chaque ligne du dataframe
    df_analysis["TRADE"] = df_analysis.apply(is_trade, axis=1)

    df_trades = get_trades(df_analysis, instrument, granularity)
    df_trades["ma_l"] = ma_l
    df_trades["ma_s"] = ma_s
    # On crée une colonne cross qui va avoir pour valeur la concatenation des ma_l et ma_s
    df_trades["cross"] = df_trades.apply(add_cross, axis=1)
    return MAResult(
        df_trades,
        instrument.name,
        ma_l,
        ma_s,
        granularity
    )

def append_df_to_file(df, filename):
    # On enregistre les valeurs dans le fichier
    # Si le fichier existe
    if os.path.isfile(filename):
        fd = pd.read_pickle(filename)
        df = pd.concat([fd, df])

    # On réorganise les index pour faciliter les concatenations des dataframes
    df.reset_index(inplace=True, drop=True)
    df.to_pickle(filename)
    # On affiche les infos sur le nombres de lignes et colonnes
    print(filename, df.shape)
    # On affiche les 2 dernières lignes de tableau
    print(df.tail(2))

def get_fullname(filepath, filename):
    # On recupère le fichier pkl
    return f"{filepath}/{filename}.pkl"

def process_macro(results_list, filename):
    # On crée le dataframe à partir des données générales sur les trades
    # En regardant la classe MAResult on comprend que l'attribut result renvoie juste le sommaire sur les trades
    rl = [x.result for x in results_list]
    df = pd.DataFrame.from_dict(rl)
    # On exécute cette fonction pour ajouter le df dans le fichier
    append_df_to_file(df, filename)

def process_trades(results_list, filename):
    # On récupère les infos détaillées pour tous les trades
    # les informations détaillées sur le trade sont obtenus avec la fonction get_trades
    # Le resultat étant envoyé dans assess_pair
    df = pd.concat([x.df_trades for x in results_list])
    append_df_to_file(df, filename)


def process_results(results_list, filepath):
    # Le dataframe sur les données sommaires 
    process_macro(results_list, get_fullname(filepath, "ma_res"))
    # Le datframe sur les données détaillés
    process_trades(results_list, get_fullname(filepath, "ma_trades"))
    

def analyse_pair(instrument, granularity, ma_long, ma_short, filepath):
    # On récupère les colonnes qui seront utilisées pour extraire le dataframe
    ma_list = set(ma_long + ma_short)
    pair = instrument.name

    # On ressort le dataframe des prix
    price_data = load_price_data(pair, granularity, ma_list)
    # print(pair)
    # print(price_data.head(3))

    results_list = []

    # On se rassure que la moyenne des courtes périodes soit inférieure à celle des longues
    for ma_l in ma_long:
        for ma_s in ma_short:
            if ma_l <= ma_s:
                continue

            # On utilise ma_result pour pouvoir exécuter la fonction assess_pair
            ma_result = assess_pair(
                price_data,
                get_ma_col(ma_l),
                get_ma_col(ma_s),
                instrument,
                granularity
            )

            # print(ma_result)
            results_list.append(ma_result)
    process_results(results_list, filepath)



def run_ma_sim(curr_list=["CAD", "JPY", "GBP", "NZD"],
               granularity=["H1"],
               ma_long=[20,40],
               ma_short=[10],
               filepath="./data"):
    # On recupère les données de l'API et on crée un dictionnaire
    ic.LoadInstruments("./data")
    for g in granularity:
        for p1 in curr_list:
            for p2 in curr_list:
                pair = f"{p1}_{p2}"
                # On parcourt les éléments du dictionnaire et on exécute la fonction analyse_pair
                # la fonction analyse pair exécute la fonction assess_pair et affiche les "print"
                if pair in ic.instruments_dict.keys():
                    analyse_pair(ic.instruments_dict[pair], g, ma_long, ma_short, filepath)

        create_ma_res(g)