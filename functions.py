import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None
import matplotlib.pyplot as plt
import seaborn as sns

# import geopandas as gpd
# import geodatasets as gds

from thefuzz import fuzz
from thefuzz import process
import re


def clean_cols(col) :
    """
    Takes a Series as argument, strips it off its whitespaces and capitalizes it.
    """
    col = col.strip()
    col = col.title()
    return col


def fix_m(n) :
    """
    Takes a three-value long string and transforms it into an appropriate month number.
    """
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    n = process.extractOne(n, months, scorer=fuzz.partial_ratio)[0]
    m_numbers = {months[x] : ("0" + str(x + 1) if x < 9 else str(x + 1)) for x in range(12)}
    for m in m_numbers :
        if n == m :
            n = m_numbers[m]
    return n


def clean_date(date) :
    """
    Takes a Series as argument, cleans it.
    """
    check = re.findall("\d\d.\D\D{3}\d{4}|\d\d.\D\D{3}|\d{4}", str(date))
    if check :
        try :
            check = check[0].replace(" ", "-")
            month = re.findall("[a-zA-Z]{3}", str(check))[0]
            month_new = fix_m(month)
            check = check.replace(month, str(month_new))
            check = f"{check[:2]}-{check[3 :5]}-{check[6 :]}"
        except IndexError :
            if check == "1018" :
                check = "2018"
            elif check >= "2024" :
                check = "1959"
            return str(check)
        else :
            return str(check)
    else :
        return ""


def clean_type(type) :
    """

    """
    type_dict = {"Unprovoked" : "Unprovoked",
                 "Provoked" : "Provoked",
                 "Invalid" : "Invalid",
                 "Watercraft" : "Watercraft",
                 "Sea Disaster" : "Sea_Disaster",
                 "Questionable" : "Invalid",
                 "Boat" : "Watercraft",
                 " Provoked" : "Provoked",
                 "?" : "Invalid",
                 "Unconfirmed" : "Invalid",
                 "Unverified" : "Invalid",
                 "Under investigation" : "Invalid", }
    return type.map(type_dict)


def clean_ctr(ctr) :
    """

    """
    ctr = str(ctr).title().strip()
    ctr = ctr.replace("?", "").replace("(Uae)", "").replace("St ", "St. ")
    if ctr == "Iran / Iraq" :
        ctr = "Iran"
    elif ctr == "Ceylon (Sri Lanka)" :
        ctr = "Sri Lanka"
    return ctr


def extract_m(m) :
    """

    """
    m = m.map(lambda x : re.findall("-..-", str(x))[0].replace("-", "") if len(str(x)) > 4 else x)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    m_num2 = {"0" + str(x + 1) : months[x] for x in range(12)}
    return m.map(m_num2)


def normalise_sex(df) :
    sex_mapping = {
        'M' : 'M',
        'F' : 'F',
        ' M' : 'M',
        'M ' : 'M',
        'lli' : 'M',
        'M x 2' : 'M',
        '.' : 'U',
    }

    df["Sex"] = df["Sex"].map(sex_mapping)
    df["Sex"] = df["Sex"].map(sex_mapping).fillna('U')
    return df


def get_activity(activity) :
    # Breakdown activities by category
    unknown_activities = {
        'Murder',
        'Suicide',
        'UN',
        'Unknown',
        'male',
        'Hilo',
        'Filming',
        'Rescuing',
        'Shipwreck',
        'Shipwrecked',
        'Sightseeing'
    }

    diving_activites = {
        'Skindiving',
        'Snorkeling',
        'Diving'
    }

    boating_activities = {
        'Boat',
        'Boating',
        'Canoeing',
        'Kayaking',
        'Paddleboarding',
        'Paddleskiing',
        'Rowing',
        'Sailing',
        'Wakeboarding',
        'Watercraft',
        'Parasailing'
    }

    swimming_and_bathing_activities = {
        'Bather',
        'Bathing',
        'Sitting',
        'Splashing',
        'Stamding',
        'Standing',
        'Washing',
        'Swimming',
        'Swimmingq',
        'Swmming',
        'Playing',
        'Jumping'
    }

    surfing_activities = {
        'Bodyboarding',
        'Bodysurfing',
        'Foilboarding',
        'Kiteboarding',
        'Kitesurfing',
        'Skimboarding',
        'Surfing',
        'Windsurfing'
    }

    fishing_activities = {
        'Angling',
        'Crabbing',
        'Crawling',
        'Crayfishing',
        'Fishing',
        'Fishingat',
        'Lobstering',
        'Oystering',
        'Spearfishing',
        'Spearishing',
        'Shrimping',
        'Batin'
    }

    if activity == 'Undisclosed' :
        return 'Undisclosed'

    activity = activity.lower()

    for i in diving_activites :
        if fuzz.partial_ratio(i.lower(), activity) > 75 :
            return 'Diving'

    for i in boating_activities :
        if fuzz.partial_ratio(i.lower(), activity) > 75 :
            return 'Boating'

    for i in swimming_and_bathing_activities :
        if fuzz.partial_ratio(i.lower(), activity) > 75 :
            return 'Swimming/Bathing'

    for i in surfing_activities :
        if fuzz.partial_ratio(i.lower(), activity) > 75 :
            return 'Surfing'

    for i in fishing_activities :
        if fuzz.partial_ratio(i.lower(), activity) > 75 :
            return 'Fishing'

    return 'Not categorised'


def get_species(x) :
    species_list = [
        ("Tiger Shark", ["tiger", "tiger shark", "tigerr"]),
        ("Bull Shark", ["bull"]),
        ("Blacktip Shark", ["blacktip", "blacktip shark", "bluacktip"]),
        ("White Shark", ["white", "whale"]),
        ("Raggedtooth Shark", ["raggedtooth", "sandtiger"]),
        ("Sevengill Shark", ["sevengill"]),
        ("Lemon Shark", ["lemon"]),
        ("Oceanic Whitetip Shark", ["oceanic", "oceanic whitetip", "oceaniic"]),
        ("Nurse Shark", ["nurse"]),
        ("Cookiecutter Shark", ["cookiecutter"]),
        ("Blue Shark", ["blue"]),
        ("Wobbegong Shark", ["wobbegong"]),
        ("Caribbean Reef Shark", ["caribbean", "reef"]),
        ("Grey Nurse Shark", ["grey"]),
        ("Bronze Whaler Shark", ["bronze", "bronz"]),
        ("Mako Shark", ["mako"]),
        ("Spinner Shark", ["spinner"]),
        ("Galapagos Shark", ["galapagos"]),
        ("Tope Shark", ["tope"]),
        ("Epaulette Shark", ["epaulette"]),
        ("Angel Shark", ["angel"]),
        ("Reef Shark", ["reef"]),
        ("Silky Shark", ["silky"]),
        ("Thresher Shark", ["thresher"]),
        ("Hammerhead Shark", ["hammerhead"]),
        ("Shovelnose Shark", ["shovelnose"]),
        ("Tawny Shark", ["tawny"]),
        ("Dogfish Shark", ["dogfish"])
    ]

    x = x.lower()
    for species, variations in species_list :
        species = species.lower()
        for variation in variations :
            if fuzz.partial_ratio(variation.lower(), x) > 70 :
                return species.capitalize()
    return 'Other'


def normalize_injury(df) :
    df["Injury"] = df["Injury"].apply(lambda x : "Fatal" if isinstance(x, str) and "fatal" in x.lower() else x)
    df["Injury"] = df["Injury"].apply(lambda x : "Severe" if isinstance(x, str) and "bitten" in x.lower() else x)
    df["Injury"] = df["Injury"].apply(lambda x : "Severe" if isinstance(x, str) and "broken" in x.lower() else x)
    df["Injury"] = df["Injury"].apply(lambda x : "Severe" if isinstance(x, str) and "lost" in x.lower() else x)
    df["Injury"] = df["Injury"].apply(lambda x : "Severe" if isinstance(x, str) and "severe" in x.lower() else x)
    df["Injury"] = df["Injury"].apply(lambda x : "Moderate" if isinstance(x, str) and "lacerations" in x.lower() else x)
    df["Injury"] = df["Injury"].apply(lambda x : "Minor" if isinstance(x, str) and "minor" in x.lower() else x)
    df["Injury"] = df["Injury"].apply(lambda x : "Moderate" if isinstance(x, str) and "laceration" in x.lower() else x)
    df["Injury"] = df["Injury"].apply(
        lambda x : "No injury sustained" if isinstance(x, str) and "no injury" in x.lower() else x)
    df["Injury"] = df["Injury"].apply(lambda x : "Unknown" if isinstance(x, str) and "no details" in x.lower() else x)
    df["Injury"] = df["Injury"].apply(
        lambda x : "Unclassified" if x not in ["Fatal", "Severe", "Moderate", "Minor", "No injury sustained",
                                               "Unknown"] else x)
    return df


def classify_size(length) :
    try :
        length = float(length)
        if length > 3.0 :
            return "Large"
        elif 1.5 <= length <= 3.0 :
            return "Medium"
        else :
            return "Small"
    except ValueError :
        return "Unknown"


def get_time(x) :
    if x == 'Unknown' :
        return x

    try :
        x = str(x)
        x = x.split('h')[0]
        x = int(x)

        if x > 23 :
            x = int(x / 100)

        time_ranges = {
            'Morning' : (6, 11),  # '06:00', '11:59'
            'Afternoon' : (12, 17),  # '12:00', '17:59'
            'Evening' : (18, 21),  # '18:00', '21:59'
        }

        for t_range, (start, end) in time_ranges.items() :
            if start <= x <= end :
                return t_range

        if (22 <= x <= 24) | (0 <= x <= 5) :
            return 'Night'

        return None

    except :
        time_ranges = ['Morning', 'Afternoon', 'Evening', 'Night']

        for t_range in time_ranges :
            if fuzz.partial_ratio(t_range, x) > 70 :
                return t_range

        return None

def name_unknown(df):
    df['Name'] = np.where(df['Name'].isin(['male', 'female']), 'Unknown ' + df['Name'], df['Name'])
    df['Name'] = df['Name'].replace('', 'Unknown').fillna('Unknown')
    return df
