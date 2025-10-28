import os

AA_DATA_DIR = os.getenv("AA_DATA_DIR") 

highlight_cells = [(2023, "April"),(2024, "January")]

capital_districts = [
    "Maputo Cidade",
    "Quelim",
    "Cidade de Tete",
    "Beira",
    "Nampula",
    "Lichinga",
    "Matola",
    "Cidade de Pemba",
    "Cidade de Xai Xai",
    "Cidade de Inhambane",
    "Cidade de Chimoio",
]

month_order = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

capitals_threshold = 300
default_threshold = 100
trend_threshold = 0
number_of_districts = 2

district_case_limit = 1500
province_case_limit = 2500

# setting both of these to zero for now
winsorising_lower_limit = 0
winsorising_upper_limit = 0