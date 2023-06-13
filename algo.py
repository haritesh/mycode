import time
import json
import os
import sys
import pyfiglet
from urllib.parse import urlparse, parse_qs
from fyers_api import fyersModel
import pandas as pd
from fyers_api import accessToken
import xlwings as ef
import xlwings as xw
import requests
import threading
from datetime import datetime, timedelta
from NorenRestApiPy.NorenApi import NorenApi
import pyotp
import logging
import pyotp

os.system("")

logging.basicConfig(filename="logger.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

username = "XP10554"  # fyers_id
password = "Xyxs2000@"  # fyers_password
pin = 2020  # your integer pin
client_id = "JTT7PPDTGP-100"  # "L9NY****W-100" (Client_id here refers to APP_ID of the created app)
secret_key = "54rgrfCKRFX"  # app_secret key which you got after creating the app
redirect_uri = "https://www.google.com/"  # redircet_uri you entered while creating APP.
app_id = client_id[:-4]  # "L9NY****W" (don't change this app_id variable)
client_id_1 = "JBT7CYDTGP-100:"  # "L9NY****W-100" (Client_id here refers to APP_ID of the created app)
# SHoonya Login Credentials
userid       = "FA7F454"
pwd          = "bdtas00@"

global signal
feed_opened = False
timeFrame = 68  # 5 sec coz dealy repsone of historical API
S5_factor = 1.642
S4_factor = 0.55
S3_factor = 0.275
R3_factor = 0.275
R4_factor = 0.55
R5_factor = 1.642
FB_factor = 0.20
FS_factor = 0.618
S5CESL_Factor = 20
S5PEBuy_Factor = 10
S5PETP_Factor = 50
R5PESL_Factor = 20
R5CESL_Factor = 20
R5CEBuy_Factor = 10
R5CETP_Factor = 50
global t1
i = 1
c = 0
flag = 1
global S5CE, S5BCE, S5TPCE, S5SLCE, S5PE, S5BPE, S5TPPE, S5SLPE, S4CE, S4BCE, S4TPCE, S4SLCE, S4PE, S4BPE, S4TPPE, S4SLPE, S3CE, S3BCE, S3TPCE, S3SLCE, S3PE, S3BPE, S3TPPE, S3SLPE, R3CE, R3BCE, R3TPCE, R3SLCE, R3PE, R3BPE, R3TPPE, R3SLPE, R4CE, R4BCE, R4TPCE, R4SLCE, R4PE, R4BPE, R4TPPE, R4SLPE, R5CE, R5BCE, R5TPCE, R5SLCE, R5PE, R5BPE, R5TPPE, R5SLPE
global cs_flag, pe_flag, ce_flag, no_trade, revert_flag, trade_book, PClose_1m, Close_1m, Time_1m, cost_price, sell_price, profit, loss, qty, lot_size, total_pnl, strike_ce_flag, strike_pe_flag, exit_type, PE_Symbol, CE_Symbol
pe_flag = 0
ce_flag = 0
cs_flag = 0
lot_size = 50
qty = 2 * lot_size
no_trade = 0
cost_price = 0
sell_price = 0
profit = 0
total_pnl = 0
strike_ce_flag = 0
strike_pe_flag = 0
PClose_1m = 0
Close_1m = 0
PE_Symbol = 0
CE_Symbol = 0

sheet = ef.Book(r"C:\Users\Aditya\PycharmProjects\Algo_Strategies\Camrilla_Pivot\embed.xlsm").sheets['Settings']
sheet1 = ef.Book(r"C:\Users\Aditya\PycharmProjects\Algo_Strategies\Camrilla_Pivot\embed.xlsm").sheets['Trade_Log']
workbook = ef.Book(r"C:\Users\Aditya\PycharmProjects\Algo_Strategies\Camrilla_Pivot\embed.xlsm")
sht_Login    = ef.Book(r"C:\Users\Aditya\PycharmProjects\Algo_Strategies\Camrilla_Pivot\embed.xlsm").sheets['Login Credentials']


FY_ID                  = sht_Login.range("B3").value
APP_ID                 = sht_Login.range("B4").value
SECRET_KEY             = sht_Login.range("B5").value
PIN                    = sht_Login.range("B6").value
TOTP_KEY               = sht_Login.range("B7").value
APP_TYPE               = "100"
client_id              = f'{APP_ID}-{APP_TYPE}'
APP_ID_TYPE            = "2"
REDIRECT_URI           = "https://www.google.com/"  # Redirect url from the app.
BASE_URL               = "https://api-t2.fyers.in/vagator/v2"
BASE_URL_2             = "https://api.fyers.in/api/v2"
URL_SEND_LOGIN_OTP     = BASE_URL + "/send_login_otp"  # /send_login_otp_v2
URL_VERIFY_TOTP        = BASE_URL + "/verify_otp"
URL_VERIFY_PIN         = BASE_URL + "/verify_pin"
URL_TOKEN              = BASE_URL_2 + "/token"
URL_VALIDATE_AUTH_CODE = BASE_URL_2 + "/validate-authcode"
SUCCESS                = 1
ERROR                  =-1


class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


class ShoonyaApiPy(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/', websocket='wss://api.shoonya.com/NorenWSTP/', eodhost='https://api.shoonya.com/chartApi/getdata/')

api = ShoonyaApiPy()

def setup():
    session = accessToken.SessionModel(client_id=client_id, secret_key=SECRET_KEY, redirect_uri=REDIRECT_URI, response_type='code', grant_type='authorization_code')
    send_otp_result = send_login_otp(fy_id=FY_ID, app_id=APP_ID_TYPE)
    # Step 1 - Retrieve request_key from send_login_otp API
    if send_otp_result[0] != SUCCESS:
        print(f"send_login_otp failure - {send_otp_result[1]}")
        sys.exit()
    else:
        print("")
        # print("send_login_otp success")
    # Step 2 - Verify totp and get request key from verify_otp API

    for i in range(1, 2):
        request_key = send_otp_result[1]
        verify_totp_result = verify_totp(request_key=request_key, totp=pyotp.TOTP(TOTP_KEY).now())
        if verify_totp_result[0] != SUCCESS:
            print(f"verify_totp_result failure - {verify_totp_result[1]}")
            time.sleep(1)
        else:
            # print(f"verify_totp_result success")
            break
    request_key_2 = verify_totp_result[1]
    # Step 3 - Verify pin and send back access token
    ses = requests.Session()
    payload_pin = {"request_key": f"{request_key_2}", "identity_type": "pin", "identifier": f"{PIN}", "recaptcha_token": ""}
    res_pin = ses.post('https://api-t2.fyers.in/vagator/v2/verify_pin', json=payload_pin).json()
    # print(res_pin['data'])
    ses.headers.update({
        'authorization': f"Bearer {res_pin['data']['access_token']}"
    })
    authParam = {"fyers_id": FY_ID, "app_id": APP_ID, "redirect_uri": REDIRECT_URI, "appType": APP_TYPE, "code_challenge": "", "state": "None", "scope": "", "nonce": "", "response_type": "code", "create_cookie": True}
    authres = ses.post('https://api.fyers.in/api/v2/token', json=authParam).json()
    # print(authres)
    url = authres['Url']
    # print(url)
    parsed = urlparse(url)
    auth_code = parse_qs(parsed.query)['auth_code'][0]
    session.set_token(auth_code)
    response = session.generate_token()
    access_token = response["access_token"]
    write_file(access_token)
    sht_Login.range("B8").value = access_token

    # print("ACCESS TOKEN",access_token)
    fyers = fyersModel.FyersModel(client_id=client_id, token=read_file(), log_path=os.getcwd())
    profile = (fyers.get_profile())

    df = pd.DataFrame(profile['data'], index=[0]).transpose()
    df.columns = ['']
    print(df.to_string())
    for i in range(38):
        print(">", end="", flush=True)
        time.sleep(0.1)
    print(style.YELLOW, "")
    word = "Logged in successfully"
    for char in word:
        print(char, end="", flush=True)
        time.sleep(0.1)
    print(style.CYAN, "")
    for i in range(38):
        print(">", end="", flush=True)
        time.sleep(0.1)
    print("")

def read_file1():
    with open("tokenf.txt", "r") as f:
        token = f.read()
    return token

def write_file1(token):
    with open("tokenf.txt", "w") as f:
        f.write(token)
def send_login_otp(fy_id, app_id):
    try:
        result_string = requests.post(url=URL_SEND_LOGIN_OTP, json={"fy_id": fy_id, "app_id": app_id})
        if result_string.status_code != 200:
            return [ERROR, result_string.text]
        result      = json.loads(result_string.text)
        request_key = result["request_key"]
        return [SUCCESS, request_key]
    except Exception as e:
        return [ERROR, e]
def verify_totp(request_key, totp):
    try:
        result_string = requests.post(url=URL_VERIFY_TOTP, json={"request_key": request_key, "otp": totp})
        if result_string.status_code != 200:
            return [ERROR, result_string.text]
        result      = json.loads(result_string.text)
        request_key = result["request_key"]
        return [SUCCESS, request_key]
    except Exception as e:
        return [ERROR, e]
def read_file():
    with open("tokenf.txt", "r") as f:
        token = f.read()
    return token

def read_file_f():
    with open(r"C:\Users\Aditya\PycharmProjects\Algo_Strategies\Straddle_FINVASIA_New\tokenf.txt", "r") as f:
        token = f.read()
    return token
def write_file(token):
    with open("tokenf.txt", "w") as f:
        f.write(token)




def get_1D_candel():
    global S5CE, S5BCE, S5TPCE, S5SLCE, S5PE, S5BPE, S5TPPE, S5SLPE, S4CE, S4BCE, S4TPCE, S4SLCE, S4PE, S4BPE, S4TPPE, S4SLPE, S3CE, S3BCE, S3TPCE, S3SLCE, S3PE, S3BPE, S3TPPE, S3SLPE, R3CE, R3BCE, R3TPCE, R3SLCE, R3PE, R3BPE, R3TPPE, R3SLPE, R4CE, R4BCE, R4TPCE, R4SLCE, R4PE, R4BPE, R4TPPE, R4SLPE, R5CE, R5BCE, R5TPCE, R5SLCE, R5PE, R5BPE, R5TPPE, R5SLPE
    global i, flag
    # try:
    try:
        token = read_file()
    except FileNotFoundError:
        print("Getting the access token!")
        setup()
        sys.exit()
    fyers = fyersModel.FyersModel(client_id=client_id, token=token, log_path=os.getcwd())
    lastdate = sheet.range('H46').value.strftime('%Y-%m-%d')
    data = {"symbol": "NSE:NIFTY50-INDEX", "resolution": "1D", "date_format": "1", "range_from": lastdate,
            "range_to": lastdate, "cont_flag": "1"}
    hd = fyers.history(data)
    print(hd)
    columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
    hd1 = pd.DataFrame(hd['candles'], columns=columns)
    hd2 = pd.DataFrame(hd1)
    hd2['Date'] = pd.to_datetime(hd1['Timestamp'], unit='s')
    #print(hd2)

    if hd2.empty:
        sheet.range('H48').value = i
        i = i + 1
        get_1D_candel()
    if flag == 1:

        O = hd2.values[0, 1]
        H = hd2.values[0, 2]
        L = hd2.values[0, 3]
        C = hd2.values[0, 4]

        print(style.RED, "Previous Day Candel Data:")
        print(style.GREEN,"Open:", round(O, 1))
        print(style.BLUE,"High:",round(H, 1))
        print(style.MAGENTA,"Low:",round(L, 1))
        print(style.YELLOW,"Close:",round(C, 1))
        print(style.RESET,)
        logger.info("Previous Day Candel Data: Open:%s ,High: %s, Low: %s, Close: %s", round(O, 1), round(H, 1), round(L, 1),round(C, 1))

        S3CE = C - (H - L) * S3_factor
        S4CE = C - (H - L) * S4_factor
        S5CE = S4CE + S5_factor * (S4CE - S3CE)
        S3PE = C - (H - L) * S3_factor
        S4PE = C - (H - L) * S4_factor
        S5PE = S4PE + S5_factor * (S4PE - S3PE)
        R3CE = C + (H - L) * R3_factor
        R4CE = C + (H - L) * R4_factor
        R5CE = R4CE + R5_factor * (R4CE - R3CE)
        R3PE = C + (H - L) * R3_factor
        R4PE = C + (H - L) * R4_factor
        R5PE = R4PE + R5_factor * (R4PE - R3PE)

        S3BCE = S3CE + ((R3CE - S3CE) * FB_factor)
        S4BCE = S4CE + ((S3CE - S4CE) * FB_factor)
        S5BCE = S5CE + ((S4CE - S5CE) * FB_factor)
        S3BPE = S3PE - ((S3PE - S4PE) * FB_factor)
        S4BPE = S4PE - ((S4PE - S5PE) * FB_factor)
        S5BPE = S5PE - S5PEBuy_Factor
        R3BCE = R3CE + ((R4CE - R3CE) * FB_factor)
        R4BCE = R4CE + ((R5CE - R4CE) * FB_factor)
        R5BCE = R5CE + R5CEBuy_Factor
        R3BPE = R3PE - ((R3PE - S3PE) * FB_factor)
        R4BPE = R4PE - ((R4PE - R3PE) * FB_factor)
        R5BPE = R5PE - ((R5PE - R4PE) * FB_factor)

        S3TPCE = S3CE + ((R3CE - S3CE) * FS_factor)
        S4TPCE = S4CE + ((S3CE - S4CE) * FS_factor)
        S5TPCE = S5CE + ((S4CE - S5CE) * FS_factor)
        S3TPPE = S3PE - ((S3PE - S4PE) * FS_factor)
        S4TPPE = S4PE - ((S4PE - S5PE) * FS_factor)
        S5TPPE = S5PE - S5PETP_Factor
        R3TPCE = R3CE + ((R4CE - R3CE) * FS_factor)
        R4TPCE = R4CE + ((R5CE - R4CE) * FS_factor)
        R5TPCE = R5CE + R5CETP_Factor
        R3TPPE = R3PE - ((R3PE - S3PE) * FS_factor)
        R4TPPE = R4PE - ((R4PE - R3PE) * FS_factor)
        R5TPPE = R5PE - ((R5PE - R4PE) * FS_factor)

        S3SLCE = S3CE - ((S3CE - S4CE) * FB_factor)
        S4SLCE = S4CE - ((S4CE - S5CE) * FB_factor)
        S5SLCE = S5CE - S5CESL_Factor
        S3SLPE = S3PE + ((R3PE - S3PE) * FB_factor)
        S4SLPE = S4PE + ((S3PE - S4PE) * FB_factor)
        S5SLPE = S5PE + ((S4PE - S5PE) * FB_factor)
        R3SLCE = R3CE - ((R3CE - S3CE) * FB_factor)
        R4SLCE = R4CE - ((R4CE - R3CE) * FB_factor)
        R5SLCE = R5CE - ((R5CE - R4CE) * FB_factor)
        R3SLPE = R3PE + ((R4PE - R3PE) * FB_factor)
        R4SLPE = R4PE + ((R5PE - R4PE) * FB_factor)
        R5SLPE = R5PE + R5PESL_Factor

        #print(S5CE, S5BCE, S5TPCE, S5SLCE, S5PE, S5BPE, S5TPPE, S5SLPE, S4CE, S4BCE, S4TPCE, S4SLCE, S4PE, S4BPE, S4TPPE, S4SLPE, S3CE, S3BCE, S3TPCE, S3SLCE, S3PE, S3BPE, S3TPPE, S3SLPE, R3CE, R3BCE, R3TPCE, R3SLCE, R3PE, R3BPE, R3TPPE, R3SLPE, R4CE, R4BCE, R4TPCE, R4SLCE, R4PE, R4BPE, R4TPPE, R4SLPE, R5CE, R5BCE, R5TPCE, R5SLCE, R5PE, R5BPE, R5TPPE, R5SLPE)
        Print_Levels()
        #print(S5CE, S4CE, S3CE, R3CE, R4CE, R5CE)

        flag = 1
        if flag == 1:
            flag = 0
    # except:
    #     print("error: 1D Candle, retrying..")
    #     get_1D_candel()

def Print_Levels():
    print(style.GREEN,"CALL Options")
    print(style.BLUE,'Pivot Levels :', 'S3:', round(S3CE,0 ),"| ",'S4:', round(S4CE,0 ),"| ",'S5:', round(S5CE,0 ),"| "'R3:', round(R3CE,0 ),"| ",'R4:', round(R4CE,0 ),"| ",'R5:', round(R5CE,0 ),"| ")
    print(style.GREEN,'BUY Level    :', 'S3:', round(S3BCE, 0), "| ", 'S4:', round(S4BCE, 0), "| ", 'S5:', round(S5BCE, 0), "| "'R3:', round(R3BCE, 0), "| ", 'R4:', round(R4BCE, 0), "| ", 'R5:', round(R5BCE, 0), "| ")
    print(style.CYAN, 'TGT Level    :', 'S3:', round(S3TPCE, 0), "| ", 'S4:', round(S4TPCE, 0), "| ", 'S5:', round(S5TPCE, 0), "| "'R3:', round(R3TPCE, 0), "| ", 'R4:', round(R4TPCE, 0), "| ", 'R5:', round(R5TPCE, 0), "| ")
    print(style.RED,'SL Level     :', 'S3:', round(S3SLCE, 0), "| ", 'S4:', round(S4SLCE, 0), "| ", 'S5:', round(S5SLCE, 0), "| "'R3:', round(R3SLCE, 0), "| ", 'R4:', round(R4SLCE, 0), "| ", 'R5:', round(R5SLCE, 0), "| ")
    print("")
    print(style.RED,"PUT Options")
    print(style.BLUE, 'Pivot Levels :', 'S3:', round(S3PE, 0), "| ", 'S4:', round(S4PE, 0), "| ", 'S5:', round(S5PE, 0), "| "'R3:', round(R3PE, 0), "| ", 'R4:', round(R4PE, 0), "| ", 'R5:', round(R5PE, 0), "| ")
    print(style.GREEN, 'BUY Level    :', 'S3:', round(S3BPE, 0), "| ", 'S4:', round(S4BPE, 0), "| ", 'S5:', round(S5BPE, 0), "| "'R3:', round(R3BPE, 0), "| ", 'R4:', round(R4BPE, 0), "| ", 'R5:', round(R5BPE, 0), "| ")
    print(style.CYAN, 'TGT Level    :', 'S3:', round(S3TPPE, 0), "| ", 'S4:', round(S4TPPE, 0), "| ", 'S5:', round(S5TPPE, 0), "| "'R3:', round(R3TPPE, 0), "| ", 'R4:', round(R4TPPE, 0), "| ", 'R5:', round(R5TPPE, 0), "| ")
    print(style.RED, 'SL Level     :', 'S3:', round(S3SLPE, 0), "| ", 'S4:', round(S4SLPE, 0), "| ", 'S5:', round(S5SLPE, 0), "| "'R3:', round(R3SLPE, 0), "| ", 'R4:', round(R4SLPE, 0), "| ", 'R5:', round(R5SLPE, 0), "| ")
    print("")

def get_1m_candel():
    global i, cs_flag, pe_flag, ce_flag, no_trade, revert_flag, trade_book, PClose_1m, Close_1m, Time_1m, c, t1
    try:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        if current_time > "09:14:00" and current_time < "15:30:00" :
            interval = timeFrame - datetime.now().second
            print(f"Code run after {interval} sec")
            for i in range(interval, 0, -1):
                time.sleep(1)
                #print("Waiting for Signal", i, datetime.now())
                #Print_Levels()
            time.sleep(1)
            token = read_file()
            fyers = fyersModel.FyersModel(client_id=client_id, token=token, log_path=os.getcwd())
            cdate = sheet.range('H47').value.strftime('%Y-%m-%d')
            data = {"symbol": "NSE:NIFTY50-INDEX", "resolution": "1", "date_format": "1", "range_from": cdate,
                    "range_to": cdate, "cont_flag": "1"}
            hd = fyers.history(data)
            columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
            hd1 = pd.DataFrame(hd['candles'], columns=columns)
            hd2 = pd.DataFrame(hd1)
            print(hd2)
            hd2['Date'] = pd.to_datetime(hd1['Timestamp'], unit='s') + timedelta(hours=5, minutes=30)
            # df2 = hd2[0::len(hd2) - 1 if len(hd2) > 1 else 1]
            PClose_1m = hd2.iloc[-2, 4]
            Close_1m = hd2.iloc[-1, 4]
            Date_1m = hd2.iloc[-1, 6].date()
            Time_1 = hd2.iloc[-1, 6].time()
            Time_1m = datetime.strptime(str(Time_1), '%H:%M:%S').strftime('%H:%M:%S')
            c = c + 1
            Print_Levels()
            print("Close Price & Date Time of last candle | Close:", Close_1m, "Date:", Date_1m, "Time:", Time_1m, "Candle No:", c, cs_flag, ce_flag, pe_flag)
        else:
            print("Waiting for Market to open | Current Time: ",datetime.now())
            time.sleep(1)
    except:
        print("Error:Awaiting Candel Data", datetime.now())

def trial_1m_candel():
    try:
        token = read_file()
    except FileNotFoundError:
        print("Getting the access token!")
        setup()
        sys.exit()
    fyers = fyersModel.FyersModel(client_id=client_id, token=token, log_path=os.getcwd())
    cdate = sheet.range('H47').value.strftime('%Y-%m-%d')
    data = {"symbol": "NSE:NIFTY50-INDEX", "resolution": "1", "date_format": "1", "range_from": cdate,
            "range_to": cdate, "cont_flag": "1"}
    hd = fyers.history(data)
    columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
    hd1 = pd.DataFrame(hd['candles'], columns=columns)
    hd2 = pd.DataFrame(hd1)
    hd2['Date'] = pd.to_datetime(hd1['Timestamp'], unit='s') + timedelta(hours=5, minutes=30)
    print(hd2)

def check_signal():
    global i, flag, c, cs_flag, no_trade, Close_1m, t1, Time_1m
    global S5CE, S5BCE, S5TPCE, S5SLCE, S5PE, S5BPE, S5TPPE, S5SLPE, S4CE, S4BCE, S4TPCE, S4SLCE, S4PE, S4BPE, S4TPPE, S4SLPE, S3CE, S3BCE, S3TPCE, S3SLCE, S3PE, S3BPE, S3TPPE, S3SLPE, R3CE, R3BCE, R3TPCE, R3SLCE, R3PE, R3BPE, R3TPPE, R3SLPE, R4CE, R4BCE, R4TPCE, R4SLCE, R4PE, R4BPE, R4TPPE, R4SLPE, R5CE, R5BCE, R5TPCE, R5SLCE, R5PE, R5BPE, R5TPPE, R5SLPE

    while True:
        # try:
            get_1m_candel()
            if Close_1m < R5PE and PClose_1m > R5PE and Time_1m > "09:20:00" and Time_1m < "15:15:00":
                print("R5 Cross Down")
                logger.info("R5 Cross Down-CS")
                cs_flag = 1
                R5_cross_down()
            if Close_1m < R4PE and PClose_1m > R4PE and Time_1m > "09:20:00" and Time_1m < "15:15:00":
                print("R4 Cross Down")
                logger.info("R4 Cross Down-CS")
                cs_flag = 1
                R4_cross_down()
            if Close_1m < R3PE and PClose_1m > R3PE and Time_1m > "09:20:00" and Time_1m < "15:15:00":
                print("R3 Cross Down")
                logger.info("R3 Cross Down-CS")
                cs_flag = 1
                R3_cross_down()
            if Close_1m < S3PE and PClose_1m > S3PE and Time_1m > "09:20:00" and Time_1m < "15:15:00":
                print("S3 Cross Down")
                logger.info("S3 Cross Down-CS")
                cs_flag = 1
                S3_cross_down()
            if Close_1m < S4PE and PClose_1m > S4PE and Time_1m > "09:20:00" and Time_1m < "15:15:00":
                print("S4 Cross Down")
                logger.info("S4 Cross Down-CS")
                cs_flag = 1
                S4_cross_down()
            if Close_1m < S5PE and PClose_1m > S5PE and Time_1m > "09:20:00" and Time_1m < "15:15:00":
                print("S5 Cross Down")
                logger.info("S5 Cross Down-CS")
                cs_flag = 1
                S5_cross_down()
            if Close_1m > S5CE and PClose_1m < S5CE and Time_1m > "09:20:00" and Time_1m < "15:15:00":
                print("S5 Cross Up")
                logger.info("S5 Cross Up-CS")
                cs_flag = 1
                S5_cross_up()
            if Close_1m > S4CE and PClose_1m < S4CE and Time_1m > "09:20:00" and Time_1m < "15:15:00":
                print("S4 Cross Up")
                logger.info("S4 Cross Up-CS")
                cs_flag = 1
                S4_cross_up()
            if Close_1m > S3CE and PClose_1m < S3CE and Time_1m > "09:20:00" and Time_1m < "15:15:00":
                print("S3 Cross Up")
                logger.info("S3 Cross Up-CS")
                cs_flag = 1
                S3_cross_up()
            if Close_1m > R3CE and PClose_1m < R3CE and Time_1m > "09:20:00" and Time_1m < "15:15:00":
                print("R3 Cross Up")
                logger.info("R3 Cross Up-CS")
                cs_flag = 1
                R3_cross_up()
            if Close_1m > R4CE and PClose_1m < R4CE and Time_1m > "09:20:00" and Time_1m < "15:15:00":
                print("R4 Cross Up")
                logger.info("R4 Cross Up-CS")
                cs_flag = 1
                R4_cross_up()
            if Close_1m > R5CE and PClose_1m < R5CE and Time_1m > "09:20:00" and Time_1m < "15:15:00":
                print("R5 Cross Up")
                logger.info("R5 Cross Up-CS")
                cs_flag = 1
                R5_cross_up()
        # except:
        #     print("Error :Candel data not available", datetime.now())
        #     logger.info("Error: Candel data  not available")

def quotes_buy():
    global c, pe_flag, ce_flag, cost_price, qty, total_pnl,signal

    sheet.range('Z7').value = "API"
    q = 19
    sheet.range('Z19').value = Close_1m
    token = read_file()
    fyers = fyersModel.FyersModel(client_id=client_id, token=token, log_path=os.getcwd())
    cdate = sheet.range('H47').value.strftime('%Y-%m-%d')
    symbol = sheet.range('B15').value
    data = {"symbol": symbol, "resolution": "1", "date_format": "1", "range_from": cdate,
            "range_to": cdate, "cont_flag": "0"}
    hd = fyers.history(data)
    print(hd)
    columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
    hd1 = pd.DataFrame(hd['candles'], columns=columns)
    hd2 = pd.DataFrame(hd1)
    hd2['Date'] = pd.to_datetime(hd1['Timestamp'], unit='s') + timedelta(hours=5, minutes=30)
    CE_Close_1m = hd2.iloc[-1, 4]
    CE_Date_1m = hd2.iloc[-1, 6].date()
    CE_Time_1 = hd2.iloc[-1, 6].time()
    print('Strike Price : ', CE_Close_1m, 'Date : ', CE_Date_1m, 'Time', CE_Time_1, 'Candel No. : ', c)
    logger.info('Strike Price :%s, Date :%s, Time :%s, Candel No. :%s', CE_Close_1m,  CE_Date_1m,  CE_Time_1,  c)
    symbol1 = sheet.range('B16').value
    data = {"symbol": symbol1, "resolution": "1", "date_format": "1", "range_from": cdate,
            "range_to": cdate, "cont_flag": "0"}
    hd = fyers.history(data)
    columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
    hd1 = pd.DataFrame(hd['candles'], columns=columns)
    hd2 = pd.DataFrame(hd1)
    hd2['Date'] = pd.to_datetime(hd1['Timestamp'], unit='s') + timedelta(hours=5, minutes=30)
    PE_Close_1m = hd2.iloc[-1, 4]
    PE_Date_1m = hd2.iloc[-1, 6].date()
    PE_Time_1 = hd2.iloc[-1, 6].time()
    print('Strike Price : ', PE_Close_1m, 'Date : ', PE_Date_1m, 'Time', PE_Time_1, 'Candel No. : ', c)
    logger.info('Strike Price :%s, Date :%s, Time :%s, Candel No. :%s', PE_Close_1m,  PE_Date_1m,  PE_Time_1,  c)
    if pe_flag == 1:
        cost_price = PE_Close_1m * qty
        if sheet.range('H56').value == 1:
            finvasia_buy_order_pe()
        base_url = 'https://api.telegram.org/bot5171253847:AAECG41z9ZsVXfSK4dBx77u9fsJJKsmD8_U/sendMessage?chat_id=-777697489&text="{}"'.format(f'Buying PE: {symbol1} @Price: {PE_Close_1m} Total Buy Value {cost_price} @Nifty: {Close_1m} Date: {PE_Date_1m} Time: {PE_Time_1}')
        requests.get(base_url)
        p = int(sheet1.range('N1').value)

        sheet1.range(f"B{p}").value = datetime.now()
        sheet1.range(f"C{p}").value = PE_Date_1m
        sheet1.range(f"D{p}").value = str(PE_Time_1)
        sheet1.range(f"E{p}").value = "PE"
        sheet1.range(f"F{p}").value = str(symbol1)
        sheet1.range(f"G{p}").value = str(Close_1m)
        sheet1.range(f"H{p}").value = "BUY " + signal
        sheet1.range(f"I{p}").value = str(PE_Close_1m)
        sheet1.range(f"J{p}").value = 50
        sheet1.range(f"K{p}").value = str(cost_price)
        sheet1.range(f"L{p}").value = ""
        workbook.save()
    elif ce_flag == 1:
        cost_price = CE_Close_1m * qty
        if sheet.range('H56').value == 1:
            finvasia_buy_order_ce()
        base_url = 'https://api.telegram.org/bot5171253847:AAECG41z9ZsVXfSK4dBx77u9fsJJKsmD8_U/sendMessage?chat_id=-777697489&text="{}"'.format(f'Buying CE: {symbol} @Price: {CE_Close_1m} Total Buy Value {cost_price} @Nifty: {Close_1m} Date: {CE_Date_1m} Time: {CE_Time_1}')
        requests.get(base_url)
        p = int(sheet1.range('N1').value)
        sheet1.range(f"B{p}").value = datetime.now()
        sheet1.range(f"C{p}").value = CE_Date_1m
        sheet1.range(f"D{p}").value = str(CE_Time_1)
        sheet1.range(f"E{p}").value = "CE"
        sheet1.range(f"F{p}").value = str(symbol)
        sheet1.range(f"G{p}").value = str(Close_1m)
        sheet1.range(f"H{p}").value = "BUY " + signal
        sheet1.range(f"I{p}").value = str(CE_Close_1m)
        sheet1.range(f"J{p}").value = 50
        sheet1.range(f"K{p}").value = str(cost_price)
        sheet1.range(f"L{p}").value = ""
        workbook.save()
    print("Cost_price : ", cost_price)
    logger.info("Cost_price : %s", cost_price)

def place_buy_orders():
    print("buy")

def place_sell_orders():
    print("sell")

def quotes_sell():
    global c, pe_flag, ce_flag, sell_price, qty, cost_price, profit, total_pnl, strike_pe_flag, strike_ce_flag, exit_type

    q = 19
    token = read_file()
    fyers = fyersModel.FyersModel(client_id=client_id, token=token, log_path=os.getcwd())
    cdate = sheet.range('H47').value.strftime('%Y-%m-%d')
    symbol = sheet.range('B15').value
    data = {"symbol": symbol, "resolution": "1", "date_format": "1", "range_from": cdate,
            "range_to": cdate, "cont_flag": "0"}
    hd = fyers.history(data)
    columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
    hd1 = pd.DataFrame(hd['candles'], columns=columns)
    hd2 = pd.DataFrame(hd1)
    hd2['Date'] = pd.to_datetime(hd1['Timestamp'], unit='s') + timedelta(hours=5, minutes=30)
    CE_Close_1m = hd2.iloc[-1, 4]
    CE_Date_1m = hd2.iloc[-1, 6].date()
    CE_Time_1 = hd2.iloc[-1, 6].time()
    print('Strike Price : ', CE_Close_1m, 'Date : ', CE_Date_1m, 'Time', CE_Time_1, 'Candel No. : ', c)
    logger.info('Strike Price :%s, Date :%s, Time :%s, Candel No. :%s', CE_Close_1m,  CE_Date_1m,  CE_Time_1,  c)
    symbol1 = sheet.range('B16').value
    data = {"symbol": symbol1, "resolution": "1", "date_format": "1", "range_from": cdate,
            "range_to": cdate, "cont_flag": "0"}
    hd = fyers.history(data)
    columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
    hd1 = pd.DataFrame(hd['candles'], columns=columns)
    hd2 = pd.DataFrame(hd1)
    hd2['Date'] = pd.to_datetime(hd1['Timestamp'], unit='s') + timedelta(hours=5, minutes=30)
    PE_Close_1m = hd2.iloc[-1, 4]
    PE_Date_1m = hd2.iloc[-1, 6].date()
    PE_Time_1 = hd2.iloc[-1, 6].time()
    print('Strike Price : ', PE_Close_1m, 'Date : ', PE_Date_1m, 'Time', PE_Time_1, 'Candel No. : ', c)
    logger.info('Strike Price :%s, Date :%s, Time :%s, Candel No. :%s', PE_Close_1m,  PE_Date_1m,  PE_Time_1,  c)
    if strike_pe_flag == 1:
        sell_price = round((PE_Close_1m * qty), 1)
        strike_pe_flag = 0
        profit = round((sell_price - cost_price), 1)
        total_pnl = round((total_pnl + profit), 1)
        print('Profit : ', profit, ' Total_PnL : ', total_pnl)
        logger.info('Profit :%s,Total_PnL :%s ', profit, total_pnl)
        if sheet.range('H56').value == 1:
            finvasia_sell_order_pe()
        base_url = 'https://api.telegram.org/bot5171253847:AAECG41z9ZsVXfSK4dBx77u9fsJJKsmD8_U/sendMessage?chat_id=-777697489&text="{}"'.format(f'Sell PE: {symbol1} Exit: {exit_type} @Price: {PE_Close_1m} Total Sell Value {sell_price} PnL {profit} Day PnL {total_pnl} @Nifty: {Close_1m} Date: {PE_Date_1m} Time: {PE_Time_1}')
        requests.get(base_url)
        p = int(sheet1.range('N1').value)
        sheet1.range(f"B{p}").value = datetime.now()
        sheet1.range(f"C{p}").value = str(PE_Date_1m)
        sheet1.range(f"D{p}").value = str(PE_Time_1)
        sheet1.range(f"E{p}").value = "PE"
        sheet1.range(f"F{p}").value = str(symbol1)
        sheet1.range(f"G{p}").value = str(Close_1m)
        sheet1.range(f"H{p}").value = "SELL"
        sheet1.range(f"I{p}").value = str(PE_Close_1m)
        sheet1.range(f"J{p}").value = 50
        sheet1.range(f"K{p}").value = str(sell_price)
        sheet1.range(f"L{p}").value = str(exit_type)
        workbook.save()
    elif strike_ce_flag == 1:
        sell_price = round((CE_Close_1m * qty), 1)
        strike_ce_flag = 0
        profit = round((sell_price - cost_price), 1)
        total_pnl = round((total_pnl + profit), 1)
        print('Profit : ', profit, ' Total_PnL : ', total_pnl)
        logger.info('Profit :%s,Total_PnL :%s ', profit, total_pnl)
        if sheet.range('H56').value == 1:
            finvasia_sell_order_ce()
        base_url = 'https://api.telegram.org/bot5171253847:AAECG41z9ZsVXfSK4dBx77u9fsJJKsmD8_U/sendMessage?chat_id=-777697489&text="{}"'.format(f'Sell CE: {symbol} Exit: {exit_type} @Price: {CE_Close_1m} Total Sell Value {sell_price} PnL {profit} Day PnL {total_pnl} @Nifty: {Close_1m} Date: {CE_Date_1m} Time: {CE_Time_1}')
        requests.get(base_url)
        p = int(sheet1.range('N1').value)
        sheet1.range(f"B{p}").value = datetime.now()
        sheet1.range(f"C{p}").value = str(CE_Date_1m)
        sheet1.range(f"D{p}").value = str(CE_Time_1)
        sheet1.range(f"E{p}").value = "CE"
        sheet1.range(f"F{p}").value = str(symbol)
        sheet1.range(f"G{p}").value = str(Close_1m)
        sheet1.range(f"H{p}").value = "SELL"
        sheet1.range(f"I{p}").value = str(CE_Close_1m)
        sheet1.range(f"J{p}").value = 50
        sheet1.range(f"K{p}").value = str(sell_price)
        sheet1.range(f"L{p}").value = str(exit_type)
        workbook.save()

def R3_cross_down():
    global S5CE, S5BCE, S5TPCE, S5SLCE, S5PE, S5BPE, S5TPPE, S5SLPE, S4CE, S4BCE, S4TPCE, S4SLCE, S4PE, S4BPE, S4TPPE, S4SLPE, S3CE, S3BCE, S3TPCE, S3SLCE, S3PE, S3BPE, S3TPPE, S3SLPE, R3CE, R3BCE, R3TPCE, R3SLCE, R3PE, R3BPE, R3TPPE, R3SLPE, R4CE, R4BCE, R4TPCE, R4SLCE, R4PE, R4BPE, R4TPPE, R4SLPE, R5CE, R5BCE, R5TPCE, R5SLCE, R5PE, R5BPE, R5TPPE, R5SLPE
    global i, cs_flag, pe_flag, ce_flag, no_trade, revert_flag, trade_book, PClose_1m, Close_1m, Time_1m, strike_ce_flag, strike_pe_flag, exit_type, signal
    while True:
        get_1m_candel()
        if Close_1m <= R3BPE and cs_flag == 1 and pe_flag == 0 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE BUY")
            logger.info("PE BUY")
            strike_pe_flag = 1
            pe_flag = 1
            ce_flag = 0
            cs_flag = 0
            signal = "R3 CD"
            quotes_buy()

        if Close_1m > R3CE and PClose_1m < R3CE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 1 and ce_flag == 0:
            print("R3 Cross Up")
            logger.info("R3 Cross Up")
            revert_flag = 1
        if Close_1m <= R3TPPE and cs_flag == 0 and pe_flag == 1 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE TP ")
            logger.info("PE TP")
            exit_type = "TP"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break

        if Close_1m >= R3SLPE and cs_flag == 0 and pe_flag == 1 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE SL ")
            logger.info("PE SL")
            exit_type = "SL"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            if revert_flag == 1:
                print("CE BUY")
                logger.info("CE BUY")
                strike_ce_flag = 1
                revert_flag = 0
                ce_flag = 1
                signal = "R3 CU"
                quotes_buy()
                R3_cross_up()

            break
        if Time_1m >= "15:15:00" and cs_flag == 0 and pe_flag == 1 and ce_flag == 0:
            print("SO ")
            logger.info("SO ")
            exit_type = "SO"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Time_1m >= "15:15:00" and cs_flag == 1 and pe_flag == 0 and ce_flag == 0:
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0
            break
        if Close_1m > R3CE and PClose_1m < R3CE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 0:
            print("R3 Cross Up")
            logger.info("R3 Cross Up")
            no_trade = 1
            break
        i += 1
    if no_trade == 1:
        no_trade = 0
        R3_cross_up()

def R3_cross_up():
    global S5CE, S5BCE, S5TPCE, S5SLCE, S5PE, S5BPE, S5TPPE, S5SLPE, S4CE, S4BCE, S4TPCE, S4SLCE, S4PE, S4BPE, S4TPPE, S4SLPE, S3CE, S3BCE, S3TPCE, S3SLCE, S3PE, S3BPE, S3TPPE, S3SLPE, R3CE, R3BCE, R3TPCE, R3SLCE, R3PE, R3BPE, R3TPPE, R3SLPE, R4CE, R4BCE, R4TPCE, R4SLCE, R4PE, R4BPE, R4TPPE, R4SLPE, R5CE, R5BCE, R5TPCE, R5SLCE, R5PE, R5BPE, R5TPPE, R5SLPE
    global i, cs_flag, pe_flag, ce_flag, no_trade, revert_flag, trade_book, PClose_1m, Close_1m, Time_1m, strike_ce_flag, strike_pe_flag, exit_type,signal
    while True:
        get_1m_candel()
        if Close_1m >= R3BCE and cs_flag == 1 and pe_flag == 0 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE BUY")
            logger.info("CE BUY")
            strike_ce_flag = 1
            pe_flag = 0
            ce_flag = 1
            cs_flag = 0
            signal = "R3 CU"
            quotes_buy()



        if Close_1m < R3PE and PClose_1m > R3PE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 1:
            print("R3 Cross Down")
            logger.info("R3 Cross Down")
            revert_flag = 1

        if Close_1m >= R3TPCE and cs_flag == 0 and pe_flag == 0 and ce_flag == 1 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE TP ")
            logger.info("CE TP")
            exit_type = "TP"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Close_1m <= R3SLCE and cs_flag == 0 and pe_flag == 0 and ce_flag == 1 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE SL ")
            logger.info("CE SL")
            exit_type = "SL"
            quotes_sell()
            ce_flag = 0
            pe_flag = 0
            cs_flag = 0

            if revert_flag == 1:
                print("PE BUY")
                logger.info("PE BUY")
                strike_pe_flag = 1
                revert_flag = 0
                pe_flag = 1
                signal = "R3 CD"
                quotes_buy()
                R3_cross_down()


            break
        if Time_1m >= "15:15:00" and cs_flag == 0 and pe_flag == 0 and ce_flag == 1:
            print("SO ")
            logger.info("SO ")
            exit_type = "SO"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Time_1m >= "15:15:00" and cs_flag == 1 and pe_flag == 0 and ce_flag == 0:
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0
            break
        if Close_1m < R3PE and PClose_1m > R3PE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 0:
            print("R3 Cross down")
            logger.info("R3 Cross down")
            no_trade = 1
            break
        i += 1
    if no_trade == 1:
        no_trade = 0
        R3_cross_down()

def R4_cross_down():
    global S5CE, S5BCE, S5TPCE, S5SLCE, S5PE, S5BPE, S5TPPE, S5SLPE, S4CE, S4BCE, S4TPCE, S4SLCE, S4PE, S4BPE, S4TPPE, S4SLPE, S3CE, S3BCE, S3TPCE, S3SLCE, S3PE, S3BPE, S3TPPE, S3SLPE, R3CE, R3BCE, R3TPCE, R3SLCE, R3PE, R3BPE, R3TPPE, R3SLPE, R4CE, R4BCE, R4TPCE, R4SLCE, R4PE, R4BPE, R4TPPE, R4SLPE, R5CE, R5BCE, R5TPCE, R5SLCE, R5PE, R5BPE, R5TPPE, R5SLPE
    global i, cs_flag, pe_flag, ce_flag, no_trade, revert_flag, trade_book, PClose_1m, Close_1m, Time_1m, strike_ce_flag, strike_pe_flag, exit_type,signal
    while True:
        get_1m_candel()
        if Close_1m <= R4BPE and cs_flag == 1 and pe_flag == 0 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE BUY")
            logger.info("PE BUY")
            strike_pe_flag = 1
            pe_flag = 1
            ce_flag = 0
            cs_flag = 0
            signal = "R4 CD"
            quotes_buy()


        if Close_1m > R4CE and PClose_1m < R4CE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 1 and ce_flag == 0:
            print("R4 Cross Up")
            logger.info("R4 Cross Up")
            revert_flag = 1
        if Close_1m <= R4TPPE and cs_flag == 0 and pe_flag == 1 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE TP ")
            logger.info("PE TP")
            exit_type = "TP"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Close_1m >= R4SLPE and cs_flag == 0 and pe_flag == 1 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE SL ")
            logger.info("PE SL")
            exit_type = "SL"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            if revert_flag == 1:
                print("CE BUY")
                logger.info("CE BUY")
                strike_ce_flag = 1
                revert_flag = 0
                ce_flag = 1
                signal = "R4 CU"
                quotes_buy()
                R4_cross_up()


            break
        if Time_1m >= "15:15:00" and cs_flag == 0 and pe_flag == 1 and ce_flag == 0:
            print("SO ")
            logger.info("SO ")
            exit_type = "SO"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Time_1m >= "15:15:00" and cs_flag == 1 and pe_flag == 0 and ce_flag == 0:
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0
            break
        if Close_1m > R4CE and PClose_1m < R4CE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 0:
            print("R4 Cross Up")
            logger.info("R4 Cross Up")
            no_trade = 1
            break
        i += 1
    if no_trade == 1:
        no_trade = 0
        R4_cross_up()

def R4_cross_up():
    global S5CE, S5BCE, S5TPCE, S5SLCE, S5PE, S5BPE, S5TPPE, S5SLPE, S4CE, S4BCE, S4TPCE, S4SLCE, S4PE, S4BPE, S4TPPE, S4SLPE, S3CE, S3BCE, S3TPCE, S3SLCE, S3PE, S3BPE, S3TPPE, S3SLPE, R3CE, R3BCE, R3TPCE, R3SLCE, R3PE, R3BPE, R3TPPE, R3SLPE, R4CE, R4BCE, R4TPCE, R4SLCE, R4PE, R4BPE, R4TPPE, R4SLPE, R5CE, R5BCE, R5TPCE, R5SLCE, R5PE, R5BPE, R5TPPE, R5SLPE
    global i, cs_flag, pe_flag, ce_flag, no_trade, revert_flag, trade_book, PClose_1m, Close_1m, Time_1m, strike_ce_flag, strike_pe_flag, exit_type,signal
    while True:
        get_1m_candel()
        if Close_1m >= R4BCE and cs_flag == 1 and pe_flag == 0 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE BUY")
            logger.info("CE Buy")
            strike_ce_flag = 1
            pe_flag = 0
            ce_flag = 1
            cs_flag = 0
            signal = "R4 CU"
            quotes_buy()


        if Close_1m < R4PE and PClose_1m > R4PE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 1:
            print("R4 Cross Down")
            logger.info("R4 Cross Down")
            revert_flag = 1
        if Close_1m >= R4TPCE and cs_flag == 0 and pe_flag == 0 and ce_flag == 1 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE TP ")
            logger.info("CE TP")
            exit_type = "TP"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Close_1m <= R4SLCE and cs_flag == 0 and pe_flag == 0 and ce_flag == 1 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE SL ")
            logger.info("CE SL")
            exit_type = "SL"
            quotes_sell()
            ce_flag = 0
            pe_flag = 0
            cs_flag = 0

            if revert_flag == 1:
                print("PE BUY")
                logger.info("PE BUY")
                strike_pe_flag = 1
                revert_flag = 0
                pe_flag = 1
                signal = "R4 CD"
                quotes_buy()
                R4_cross_down()

            break
        if Time_1m >= "15:15:00" and cs_flag == 0 and pe_flag == 0 and ce_flag == 1:
            print("SO ")
            logger.info("SO")
            exit_type = "SO"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Time_1m >= "15:15:00" and cs_flag == 1 and pe_flag == 0 and ce_flag == 0:
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0
            break
        if Close_1m < R4PE and PClose_1m > R4PE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 0:
            print("R4 Cross down")
            logger.info("R4 Cross down")
            no_trade = 1
            break
        i += 1
    if no_trade == 1:
        no_trade = 0
        R4_cross_down()

def R5_cross_down():
    global S5CE, S5BCE, S5TPCE, S5SLCE, S5PE, S5BPE, S5TPPE, S5SLPE, S4CE, S4BCE, S4TPCE, S4SLCE, S4PE, S4BPE, S4TPPE, S4SLPE, S3CE, S3BCE, S3TPCE, S3SLCE, S3PE, S3BPE, S3TPPE, S3SLPE, R3CE, R3BCE, R3TPCE, R3SLCE, R3PE, R3BPE, R3TPPE, R3SLPE, R4CE, R4BCE, R4TPCE, R4SLCE, R4PE, R4BPE, R4TPPE, R4SLPE, R5CE, R5BCE, R5TPCE, R5SLCE, R5PE, R5BPE, R5TPPE, R5SLPE
    global i, cs_flag, pe_flag, ce_flag, no_trade, revert_flag, trade_book, PClose_1m, Close_1m, Time_1m, strike_ce_flag, strike_pe_flag, exit_type,signal
    while True:
        get_1m_candel()
        if Close_1m <= R5BPE and cs_flag == 1 and pe_flag == 0 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE BUY")
            logger.info("PE BUY")
            strike_pe_flag = 1
            pe_flag = 1
            ce_flag = 0
            cs_flag = 0
            signal = "R5 CD"
            quotes_buy()

        if Close_1m < R5CE and PClose_1m > R5CE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 1 and ce_flag == 0:
            print("R5 Cross Up")
            logger.info("R5 Cross Up")
            revert_flag = 1

        if Close_1m <= R5TPPE and cs_flag == 0 and pe_flag == 1 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE TP ")
            logger.info("PE TP")
            exit_type = "TP"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Close_1m >= R5SLPE and cs_flag == 0 and pe_flag == 1 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE SL ")
            logger.info("PE SL")
            exit_type = "SL"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            if revert_flag == 1:
                print("CE BUY")
                logger.info("CE BUY")
                strike_ce_flag = 1
                revert_flag = 0
                ce_flag = 1
                signal = "R5 CU"
                quotes_buy()
                R5_cross_up()

            break
        if Time_1m >= "15:15:00" and cs_flag == 0 and pe_flag == 1 and ce_flag == 0:
            print("SO ")
            logger.info("SO")
            exit_type = "SO"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Time_1m >= "15:15:00" and cs_flag == 1 and pe_flag == 0 and ce_flag == 0:
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0
            break
        if Close_1m > R5CE and PClose_1m < R5CE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 0:
            print("R5 Cross Up")
            logger.info("R5 Cross Up")
            no_trade = 1
            break
        i += 1

    if no_trade == 1:
        no_trade = 0
        R5_cross_up()
    if i == 92935:
        print(i)

def R5_cross_up():
    global S5CE, S5BCE, S5TPCE, S5SLCE, S5PE, S5BPE, S5TPPE, S5SLPE, S4CE, S4BCE, S4TPCE, S4SLCE, S4PE, S4BPE, S4TPPE, S4SLPE, S3CE, S3BCE, S3TPCE, S3SLCE, S3PE, S3BPE, S3TPPE, S3SLPE, R3CE, R3BCE, R3TPCE, R3SLCE, R3PE, R3BPE, R3TPPE, R3SLPE, R4CE, R4BCE, R4TPCE, R4SLCE, R4PE, R4BPE, R4TPPE, R4SLPE, R5CE, R5BCE, R5TPCE, R5SLCE, R5PE, R5BPE, R5TPPE, R5SLPE
    global i, cs_flag, pe_flag, ce_flag, no_trade, revert_flag, trade_book, PClose_1m, Close_1m, Time_1m, strike_ce_flag, strike_pe_flag, strike_ce_flag, strike_pe_flag, exit_type,signal
    while True:
        get_1m_candel()
        if Close_1m >= R5BCE and cs_flag == 1 and pe_flag == 0 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE BUY")
            logger.info("CE BUY")
            strike_ce_flag = 1
            pe_flag = 0
            ce_flag = 1
            cs_flag = 0
            signal = "R5 CU"
            quotes_buy()

        if Close_1m < R5PE and PClose_1m > R5PE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 1:
            print("R5 Cross Down")
            logger.info("R5 Cross Down")
            revert_flag = 1

        if Close_1m >= R5TPCE and cs_flag == 0 and pe_flag == 0 and ce_flag == 1 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE TP ")
            logger.info("CE TP")
            exit_type = "TP"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Close_1m <= R5SLCE and cs_flag == 0 and pe_flag == 0 and ce_flag == 1 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE SL ")
            logger.info("CE SL")
            exit_type = "SL"
            quotes_sell()
            ce_flag = 0
            pe_flag = 0
            cs_flag = 0

            if revert_flag == 1:
                print("PE BUY")
                logger.info("PE BUY")
                strike_pe_flag = 1
                revert_flag = 0
                pe_flag = 1
                signal = "R5 CD"
                quotes_buy()
                R5_cross_down()

            break
        if Time_1m >= "15:15:00" and cs_flag == 0 and pe_flag == 0 and ce_flag == 1:
            print("SO ")
            logger.info("SO")
            exit_type = "SO"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Time_1m >= "15:15:00" and cs_flag == 1 and pe_flag == 0 and ce_flag == 0:
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0
            break
        if Time_1m >= "15:15:00" and cs_flag == 1 and pe_flag == 0 and ce_flag == 0:
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0
            break
        if Close_1m < R5PE and PClose_1m > R5PE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 0:
            print("R5 Cross down")
            logger.info("R5 Cross down")
            no_trade = 1
            break
        i += 1

    if no_trade == 1:
        no_trade = 0
        R5_cross_down()

def S3_cross_down():
    global S5CE, S5BCE, S5TPCE, S5SLCE, S5PE, S5BPE, S5TPPE, S5SLPE, S4CE, S4BCE, S4TPCE, S4SLCE, S4PE, S4BPE, S4TPPE, S4SLPE, S3CE, S3BCE, S3TPCE, S3SLCE, S3PE, S3BPE, S3TPPE, S3SLPE, R3CE, R3BCE, R3TPCE, R3SLCE, R3PE, R3BPE, R3TPPE, R3SLPE, R4CE, R4BCE, R4TPCE, R4SLCE, R4PE, R4BPE, R4TPPE, R4SLPE, R5CE, R5BCE, R5TPCE, R5SLCE, R5PE, R5BPE, R5TPPE, R5SLPE
    global i, cs_flag, pe_flag, ce_flag, no_trade, revert_flag, trade_book, PClose_1m, Close_1m, Time_1m, strike_ce_flag, strike_pe_flag, strike_ce_flag, strike_pe_flag, exit_type,signal
    while True:
        get_1m_candel()
        if Close_1m <= S3BPE and cs_flag == 1 and pe_flag == 0 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE BUY")
            logger.info("PE BUY")
            strike_pe_flag = 1
            pe_flag = 1
            ce_flag = 0
            cs_flag = 0
            signal = "S3 CD"
            quotes_buy()

        if Close_1m > S3CE and PClose_1m < S3CE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 1 and ce_flag == 0:
            print("S3 Cross Up")
            logger.info("S3 Cross Up")
            revert_flag = 1

        if Close_1m <= S3TPPE and cs_flag == 0 and pe_flag == 1 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE TP ")
            logger.info("PE TP")
            exit_type = "TP"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Close_1m >= S3SLPE and cs_flag == 0 and pe_flag == 1 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE SL ")
            logger.info("PE SL")
            exit_type = "SL"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            if revert_flag == 1:
                print("CE BUY")
                logger.info("CE BUY")
                strike_ce_flag = 1
                revert_flag = 0
                ce_flag = 1
                signal = "S3 CU"
                quotes_buy()
                S3_cross_up()

            break
        if Time_1m >= "15:15:00" and cs_flag == 0 and pe_flag == 1 and ce_flag == 0:
            print("SO ")
            logger.info("SO ")
            exit_type = "SO"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Time_1m >= "15:15:00" and cs_flag == 1 and pe_flag == 0 and ce_flag == 0:
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0
            break
        if Close_1m > S3CE and PClose_1m < S3CE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 0:
            print("S3 Cross Up")
            logger.info("S3 Cross Up")
            no_trade = 1
            cs_flag = 1
            break
        i += 1
    if no_trade == 1:
        no_trade = 0
        S3_cross_up()

def S3_cross_up():
    global S5CE, S5BCE, S5TPCE, S5SLCE, S5PE, S5BPE, S5TPPE, S5SLPE, S4CE, S4BCE, S4TPCE, S4SLCE, S4PE, S4BPE, S4TPPE, S4SLPE, S3CE, S3BCE, S3TPCE, S3SLCE, S3PE, S3BPE, S3TPPE, S3SLPE, R3CE, R3BCE, R3TPCE, R3SLCE, R3PE, R3BPE, R3TPPE, R3SLPE, R4CE, R4BCE, R4TPCE, R4SLCE, R4PE, R4BPE, R4TPPE, R4SLPE, R5CE, R5BCE, R5TPCE, R5SLCE, R5PE, R5BPE, R5TPPE, R5SLPE
    global i, cs_flag, pe_flag, ce_flag, no_trade, revert_flag, trade_book, PClose_1m, Close_1m, Time_1m, strike_ce_flag, strike_pe_flag, exit_type,signal
    while True:
        get_1m_candel()
        if Close_1m >= S3BCE and cs_flag == 1 and pe_flag == 0 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE BUY")
            logger.info("CE BUY")
            strike_ce_flag = 1
            pe_flag = 0
            ce_flag = 1
            cs_flag = 0
            signal = "S3 CU"
            quotes_buy()

        if Close_1m < S3PE and PClose_1m > S3PE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 1:
            print("S3 Cross Down")
            logger.info("S3 Cross Down")
            revert_flag = 1

        if Close_1m >= S3TPCE and cs_flag == 0 and pe_flag == 0 and ce_flag == 1 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE TP ")
            logger.info("CE TP")
            exit_type = "TP"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Close_1m <= S3SLCE and cs_flag == 0 and pe_flag == 0 and ce_flag == 1 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE SL ")
            logger.info("CE SL")
            exit_type = "SL"
            quotes_sell()
            ce_flag = 0
            pe_flag = 0
            cs_flag = 0

            if revert_flag == 1:
                print("PE BUY")
                logger.info("PE BUY")
                strike_pe_flag = 1
                revert_flag = 0
                pe_flag = 1
                signal = "S3 CD"
                quotes_buy()
                S3_cross_down()

            break
        if Time_1m >= "15:15:00" and cs_flag == 0 and pe_flag == 0 and ce_flag == 1:
            print("SO ")
            logger.info("SO")
            exit_type = "SO"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Time_1m >= "15:15:00" and cs_flag == 1 and pe_flag == 0 and ce_flag == 0:
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0
            break
        if Close_1m < S3PE and PClose_1m > S3PE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 0:
            print("S3 Cross Down")
            logger.info("S3 Cross Down")
            no_trade = 1
            cs_flag = 1
            break
        i += 1
    if no_trade == 1:
        no_trade = 0
        S3_cross_down()

def S4_cross_down():
    global S5CE, S5BCE, S5TPCE, S5SLCE, S5PE, S5BPE, S5TPPE, S5SLPE, S4CE, S4BCE, S4TPCE, S4SLCE, S4PE, S4BPE, S4TPPE, S4SLPE, S3CE, S3BCE, S3TPCE, S3SLCE, S3PE, S3BPE, S3TPPE, S3SLPE, R3CE, R3BCE, R3TPCE, R3SLCE, R3PE, R3BPE, R3TPPE, R3SLPE, R4CE, R4BCE, R4TPCE, R4SLCE, R4PE, R4BPE, R4TPPE, R4SLPE, R5CE, R5BCE, R5TPCE, R5SLCE, R5PE, R5BPE, R5TPPE, R5SLPE
    global i, cs_flag, pe_flag, ce_flag, no_trade, revert_flag, trade_book, PClose_1m, Close_1m, Time_1m, strike_ce_flag, strike_pe_flag, exit_type,signal
    while True:
        get_1m_candel()
        if Close_1m <= S4BPE and cs_flag == 1 and pe_flag == 0 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE BUY")
            logger.info("PE BUY")
            strike_pe_flag = 1
            pe_flag = 1
            ce_flag = 0
            cs_flag = 0
            signal = "S4 CD"
            quotes_buy()

        if Close_1m > S4CE and PClose_1m < S4CE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 1 and ce_flag == 0:
            print("S4 Cross Up")
            logger.info("S4 Cross Up")
            revert_flag = 1

        if Close_1m <= S4TPPE and cs_flag == 0 and pe_flag == 1 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE TP ")
            logger.info("PE TP")
            exit_type = "TP"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Close_1m >= S4SLPE and cs_flag == 0 and pe_flag == 1 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE SL ")
            logger.info("PE SL")
            exit_type = "SL"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            if revert_flag == 1:
                print("CE BUY")
                logger.info("CE BUY")
                strike_ce_flag = 1
                revert_flag = 0
                ce_flag = 1
                signal = "S4 CU"
                quotes_buy()
                S4_cross_up()

            break
        if Time_1m >= "15:15:00" and cs_flag == 0 and pe_flag == 1 and ce_flag == 0:
            print("SO ")
            logger.info("SO")
            exit_type = "SO"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Time_1m >= "15:15:00" and cs_flag == 1 and pe_flag == 0 and ce_flag == 0:
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0
            break
        if Close_1m > S4CE and PClose_1m < S4CE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 0:
            print("S4 Cross Up")
            logger.info("S4 Cross Up")
            no_trade = 1
            break
        i += 1
    if no_trade == 1:
        no_trade = 0
        S4_cross_up()

def S4_cross_up():
    global S5CE, S5BCE, S5TPCE, S5SLCE, S5PE, S5BPE, S5TPPE, S5SLPE, S4CE, S4BCE, S4TPCE, S4SLCE, S4PE, S4BPE, S4TPPE, S4SLPE, S3CE, S3BCE, S3TPCE, S3SLCE, S3PE, S3BPE, S3TPPE, S3SLPE, R3CE, R3BCE, R3TPCE, R3SLCE, R3PE, R3BPE, R3TPPE, R3SLPE, R4CE, R4BCE, R4TPCE, R4SLCE, R4PE, R4BPE, R4TPPE, R4SLPE, R5CE, R5BCE, R5TPCE, R5SLCE, R5PE, R5BPE, R5TPPE, R5SLPE
    global i, cs_flag, pe_flag, ce_flag, no_trade, revert_flag, trade_book, PClose_1m, Close_1m, Time_1m, strike_ce_flag, strike_pe_flag, exit_type,signal
    while True:
        get_1m_candel()
        if Close_1m >= S4BCE and cs_flag == 1 and pe_flag == 0 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE BUY")
            logger.info("CE BUY")
            strike_ce_flag = 1
            pe_flag = 0
            ce_flag = 1
            cs_flag = 0
            signal = "S4 CU"
            quotes_buy()

        if Close_1m < S4PE and PClose_1m > S4PE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 1:
            print("S4 Cross Down")
            logger.info("S4 Cross Down")
            revert_flag = 1

        if Close_1m >= S4TPCE and cs_flag == 0 and pe_flag == 0 and ce_flag == 1 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE TP ")
            logger.info("CE TP")
            exit_type = "TP"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Close_1m <= S4SLCE and cs_flag == 0 and pe_flag == 0 and ce_flag == 1 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE SL ")
            logger.info("CE SL")
            exit_type = "SL"
            quotes_sell()
            ce_flag = 0
            pe_flag = 0
            cs_flag = 0

            if revert_flag == 1:
                print("PE BUY")
                logger.info("PE BUY")
                strike_pe_flag = 1
                revert_flag = 0
                pe_flag = 1
                signal = "S4 CD"
                quotes_buy()
                S4_cross_down()

            break
        if Time_1m >= "15:15:00" and cs_flag == 0 and pe_flag == 0 and ce_flag == 1:
            print("SO ")
            logger.info("SO")
            exit_type = "SO"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Time_1m >= "15:15:00" and cs_flag == 1 and pe_flag == 0 and ce_flag == 0:
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0
            break
        if Close_1m < S4PE and PClose_1m > S4PE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 0:
            print("S4 Cross Down")
            logger.info("S4 Cross Down")
            no_trade = 1
            break
        i += 1
    if no_trade == 1:
        no_trade = 0
        S4_cross_down()

def S5_cross_down():
    global S5CE, S5BCE, S5TPCE, S5SLCE, S5PE, S5BPE, S5TPPE, S5SLPE, S4CE, S4BCE, S4TPCE, S4SLCE, S4PE, S4BPE, S4TPPE, S4SLPE, S3CE, S3BCE, S3TPCE, S3SLCE, S3PE, S3BPE, S3TPPE, S3SLPE, R3CE, R3BCE, R3TPCE, R3SLCE, R3PE, R3BPE, R3TPPE, R3SLPE, R4CE, R4BCE, R4TPCE, R4SLCE, R4PE, R4BPE, R4TPPE, R4SLPE, R5CE, R5BCE, R5TPCE, R5SLCE, R5PE, R5BPE, R5TPPE, R5SLPE
    global i, cs_flag, pe_flag, ce_flag, no_trade, revert_flag, trade_book, PClose_1m, Close_1m, Time_1m, strike_ce_flag, strike_pe_flag, exit_type,signal
    while True:
        get_1m_candel()
        if Close_1m <= S5BPE and cs_flag == 1 and pe_flag == 0 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE BUY")
            logger.info("PE BUY")
            strike_pe_flag = 1
            pe_flag = 1
            ce_flag = 0
            cs_flag = 0
            signal = "S5 CD"
            quotes_buy()
        if Close_1m > S5CE and PClose_1m < S5CE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 1 and ce_flag == 0:
            print("S5 Cross Up")
            logger.info("S5 Cross Up")
            revert_flag = 1

        if Close_1m <= S5TPPE and cs_flag == 0 and pe_flag == 1 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE TP ")
            logger.info("PE TP")
            exit_type = "TP"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Close_1m >= S5SLPE and cs_flag == 0 and pe_flag == 1 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("PE SL ")
            logger.info("PE SL")
            exit_type = "SL"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0
            if revert_flag == 0:
                print("CE BUY")
                logger.info("CE BUY")
                strike_ce_flag = 1
                revert_flag = 0
                ce_flag = 1
                signal = "S5 CU"
                quotes_buy()
                S5_cross_up()

            break
        if Time_1m >= "15:15:00" and cs_flag == 0 and pe_flag == 1 and ce_flag == 0:
            print("SO ")
            logger.info("SO")
            exit_type = "SO"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Time_1m >= "15:15:00" and cs_flag == 1 and pe_flag == 0 and ce_flag == 0:
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0
            break
        if Close_1m > S5CE and PClose_1m < S5CE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 0:
            print("S5 Cross Up")
            logger.info("S5 Cross Up")
            no_trade = 1
            break
        i += 1
    if no_trade == 1:
        no_trade = 0
        S5_cross_up()

def S5_cross_up():
    global S5CE, S5BCE, S5TPCE, S5SLCE, S5PE, S5BPE, S5TPPE, S5SLPE, S4CE, S4BCE, S4TPCE, S4SLCE, S4PE, S4BPE, S4TPPE, S4SLPE, S3CE, S3BCE, S3TPCE, S3SLCE, S3PE, S3BPE, S3TPPE, S3SLPE, R3CE, R3BCE, R3TPCE, R3SLCE, R3PE, R3BPE, R3TPPE, R3SLPE, R4CE, R4BCE, R4TPCE, R4SLCE, R4PE, R4BPE, R4TPPE, R4SLPE, R5CE, R5BCE, R5TPCE, R5SLCE, R5PE, R5BPE, R5TPPE, R5SLPE
    global i, cs_flag, pe_flag, ce_flag, no_trade, revert_flag, trade_book, PClose_1m, Close_1m, Time_1m, strike_ce_flag, strike_pe_flag, exit_type,signal
    while True:
        get_1m_candel()
        if Close_1m >= S5BCE and cs_flag == 1 and pe_flag == 0 and ce_flag == 0 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE BUY")
            logger.info("CE BUY")
            strike_ce_flag = 1
            pe_flag = 0
            ce_flag = 1
            cs_flag = 0
            signal = "S5 CU"
            quotes_buy()
        if Close_1m < S5PE and PClose_1m > S5PE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 1:
            print("S5 Cross Down")
            logger.info("S5 Cross Down")
            revert_flag = 1

        if Close_1m >= S5TPCE and cs_flag == 0 and pe_flag == 0 and ce_flag == 1 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE TP ")
            logger.info("CE TP")
            exit_type = "TP"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Close_1m <= S5SLCE and cs_flag == 0 and pe_flag == 0 and ce_flag == 1 and Time_1m > "09:20:00" and Time_1m < "15:15:00":
            print("CE SL ")
            logger.info("CE SL")
            exit_type = "SL"
            quotes_sell()
            ce_flag = 0
            pe_flag = 0
            cs_flag = 0

            if revert_flag == 1:
                print("PE BUY")
                logger.info("PE BUY")
                strike_pe_flag = 1
                revert_flag = 0
                pe_flag = 1
                signal = "S5 CD"
                quotes_buy()
                S5_cross_down()

            break
        if Time_1m >= "15:15:00" and cs_flag == 0 and pe_flag == 0 and ce_flag == 1:
            print("SO ")
            logger.info("SO")
            exit_type = "SO"
            quotes_sell()
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0

            break
        if Time_1m >= "15:15:00" and cs_flag == 1 and pe_flag == 0 and ce_flag == 0:
            cs_flag = 0
            pe_flag = 0
            ce_flag = 0
            break
        if Close_1m < S5PE and PClose_1m > S5PE and Time_1m > "09:20:00" and Time_1m < "15:15:00" and pe_flag == 0 and ce_flag == 0:
            print("S5 Cross Down")
            logger.info("S5 Cross Down")
            no_trade = 1
            break
        i += 1
    if no_trade == 1:
        no_trade = 0
        S5_cross_down()

def finvasia_login():
    api = ShoonyaApiPy()
    ret = api.login(userid=user, password=pwd, twoFA=pyotp.TOTP(totp_token).now(), vendor_code=vc, api_secret=apikey, imei=imei)

    logger.info(ret)

def finvasia_buy_order_pe():
    PE_symbol = sheet.range('H51').value
    ret_ce = api.set_session(userid=userid, password=pwd, usertoken=read_file_f())
    ret_ce = api.place_order(buy_or_sell='B',
                          product_type='I',
                          exchange='NFO',
                          tradingsymbol=PE_symbol,
                          quantity=100,
                          discloseqty=0,
                          price_type='MKT',
                          price=0,
                          trigger_price=0,
                          retention='DAY',
                          remarks='Buy_Order')
    print(ret_ce)
    logger.info(ret_ce)
def finvasia_buy_order_pe_OS():
    CE_symbol_ATM = sheet.range('H50').value
    CE_symbol_OTM = sheet.range('H52').value
    ret_ce = api.set_session(userid=userid, password=pwd, usertoken=read_file_f())
    ret_ce = api.place_order(buy_or_sell='B',
                          product_type='I',
                          exchange='NFO',
                          tradingsymbol=CE_symbol_OTM,
                          quantity=100,
                          discloseqty=0,
                          price_type='MKT',
                          price=0,
                          trigger_price=0,
                          retention='DAY',
                          remarks='Buy_Order')

    ret_ce = api.place_order(buy_or_sell='S',
                             product_type='I',
                             exchange='NFO',
                             tradingsymbol=CE_symbol_ATM,
                             quantity=100,
                             discloseqty=0,
                             price_type='MKT',
                             price=0,
                             trigger_price=0,
                             retention='DAY',
                             remarks='Sell_Order')
    print(ret_ce)
    logger.info(ret_ce)
def finvasia_sell_order_pe():
    PE_symbol = sheet.range('H51').value

    ret_ce = api.set_session(userid=userid, password=pwd, usertoken=read_file_f())
    ret_ce = api.place_order(buy_or_sell='S',
                          product_type='I',
                          exchange='NFO',
                          tradingsymbol=PE_symbol,
                          quantity=100,
                          discloseqty=0,
                          price_type='MKT',
                          price=0,
                          trigger_price=0,
                          retention='DAY',
                          remarks='Sell_Order')
    print(ret_ce)
    logger.info(ret_ce)
def finvasia_sell_order_pe_OS():
    CE_symbol_ATM = sheet.range('H50').value
    CE_symbol_OTM = sheet.range('H52').value

    ret_ce = api.set_session(userid=userid, password=pwd, usertoken=read_file_f())
    ret_ce = api.place_order(buy_or_sell='B',
                          product_type='I',
                          exchange='NFO',
                          tradingsymbol=CE_symbol_ATM,
                          quantity=100,
                          discloseqty=0,
                          price_type='MKT',
                          price=0,
                          trigger_price=0,
                          retention='DAY',
                          remarks='Sell_Order')
    ret_ce = api.place_order(buy_or_sell='S',
                             product_type='I',
                             exchange='NFO',
                             tradingsymbol=CE_symbol_OTM,
                             quantity=100,
                             discloseqty=0,
                             price_type='MKT',
                             price=0,
                             trigger_price=0,
                             retention='DAY',
                             remarks='Sell_Order')
    print(ret_ce)
    logger.info(ret_ce)
def finvasia_buy_order_ce():
    global CE_Symbol
    CE_symbol = sheet.range('H50').value
    print(CE_Symbol)

    ret = api.set_session(userid=userid, password=pwd, usertoken=read_file_f())
    ret = api.place_order(buy_or_sell='B',
                          product_type='I',
                          exchange='NFO',
                          tradingsymbol=CE_symbol,
                          quantity=100,
                          discloseqty=0,
                          price_type='MKT',
                          price=0,
                          trigger_price=0,
                          retention='DAY',
                          remarks='Buy_Order')
    print(ret)
    logger.info(ret)
def finvasia_buy_order_ce_OS():
    global CE_Symbol
    PE_symbol_ATM = sheet.range('H51').value
    PE_symbol_OTM = sheet.range('H53').value
    print(CE_Symbol)

    ret = api.set_session(userid=userid, password=pwd, usertoken=read_file_f())
    ret = api.place_order(buy_or_sell='B',
                          product_type='I',
                          exchange='NFO',
                          tradingsymbol=PE_symbol_OTM,
                          quantity=100,
                          discloseqty=0,
                          price_type='MKT',
                          price=0,
                          trigger_price=0,
                          retention='DAY',
                          remarks='Buy_Order')
    ret = api.place_order(buy_or_sell='S',
                          product_type='I',
                          exchange='NFO',
                          tradingsymbol=PE_symbol_ATM,
                          quantity=100,
                          discloseqty=0,
                          price_type='MKT',
                          price=0,
                          trigger_price=0,
                          retention='DAY',
                          remarks='Sell_Order')
    print(ret)
    logger.info(ret)
def finvasia_sell_order_ce():
    CE_symbol = sheet.range('H50').value
    api = ShoonyaApiPy()
    ret = api.set_session(userid=userid, password=pwd, usertoken=read_file_f())
    ret = api.place_order(buy_or_sell='S',
                          product_type='I',
                          exchange='NFO',
                          tradingsymbol=CE_symbol,
                          quantity=100,
                          discloseqty=0,
                          price_type='MKT',
                          price=0,
                          trigger_price=0,
                          retention='DAY',
                          remarks='Sell_Order')
    print(ret)
    logger.info(ret)
def finvasia_sell_order_ce_OS():
    PE_symbol_ATM = sheet.range('H51').value
    PE_symbol_OTM = sheet.range('H53').value
    api = ShoonyaApiPy()
    ret = api.set_session(userid=userid, password=pwd, usertoken=read_file_f())
    ret = api.place_order(buy_or_sell='B',
                          product_type='I',
                          exchange='NFO',
                          tradingsymbol=PE_symbol_ATM,
                          quantity=100,
                          discloseqty=0,
                          price_type='MKT',
                          price=0,
                          trigger_price=0,
                          retention='DAY',
                          remarks='Buy_Order')
    ret = api.place_order(buy_or_sell='S',
                          product_type='I',
                          exchange='NFO',
                          tradingsymbol=PE_symbol_OTM,
                          quantity=100,
                          discloseqty=0,
                          price_type='MKT',
                          price=0,
                          trigger_price=0,
                          retention='DAY',
                          remarks='Sell_Order')
    print(ret)
    logger.info(ret)




def Nifty_1d_finvasia():
    api = ShoonyaApiPy()
    ret = api.login(userid=user, password=pwd, twoFA=pyotp.TOTP(totp_token).now(), vendor_code=vc, api_secret=apikey, imei=imei)
    ret = api.get_quotes(exchange='NSE',token='26000')

def finvasia_search():
    api = ShoonyaApiPy()
    ret = api.login(userid=user, password=pwd, twoFA=pyotp.TOTP(totp_token).now(), vendor_code=vc, api_secret=apikey, imei=imei)
    ret = api.searchscrip(exchange='MCX', searchtext='SILVER')
    print(ret)

def Nifty_1m_finvasia():
    api = ShoonyaApiPy()
    ret = api.login(userid=user, password=pwd, twoFA=pyotp.TOTP(totp_token).now(), vendor_code=vc, api_secret=apikey, imei=imei)
    lastBusDay = datetime.datetime.today()
    lastBusDay = lastBusDay.replace(hour=0, minute=0, second=0, microsecond=0)
    ret = api.get_time_price_series(exchange='NSE', token='26000', starttime=lastBusDay.timestamp(), interval=1)
    print(pd.DataFrame(ret).to_string())

def event_handler_feed_update(tick_data):
    print(f"feed update {tick_data}")

def event_handler_order_update(order):
    print(f"order feed {order}")

def open_callback():
    global feed_opened
    feed_opened = True

def fin_websocket():
    api = ShoonyaApiPy()
    ret = api.login(userid=user, password=pwd, twoFA=pyotp.TOTP(totp_token).now(), vendor_code=vc, api_secret=apikey, imei=imei)



    api.start_websocket(order_update_callback=event_handler_order_update,
                        subscribe_callback=event_handler_feed_update,
                        socket_open_callback=open_callback)

    while (feed_opened == False):
        pass

    api.subscribe('MCX|239260')

def Finvasia_order_book():
    api = ShoonyaApiPy()
    ret = api.login(userid=user, password=pwd, twoFA=pyotp.TOTP(totp_token).now(), vendor_code=vc, api_secret=apikey, imei=imei)
    ret = api.get_order_book()
    print(pd.DataFrame(ret))

if __name__ == '__main__':

    result = pyfiglet.figlet_format("Welcome", font="digital")
    result1 = pyfiglet.figlet_format("MONEY BOT", font="digital")
    result2 = pyfiglet.figlet_format("Designed & Developed by Aditya Raj", font="digital")

    print(style.YELLOW, result)
    print(style.BLUE, result1)
    print(style.RED, result2)
    print(style.WHITE, "Starting...............")
    #setup()

    if sheet.range('H45').value == "Yes":
        print(style.YELLOW, "Setup Skipped")
    else:
        setup()
        sheet.range('H45').value = "Yes"

    get_1D_candel()
    print(sheet1.range('N1').value)
    time.sleep(5)
    t1 = threading.Thread(target=check_signal(), args=(10,))
    t1.start()
