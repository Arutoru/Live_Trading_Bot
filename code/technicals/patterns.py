import pandas as pd

HANGING_MAN_BODY = 15.0
HANGING_MAN_HEIGHT = 75.0
SHOOTING_STAR_HEIGHT = 25.0

SPINNING_TOP_MIN = 40.0
SPINNING_TOP_MAX = 60.0

MARUBOZU = 98.0

ENGULFING_FACTOR = 1.1

TWEEZER_BODY = 15.0
TWEEZER_HL = 0.01
TWEEZER_TOP_BODY = 40.0
TWEEZER_BOTTOM_BODY = 60.0

MORNING_STAR_PREV2_BODY = 90.0
MORNING_STAR_PREV_BODY = 10.0

# Règle pour avoir un Marubozu (le corps occupe presque tout le chandelier) 
# Future changement de tendance si le corps occupe plus de 98% du chandelier
apply_marubozu = lambda x : x.body_perc > MARUBOZU

# Règles pour avoir un pendu ou un marteau
# Si pendu (rouge) future tendance haussière
# Si marteau (vert) future tendance baissière
def apply_hanging_man(row):
#   Le bas du corps doit être à plus de 75% du chandelier
#   Le corps ne doit pas avoir plus de 15% du chandelier
    if row.body_bottom_perc > HANGING_MAN_HEIGHT:
        if row.body_perc < HANGING_MAN_BODY:
            return True
        return False

# Règles pour avoir l'étoile filante ou le marteau inversé
# Si étoile filante (rouge) future tendance baissière
# Si marteau inversé (vert) future tendance haussière
def apply_shooting_star(row):
#   Le bas du corps doit être à moins de 25% du chandelier
#     Le corps ne doit pas avoir plus de 15% du chandelier
    if row.body_bottom_perc < SHOOTING_STAR_HEIGHT:
        if row.body_perc < HANGING_MAN_BODY:
            return True
        return False

# Règle pour le spinning top (le corps est très petit par rapport au chandelier)
# Si bearish spinning top (rouge) future tendance baissière
# Si bullish spinning top (vert) future tendance haussière
def apply_spinning_top(row):
#   Le corps doit être compris entre 40 et 60% du chandelier
#   Le corps ne doit pas avoir plus de 15% du chandelier
    if row.body_bottom_perc < SPINNING_TOP_MAX:
        if row.body_bottom_perc > SPINNING_TOP_MIN:
            if row.body_perc < HANGING_MAN_BODY:
                return True
    return False

# Règle pour les avalements (le corps du chandelier du jour couvre complètement celui du jour précédent)
# Bullish engulfing (Avalement haussier) : Rouge-vert implique une tendance haussière
# Bearish engulfing (Avalement baissier) : Vert-rouge implique une tendance baissière
def apply_engulfing(row):
    if row.direction != row.direction_prev:
        if row.body_size > row.body_size_prev * ENGULFING_FACTOR:
#       Pour le Harami
#       if row.body_size < row.body_size_prev * ENGULFING_FACTOR:
            return True
    return False
# La similitude d'un avalement est un Harami (le corps du jour est complètement recouvert par celui du jour précédent)
# Si on a rouge-vert le Harami est haussier
# Si on a vert-rouge le Harami est baissier


# Règle pour les tweezer (2 chandeliers successifs de corps presque identiques)
# Si les 2 chandeliers sont vert-rouge future tendance baissière
# Si les 2  chandeliers sont rouge-vert future tendance haussière
def apply_tweezer_top(row):
#   La variation du corps doit être inférieure à 15%
    if abs(row.body_size_change) < TWEEZER_BODY:
#       Le chandelier actuele doit être rouge et le précédent doit être de couleur différente
        if row.direction == -1 and row.direction != row.direction_prev:
#           Les variations entre les extremités doit être faible
            if abs(row.low_change) < TWEEZER_HL and abs(row.high_change) < TWEEZER_HL:
#                 L'extremité supérieure du corps doit être à moins de 40% du chandelier
                if row.body_top_perc < TWEEZER_TOP_BODY:
                    return True 
    return False 

def apply_tweezer_bottom(row):
#   La variation du corps doit être inférieure à 15%
    if abs(row.body_size_change) < TWEEZER_BODY:
#       Le chandelier actuele doit être vert et le précédent doit être de couleur différente
        if row.direction == 1 and row.direction != row.direction_prev:
#           Les variations entre les extremités doit être faible
            if abs(row.low_change) < TWEEZER_HL and abs(row.high_change) < TWEEZER_HL:
#                 L'extremité inférieure du corps doit être à plus de 60% du chandelier
                if row.body_bottom_perc > TWEEZER_BOTTOM_BODY:
                    return True 
    return False 



def apply_morning_star(row, direction=1):
#   le corps du 3e dernier chandelier doit être supérieur à 90% du chandelier
    if row.body_perc_prev2 > MORNING_STAR_PREV2_BODY:
#       Le corps du 2e dernier chandelier doit etre inférieur à 10% du chandelier
        if row.body_perc_prev < MORNING_STAR_PREV_BODY:
#           Le dernier et le 3e dernier chandelier doivent être de couleur différente
            if row.direction == direction and row.direction_prev2 != direction:
#               Si le dernier chandelier est vert il faut que le haut de son corps (close) soit au dessus de la moitié du 3e dernier chandelier (mornnig)
                if direction == 1:
                    if row.mid_c > row.mid_point_prev_2:
                        return True
#               Si le dernier chandelier est rouge il faut que le bas de son corps (close) soit en dessous de la moitié du 3e dernier chandelier (evening)
                else:
                    if row.mid_c < row.mid_point_prev_2:
                        return True
    return False 

def apply_candle_props(df: pd.DataFrame):
    df_an = df.copy()
    direction = df_an.mid_c - df_an.mid_o
    body_size = abs(direction)
    direction = [1 if x >= 0 else -1 for x in direction]
    full_range = df_an.mid_h - df_an.mid_l
    body_perc = (body_size / full_range) * 100

    # On récupère la valeur max(upper) ou min(lower) entre le close ou le open
    body_lower = df_an[['mid_c', 'mid_o']].min(axis=1)
    body_upper = df_an[['mid_c', 'mid_o']].max(axis=1)
    # On calcule pourcentage du top et du bottom du corps
    body_bottom_perc = ((body_lower - df_an.mid_l) / full_range) * 100
    body_top_perc = ((df_an.mid_h - body_lower) / full_range) * 100
    # On calcule le pourcentage de changement de valeur entre les extremités respectifs des corps pour les chandeliers consécutifs
    low_change = df_an.mid_l.pct_change() * 100
    high_change = df_an.mid_h.pct_change() * 100
    # On calcule le pourcentage de variation de taille des corps des chandeliers consécutifs
    body_size_change = body_size.pct_change() * 100
    # Calcul de la valeur moyenne du chandelier
    mid_point = full_range / 2 + df_an.mid_l

    # On crée de nouvelles colonnes dans le dataframe qui serviront pour les calculs
    df_an['body_lower'] = body_lower
    df_an['body_upper'] = body_upper
    df_an['body_bottom_perc'] = body_bottom_perc
    df_an['body_top_perc'] = body_top_perc
    df_an['body_perc'] = body_perc
    df_an['direction'] = direction
    df_an['body_size'] = body_size
    df_an['low_change'] = low_change
    df_an['high_change'] = high_change
    df_an['body_size_change'] = body_size_change
    df_an['mid_point'] = mid_point
    df_an['mid_point_prev_2'] = mid_point.shift(2)
    
    # On utilise shift pour créer une colonne à partir de l'avant-dernière valeur d'une colonne
    df_an['body_size_prev'] =  df_an.body_size.shift(1)
    df_an['direction_prev'] =  df_an.direction.shift(1)
    df_an['direction_prev2'] =  df_an.direction.shift(2)
    df_an['body_perc_prev'] =  df_an.body_perc.shift(1)
    df_an['body_perc_prev2'] =  df_an.body_perc.shift(2)

    return df_an

def set_candle_patterns(df_an: pd.DataFrame):
    # La méthode apply prend en entrée une fonction qui agit sur chaque ligne ou colonne
    df_an['HANGING_MAN'] = df_an.apply(apply_hanging_man, axis=1)
    df_an['SHOOTING_STAR'] = df_an.apply(apply_shooting_star, axis=1)
    df_an['SPINNING_TOP'] = df_an.apply(apply_spinning_top, axis=1)
    df_an['MARUBOZU'] = df_an.apply(apply_marubozu, axis=1)
    df_an['ENGULFING'] = df_an.apply(apply_engulfing, axis=1)
    df_an['TWEEZER_TOP'] = df_an.apply(apply_tweezer_top, axis=1)
    df_an['TWEEZER_BOTTOM'] = df_an.apply(apply_tweezer_bottom, axis=1)
    df_an['MORNING_STAR'] = df_an.apply(apply_morning_star, axis=1)
    df_an['EVENING_STAR'] = df_an.apply(apply_morning_star, axis=1, direction=-1)

def apply_patterns(df: pd.DataFrame):
    df_an = apply_candle_props(df)
    set_candle_patterns(df_an)
    return df_an