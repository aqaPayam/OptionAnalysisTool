import re

input_text = """
[
    {
        "isin": "IROFIKCO9Q51",
        "symbol": "طخود1239",
        "title": "اختیارف خودرو-4500-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9Q61",
        "symbol": "طخود1240",
        "title": "اختیارف خودرو-5000-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9Q71",
        "symbol": "طخود0142",
        "title": "اختیارف خودرو-5000-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9L01",
        "symbol": "طخود1226",
        "title": "اختیارف خودرو-1700-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9L11",
        "symbol": "طخود1227",
        "title": "اختیارف خودرو-1800-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9L21",
        "symbol": "طخود1228",
        "title": "اختیارف خودرو-1900-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9L31",
        "symbol": "طخود1229",
        "title": "اختیارف خودرو-2000-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9L41",
        "symbol": "طخود1230",
        "title": "اختیارف خودرو-2200-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9L51",
        "symbol": "طخود1231",
        "title": "اختیارف خودرو-2400-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9L61",
        "symbol": "طخود1232",
        "title": "اختیارف خودرو-2600-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9L71",
        "symbol": "طخود1233",
        "title": "اختیارف خودرو-2800-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9L81",
        "symbol": "طخود1234",
        "title": "اختیارف خودرو-3000-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9L91",
        "symbol": "طخود1235",
        "title": "اختیارف خودرو-3250-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9M01",
        "symbol": "طخود1236",
        "title": "اختیارف خودرو-3500-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9M11",
        "symbol": "طخود1237",
        "title": "اختیارف خودرو-3750-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9M21",
        "symbol": "طخود1238",
        "title": "اختیارف خودرو-4000-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9M31",
        "symbol": "طخود0126",
        "title": "اختیارف خودرو-1500-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9M41",
        "symbol": "طخود0127",
        "title": "اختیارف خودرو-1600-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9M51",
        "symbol": "طخود0128",
        "title": "اختیارف خودرو-1700-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9M61",
        "symbol": "طخود0129",
        "title": "اختیارف خودرو-1800-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9M71",
        "symbol": "طخود0130",
        "title": "اختیارف خودرو-1900-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9M81",
        "symbol": "طخود0131",
        "title": "اختیارف خودرو-2000-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9M91",
        "symbol": "طخود0132",
        "title": "اختیارف خودرو-2200-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9N01",
        "symbol": "طخود0133",
        "title": "اختیارف خودرو-2400-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9N11",
        "symbol": "طخود0134",
        "title": "اختیارف خودرو-2600-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9N21",
        "symbol": "طخود0135",
        "title": "اختیارف خودرو-2800-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9N31",
        "symbol": "طخود0136",
        "title": "اختیارف خودرو-3000-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9N41",
        "symbol": "طخود0137",
        "title": "اختیارف خودرو-3250-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9N51",
        "symbol": "طخود0138",
        "title": "اختیارف خودرو-3500-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9N61",
        "symbol": "طخود2050",
        "title": "اختیارف خودرو-2000-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9N71",
        "symbol": "طخود2051",
        "title": "اختیارف خودرو-2200-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9N81",
        "symbol": "طخود2052",
        "title": "اختیارف خودرو-2400-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9N91",
        "symbol": "طخود2053",
        "title": "اختیارف خودرو-2600-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9O11",
        "symbol": "طخود2054",
        "title": "اختیارف خودرو-2800-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9O21",
        "symbol": "طخود2055",
        "title": "اختیارف خودرو-3000-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9O31",
        "symbol": "طخود2056",
        "title": "اختیارف خودرو-3250-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9O41",
        "symbol": "طخود2057",
        "title": "اختیارف خودرو-3500-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9O51",
        "symbol": "طخود2058",
        "title": "اختیارف خودرو-3750-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9O61",
        "symbol": "طخود2059",
        "title": "اختیارف خودرو-4000-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9O71",
        "symbol": "طخود2060",
        "title": "اختیارف خودرو-4500-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9O81",
        "symbol": "طخود2061",
        "title": "اختیارف خودرو-5000-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9O91",
        "symbol": "طخود0139",
        "title": "اختیارف خودرو-3750-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9P01",
        "symbol": "طخود0140",
        "title": "اختیارف خودرو-4000-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9P11",
        "symbol": "طخود0141",
        "title": "اختیارف خودرو-4500-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9P21",
        "symbol": "طخود3089",
        "title": "اختیارف خودرو-2400-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9P31",
        "symbol": "طخود3090",
        "title": "اختیارف خودرو-2600-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9P41",
        "symbol": "طخود3091",
        "title": "اختیارف خودرو-2800-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9P51",
        "symbol": "طخود3092",
        "title": "اختیارف خودرو-3000-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9P61",
        "symbol": "طخود3093",
        "title": "اختیارف خودرو-3250-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9P71",
        "symbol": "طخود3094",
        "title": "اختیارف خودرو-3500-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9P81",
        "symbol": "طخود3095",
        "title": "اختیارف خودرو-3750-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9P91",
        "symbol": "طخود3096",
        "title": "اختیارف خودرو-4000-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9Q01",
        "symbol": "طخود3097",
        "title": "اختیارف خودرو-4500-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9Q11",
        "symbol": "طخود3098",
        "title": "اختیارف خودرو-5000-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IROFIKCO9Q21",
        "symbol": "طخود3099",
        "title": "اختیارف خودرو-5500-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8Q51",
        "symbol": "ضخود1239",
        "title": "اختیارخ خودرو-4500-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8Q61",
        "symbol": "ضخود1240",
        "title": "اختیارخ خودرو-5000-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8Q71",
        "symbol": "ضخود0142",
        "title": "اختیارخ خودرو-5000-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8P21",
        "symbol": "ضخود3089",
        "title": "اختیارخ خودرو-2400-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8P31",
        "symbol": "ضخود3090",
        "title": "اختیارخ خودرو-2600-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8P41",
        "symbol": "ضخود3091",
        "title": "اختیارخ خودرو-2800-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8P51",
        "symbol": "ضخود3092",
        "title": "اختیارخ خودرو-3000-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8P61",
        "symbol": "ضخود3093",
        "title": "اختیارخ خودرو-3250-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8P71",
        "symbol": "ضخود3094",
        "title": "اختیارخ خودرو-3500-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8P81",
        "symbol": "ضخود3095",
        "title": "اختیارخ خودرو-3750-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8P91",
        "symbol": "ضخود3096",
        "title": "اختیارخ خودرو-4000-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8Q01",
        "symbol": "ضخود3097",
        "title": "اختیارخ خودرو-4500-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8Q11",
        "symbol": "ضخود3098",
        "title": "اختیارخ خودرو-5000-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8Q21",
        "symbol": "ضخود3099",
        "title": "اختیارخ خودرو-5500-1404/03/07",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8O91",
        "symbol": "ضخود0139",
        "title": "اختیارخ خودرو-3750-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8P01",
        "symbol": "ضخود0140",
        "title": "اختیارخ خودرو-4000-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8P11",
        "symbol": "ضخود0141",
        "title": "اختیارخ خودرو-4500-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8L01",
        "symbol": "ضخود1226",
        "title": "اختیارخ خودرو-1700-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8L11",
        "symbol": "ضخود1227",
        "title": "اختیارخ خودرو-1800-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8L21",
        "symbol": "ضخود1228",
        "title": "اختیارخ خودرو-1900-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8L31",
        "symbol": "ضخود1229",
        "title": "اختیارخ خودرو-2000-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8L41",
        "symbol": "ضخود1230",
        "title": "اختیارخ خودرو-2200-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8L51",
        "symbol": "ضخود1231",
        "title": "اختیارخ خودرو-2400-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8L61",
        "symbol": "ضخود1232",
        "title": "اختیارخ خودرو-2600-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8L71",
        "symbol": "ضخود1233",
        "title": "اختیارخ خودرو-2800-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8L81",
        "symbol": "ضخود1234",
        "title": "اختیارخ خودرو-3000-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8L91",
        "symbol": "ضخود1235",
        "title": "اختیارخ خودرو-3250-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8M01",
        "symbol": "ضخود1236",
        "title": "اختیارخ خودرو-3500-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8M11",
        "symbol": "ضخود1237",
        "title": "اختیارخ خودرو-3750-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8M21",
        "symbol": "ضخود1238",
        "title": "اختیارخ خودرو-4000-1403/12/01",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8N61",
        "symbol": "ضخود2050",
        "title": "اختیارخ خودرو-2000-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8N71",
        "symbol": "ضخود2051",
        "title": "اختیارخ خودرو-2200-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8N81",
        "symbol": "ضخود2052",
        "title": "اختیارخ خودرو-2400-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8N91",
        "symbol": "ضخود2053",
        "title": "اختیارخ خودرو-2600-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8O11",
        "symbol": "ضخود2054",
        "title": "اختیارخ خودرو-2800-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8O21",
        "symbol": "ضخود2055",
        "title": "اختیارخ خودرو-3000-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8O31",
        "symbol": "ضخود2056",
        "title": "اختیارخ خودرو-3250-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8O41",
        "symbol": "ضخود2057",
        "title": "اختیارخ خودرو-3500-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8O51",
        "symbol": "ضخود2058",
        "title": "اختیارخ خودرو-3750-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8O61",
        "symbol": "ضخود2059",
        "title": "اختیارخ خودرو-4000-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8O71",
        "symbol": "ضخود2060",
        "title": "اختیارخ خودرو-4500-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8O81",
        "symbol": "ضخود2061",
        "title": "اختیارخ خودرو-5000-1404/02/03",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8M31",
        "symbol": "ضخود0126",
        "title": "اختیارخ خودرو-1500-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8M41",
        "symbol": "ضخود0127",
        "title": "اختیارخ خودرو-1600-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8M51",
        "symbol": "ضخود0128",
        "title": "اختیارخ خودرو-1700-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8M61",
        "symbol": "ضخود0129",
        "title": "اختیارخ خودرو-1800-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8M71",
        "symbol": "ضخود0130",
        "title": "اختیارخ خودرو-1900-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8M81",
        "symbol": "ضخود0131",
        "title": "اختیارخ خودرو-2000-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8M91",
        "symbol": "ضخود0132",
        "title": "اختیارخ خودرو-2200-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8N01",
        "symbol": "ضخود0133",
        "title": "اختیارخ خودرو-2400-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8N11",
        "symbol": "ضخود0134",
        "title": "اختیارخ خودرو-2600-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8N21",
        "symbol": "ضخود0135",
        "title": "اختیارخ خودرو-2800-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8N31",
        "symbol": "ضخود0136",
        "title": "اختیارخ خودرو-3000-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8N41",
        "symbol": "ضخود0137",
        "title": "اختیارخ خودرو-3250-1404/01/06",
        "matketCap": 0
    },
    {
        "isin": "IRO9IKCO8N51",
        "symbol": "ضخود0138",
        "title": "اختیارخ خودرو-3500-1404/01/06",
        "matketCap": 0
    }
]
"""

symbol_mapping = {
    "ضخود": "zakhod",
    "طخود": "takhod"
}

class_template = """
class {class_name}(BaseConfig):
    OPTION_NAME = "{option_name}"
    OPTION_TICKER = "{option_ticker}"
    EXPIRATION_DATE = "{expiration_date}"
    STRIKE_PRICE = {strike_price}
    CALL_PUT = '{call_put}'  # 'c' for call (kharid), 'p' for put (forosh)
"""


def transliterate_symbol(symbol):
    """Converts Persian symbol names to English transliterations."""
    for persian, english in symbol_mapping.items():
        if symbol.startswith(persian):
            return symbol.replace(persian, english, 1)
    return symbol  # Return as is if no match


def extract_options(text):
    """Extracts option details from the input text and generates class definitions."""
    pattern = re.compile(r'"isin":\s*"([^"]+)",\s*"symbol":\s*"([^"]+)",\s*"title":\s*"([^"]+)"')
    matches = pattern.findall(text)

    class_definitions = []
    config_mappings = []

    for isin, symbol, title in matches:
        match = re.search(r"اختیار([خ|ف]) خودرو-(\d+)-(\d{4}/\d{2}/\d{2})", title)
        if match:
            call_put = 'c' if match.group(1) == "خ" else 'p'  # 'خ' (kharid) = Call, 'ف' (forosh) = Put
            strike_price = int(match.group(2))
            expiration_date = match.group(3).replace("/", "-")

            eng_symbol = transliterate_symbol(symbol)  # Convert Persian to English
            class_name = f"Option_{eng_symbol}"  # Generate class name in English

            class_definitions.append(class_template.format(
                class_name=class_name,
                option_name=eng_symbol,
                option_ticker=isin,
                expiration_date=expiration_date,
                strike_price=strike_price,
                call_put=call_put
            ))

            # Adding to CONFIGS dictionary
            config_mappings.append(f"    '{eng_symbol}': {class_name},")

    # Generate CONFIGS dictionary
    configs_code = "\n# Map modes to configurations\nCONFIGS = {\n" + "\n".join(config_mappings) + "\n}"

    return "\n".join(class_definitions) + "\n" + configs_code


def main():
    """Main function to process the input text and generate class definitions."""
    generated_code = extract_options(input_text)
    print(generated_code)


if __name__ == "__main__":
    main()
