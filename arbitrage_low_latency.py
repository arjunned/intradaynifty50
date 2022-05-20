from smartapi import SmartConnect
#from orders import *
from tokendata import *
import credentials
import time
import concurrent.futures
import csv
import pandas as pd
from datetime import datetime

# NO positions should be open in the account other than arbitrage

def place_order(orderparams):
    try:
        orderID = obj.placeOrder(orderparams)
        print(datetime.now(),f":-  The Order ID for Symbol {orderparams['tradingsymbol']} is: {orderID}")
    except Exception as e:
        print(f"Order placement for Symbol {orderparams['tradingsymbol']} failed: {e}")
def place_multiple_orders(tradeList):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(place_order, tradeList)
def get_ltp(params):
    obj = credentials.SMART_API_OBJ
    return obj.ltpData(params[0],params[1],params[2]).get('data').get('ltp')
def modify_order(obj, token, symbol, qty, exch_seg, buy_sell, ordertype, price, orderId, producttype="DELIVERY"):
    try:
        orderparams = {
            "orderid": orderId,
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": buy_sell,
            "exchange": exch_seg,
            "ordertype": ordertype,
            "producttype": producttype,
            "duration": "DAY",
            "price": price,
            "squareoff": "0",
            "stoploss": "0",
            "quantity": str(-1*int(qty)) if int(qty)<0 else str(qty)
        }
        orderresponse = obj.modifyOrder(orderparams)
        #print(orderresponse)
    except Exception as e:
        print("Order Modification failed: {}".format(e.message))
def modify_all_orders_to_market():
        obj = credentials.SMART_API_OBJ
        time.sleep(1)
        orders=obj.orderBook()['data']
        dfo=pd.DataFrame(orders)
        dfo=dfo[(dfo['status'] == 'open')]
        for index,row in dfo.iterrows():
            modify_order(obj,row['symboltoken'],row['tradingsymbol'],row['quantity'],row['exchange'],row['transactiontype'],'MARKET','0',row['orderid'],row['producttype'])
            print("Open order modified")
class PutCall():
    def __init__(self,qty):
        self.qty = qty
        self.entryflag = 0
        niftyltp = obj.ltpData('NSE','NIFTY',26000).get('data').get('ltp')
        print("NIFTY LTP: ",niftyltp)
        ATMstrike = round(round(niftyltp/100)*100)

        self.Strike1 = ATMstrike - 200
        self.Strike2 = ATMstrike
        self.Strike3 = ATMstrike + 200
        #strike tokens
        self.CE1token = getTokenInfo('NFO','OPTIDX','NIFTY',self.Strike1,'CE').iloc[0]['token']
        self.PE1token = getTokenInfo('NFO','OPTIDX','NIFTY',self.Strike1,'PE').iloc[0]['token']
        self.CE2token = getTokenInfo('NFO','OPTIDX','NIFTY',self.Strike2,'CE').iloc[0]['token']
        self.PE2token = getTokenInfo('NFO','OPTIDX','NIFTY',self.Strike2,'PE').iloc[0]['token']
        self.CE3token = getTokenInfo('NFO','OPTIDX','NIFTY',self.Strike3,'CE').iloc[0]['token']
        self.PE3token = getTokenInfo('NFO','OPTIDX','NIFTY',self.Strike3,'PE').iloc[0]['token']
        #strike symbols
        self.CE1symbol = getTokenInfo('NFO','OPTIDX','NIFTY',self.Strike1,'CE').iloc[0]['symbol']
        self.PE1symbol = getTokenInfo('NFO','OPTIDX','NIFTY',self.Strike1,'PE').iloc[0]['symbol']
        self.CE2symbol = getTokenInfo('NFO','OPTIDX','NIFTY',self.Strike2,'CE').iloc[0]['symbol']
        self.PE2symbol = getTokenInfo('NFO','OPTIDX','NIFTY',self.Strike2,'PE').iloc[0]['symbol']
        self.CE3symbol = getTokenInfo('NFO','OPTIDX','NIFTY',self.Strike3,'CE').iloc[0]['symbol']
        self.PE3symbol = getTokenInfo('NFO','OPTIDX','NIFTY',self.Strike3,'PE').iloc[0]['symbol']
        #instruments
        self.CE1 = ['NFO',self.CE1symbol,self.CE1token]
        self.PE1 = ['NFO',self.PE1symbol,self.PE1token]
        self.CE2 = ['NFO',self.CE2symbol,self.CE2token]
        self.PE2 = ['NFO',self.PE2symbol,self.PE2token]
        self.CE3 = ['NFO',self.CE3symbol,self.CE3token]
        self.PE3 = ['NFO',self.PE3symbol,self.PE3token]

    def entry(self,lbuffer,hbuffer):
        #if self.entryflag == 0:
        #Checking
        ex = concurrent.futures.ThreadPoolExecutor()
        fce1 = ex.submit(get_ltp, self.CE1)
        fpe1 = ex.submit(get_ltp, self.PE1)
        fce2 = ex.submit(get_ltp, self.CE2)
        fpe2 = ex.submit(get_ltp, self.PE2)
        fce3 = ex.submit(get_ltp, self.CE3)
        fpe3 = ex.submit(get_ltp, self.PE3)

        CE1ltp = fce1.result()
        PE1ltp = fpe1.result()
        CE2ltp = fce2.result()
        PE2ltp = fpe2.result()
        CE3ltp = fce3.result()
        PE3ltp = fpe3.result()

        #Boxes
        B1 = (200-(CE1ltp-PE1ltp+PE2ltp-CE2ltp))
        B2 = (200-(CE2ltp-PE2ltp+PE3ltp-CE3ltp))
        B3 = (400-(CE1ltp-PE1ltp+PE3ltp-CE3ltp))
        MaxB = max(abs(B1),abs(B2),abs(B3))
        print(MaxB)
        if MaxB > lbuffer and MaxB < hbuffer:
            if abs(B1) == MaxB:
                if B1 > 0:
                    print((200-(CE1ltp-PE1ltp+PE2ltp-CE2ltp))*50)
                    orderparams_entry_list = [{"variety": "NORMAL",
                                   "tradingsymbol": self.CE1symbol,
                                   "symboltoken": self.CE1token,
                                   "transactiontype": "BUY",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": CE1ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                         {"variety": "NORMAL",
                                   "tradingsymbol": self.PE2symbol,
                                   "symboltoken": self.PE2token,
                                   "transactiontype": "BUY",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": PE2ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                              {"variety": "NORMAL",
                                   "tradingsymbol": self.PE1symbol,
                                   "symboltoken": self.PE1token,
                                   "transactiontype": "SELL",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": PE1ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                         {"variety": "NORMAL",
                                   "tradingsymbol": self.CE2symbol,
                                   "symboltoken": self.CE2token,
                                   "transactiontype": "SELL",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": CE2ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty}]
                    place_multiple_orders(orderparams_entry_list)
                    self.entryflag = 1
                    # data rows of csv file
                    rows = [ [self.CE1symbol, self.CE1token, -1, 200],
                             [self.PE1symbol, self.PE1token, 1, 200],
                             [self.PE2symbol, self.PE2token, -1, 200],
                             [self.CE2symbol, self.CE2token, 1, 200],
                             ]
                    # writing to csv file
                    with open(filename, 'w') as csvfile:
                        # creating a csv writer object
                        csvwriter = csv.writer(csvfile)
                        # writing the fields
                        csvwriter.writerow(fields)
                        # writing the data rows
                        csvwriter.writerows(rows)
                else:
                    print((-200+(CE1ltp-PE1ltp+PE2ltp-CE2ltp)) *50)
                    orderparams_entry_list = [{"variety": "NORMAL",
                                   "tradingsymbol": self.CE1symbol,
                                   "symboltoken": self.CE1token,
                                   "transactiontype": "SELL",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": CE1ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                         {"variety": "NORMAL",
                                   "tradingsymbol": self.PE2symbol,
                                   "symboltoken": self.PE2token,
                                   "transactiontype": "SELL",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": PE2ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                              {"variety": "NORMAL",
                                   "tradingsymbol": self.PE1symbol,
                                   "symboltoken": self.PE1token,
                                   "transactiontype": "BUY",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": PE1ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                         {"variety": "NORMAL",
                                   "tradingsymbol": self.CE2symbol,
                                   "symboltoken": self.CE2token,
                                   "transactiontype": "BUY",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": CE2ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty}]
                    place_multiple_orders(orderparams_entry_list)
                    self.entryflag = 1
                    # data rows of csv file
                    rows = [ [self.CE1symbol, self.CE1token, 1, -200],
                             [self.PE1symbol, self.PE1token, -1, -200],
                             [self.PE2symbol, self.PE2token, 1, -200],
                             [self.CE2symbol, self.CE2token, -1, -200],
                             ]
                    # writing to csv file
                    with open(filename, 'w') as csvfile:
                        # creating a csv writer object
                        csvwriter = csv.writer(csvfile)
                        # writing the fields
                        csvwriter.writerow(fields)
                        # writing the data rows
                        csvwriter.writerows(rows)
            elif abs(B2) == MaxB:
                if B2 > 0:
                    print((200-(CE2ltp-PE2ltp+PE3ltp-CE3ltp)) *50)
                    orderparams_entry_list = [{"variety": "NORMAL",
                                   "tradingsymbol": self.CE2symbol,
                                   "symboltoken": self.CE2token,
                                   "transactiontype": "BUY",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": CE2ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                         {"variety": "NORMAL",
                                   "tradingsymbol": self.PE3symbol,
                                   "symboltoken": self.PE3token,
                                   "transactiontype": "BUY",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": PE3ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                            {"variety": "NORMAL",
                                   "tradingsymbol": self.PE2symbol,
                                   "symboltoken": self.PE2token,
                                   "transactiontype": "SELL",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": PE2ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                         {"variety": "NORMAL",
                                   "tradingsymbol": self.CE3symbol,
                                   "symboltoken": self.CE3token,
                                   "transactiontype": "SELL",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": CE3ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty}]
                    place_multiple_orders(orderparams_entry_list)
                    self.entryflag = 1
                    # data rows of csv file
                    rows = [ [self.CE2symbol, self.CE2token, -1, 200],
                             [self.PE2symbol, self.PE2token, 1, 200],
                             [self.PE3symbol, self.PE3token, -1, 200],
                             [self.CE3symbol, self.CE3token, 1, 200],
                             ]
                    # writing to csv file
                    with open(filename, 'w') as csvfile:
                        # creating a csv writer object
                        csvwriter = csv.writer(csvfile)
                        # writing the fields
                        csvwriter.writerow(fields)
                        # writing the data rows
                        csvwriter.writerows(rows)
                else:
                    print((-200+(CE2ltp-PE2ltp+PE3ltp-CE3ltp)) *50)
                    orderparams_entry_list = [{"variety": "NORMAL",
                                   "tradingsymbol": self.CE2symbol,
                                   "symboltoken": self.CE2token,
                                   "transactiontype": "SELL",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": CE2ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                         {"variety": "NORMAL",
                                   "tradingsymbol": self.PE3symbol,
                                   "symboltoken": self.PE3token,
                                   "transactiontype": "SELL",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": PE3ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                              {"variety": "NORMAL",
                                   "tradingsymbol": self.PE2symbol,
                                   "symboltoken": self.PE2token,
                                   "transactiontype": "BUY",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": PE2ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                         {"variety": "NORMAL",
                                   "tradingsymbol": self.CE3symbol,
                                   "symboltoken": self.CE3token,
                                   "transactiontype": "BUY",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": CE3ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty}]
                    place_multiple_orders(orderparams_entry_list)
                    self.entryflag = 1
                    # data rows of csv file
                    rows = [ [self.CE2symbol, self.CE2token, 1, -200],
                             [self.PE2symbol, self.PE2token, -1, -200],
                             [self.PE3symbol, self.PE3token, 1, -200],
                             [self.CE3symbol, self.CE3token, -1, -200],
                             ]
                    # writing to csv file
                    with open(filename, 'w') as csvfile:
                        # creating a csv writer object
                        csvwriter = csv.writer(csvfile)
                        # writing the fields
                        csvwriter.writerow(fields)
                        # writing the data rows
                        csvwriter.writerows(rows)
            elif abs(B3) == MaxB:
                if B2 > 0:
                    print((400-(CE1ltp-PE1ltp+PE3ltp-CE3ltp)) *50)
                    orderparams_entry_list = [{"variety": "NORMAL",
                                   "tradingsymbol": self.CE1symbol,
                                   "symboltoken": self.CE1token,
                                   "transactiontype": "BUY",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": CE1ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                         {"variety": "NORMAL",
                                   "tradingsymbol": self.PE3symbol,
                                   "symboltoken": self.PE3token,
                                   "transactiontype": "BUY",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": PE3ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                              {"variety": "NORMAL",
                                   "tradingsymbol": self.PE1symbol,
                                   "symboltoken": self.PE1token,
                                   "transactiontype": "SELL",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": PE1ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                         {"variety": "NORMAL",
                                   "tradingsymbol": self.CE3symbol,
                                   "symboltoken": self.CE3token,
                                   "transactiontype": "SELL",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": CE3ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty}]
                    place_multiple_orders(orderparams_entry_list)
                    self.entryflag = 1
                    # data rows of csv file
                    rows = [ [self.CE1symbol, self.CE1token, -1, 400],
                             [self.PE1symbol, self.PE1token, 1, 400],
                             [self.PE3symbol, self.PE3token, -1, 400],
                             [self.CE3symbol, self.CE3token, 1, 400],
                             ]
                    # writing to csv file
                    with open(filename, 'w') as csvfile:
                        # creating a csv writer object
                        csvwriter = csv.writer(csvfile)
                        # writing the fields
                        csvwriter.writerow(fields)
                        # writing the data rows
                        csvwriter.writerows(rows)
                else:
                    print((-400+(CE1ltp-PE1ltp+PE3ltp-CE3ltp)) *50)
                    orderparams_entry_list = [{"variety": "NORMAL",
                                   "tradingsymbol": self.CE1symbol,
                                   "symboltoken": self.CE1token,
                                   "transactiontype": "SELL",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": CE1ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                         {"variety": "NORMAL",
                                   "tradingsymbol": self.PE3symbol,
                                   "symboltoken": self.PE3token,
                                   "transactiontype": "SELL",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": PE3ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                              {"variety": "NORMAL",
                                   "tradingsymbol": self.PE1symbol,
                                   "symboltoken": self.PE1token,
                                   "transactiontype": "BUY",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": PE1ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty},
                                         {"variety": "NORMAL",
                                   "tradingsymbol": self.CE3symbol,
                                   "symboltoken": self.CE3token,
                                   "transactiontype": "BUY",
                                   "exchange": "NFO",
                                   "ordertype": "LIMIT",
                                   "producttype": "CARRYFORWARD",
                                   "duration": "DAY",
                                   "price": CE3ltp,
                                   "squareoff": "0",
                                   "stoploss": "0",
                                   "quantity": self.qty}]
                    place_multiple_orders(orderparams_entry_list)
                    self.entryflag = 1
                    # data rows of csv file
                    rows = [ [self.CE1symbol, self.CE1token, 1, -400],
                             [self.PE1symbol, self.PE1token, -1, -400],
                             [self.PE3symbol, self.PE3token, 1, -400],
                             [self.CE3symbol, self.CE3token, -1, -400],
                             ]
                    # writing to csv file
                    with open(filename, 'w') as csvfile:
                        # creating a csv writer object
                        csvwriter = csv.writer(csvfile)
                        # writing the fields
                        csvwriter.writerow(fields)
                        # writing the data rows
                        csvwriter.writerows(rows)
            time.sleep(10)
            modify_all_orders_to_market()
            self.read_entries()

        else:
            pass
        #else:
            #pass
    def read_entries(self):
        df = pd.read_csv("arbritage_entries.csv")
        self.Lstep = int(df['step'][0])
        self.L1symbol = str(df['symbol'][0])
        self.L1token = str(df['token'][0])
        self.L1sign = int(df['sign'][0])
        self.L2symbol = str(df['symbol'][1])
        self.L2token = str(df['token'][1])
        self.L2sign = int(df['sign'][1])
        self.L3symbol = str(df['symbol'][2])
        self.L3token = str(df['token'][2])
        self.L3sign = int(df['sign'][2])
        self.L4symbol = str(df['symbol'][3])
        self.L4token = str(df['token'][3])
        self.L4sign = int(df['sign'][3])
        #instruments to exit
        self.L1 = ['NFO',self.L1symbol,self.L1token]
        self.L2 = ['NFO',self.L2symbol,self.L2token]
        self.L3 = ['NFO',self.L3symbol,self.L3token]
        self.L4 = ['NFO',self.L4symbol,self.L4token]
    def exit(self,lbuffer,hbuffer):
        #if self.entryflag == 1:
        ex = concurrent.futures.ThreadPoolExecutor()
        fl1 = ex.submit(get_ltp, self.L1)
        fl2 = ex.submit(get_ltp, self.L2)
        fl3 = ex.submit(get_ltp, self.L3)
        fl4 = ex.submit(get_ltp, self.L4)

        L1ltp = fl1.result()
        L2ltp = fl2.result()
        L3ltp = fl3.result()
        L4ltp = fl4.result()

        eqn = self.Lstep + self.L1sign*L1ltp + self.L2sign*L2ltp + self.L3sign*L3ltp + self.L4sign*L4ltp
        print(eqn)
        if eqn < lbuffer and eqn > hbuffer:
            orderparams_exit_list = [{"variety": "NORMAL",
                           "tradingsymbol": self.L1symbol,
                           "symboltoken": self.L1token,
                           "transactiontype": "BUY" if self.L1sign > 0 else "SELL",
                           "exchange": "NFO",
                           "ordertype": "LIMIT",
                           "producttype": "CARRYFORWARD",
                           "duration": "DAY",
                           "price": L1ltp,
                           "squareoff": "0",
                           "stoploss": "0",
                           "quantity": self.qty},
                                 {"variety": "NORMAL",
                           "tradingsymbol": self.L2symbol,
                           "symboltoken": self.L2token,
                           "transactiontype": "BUY" if self.L2sign > 0 else "SELL",
                           "exchange": "NFO",
                           "ordertype": "LIMIT",
                           "producttype": "CARRYFORWARD",
                           "duration": "DAY",
                           "price": L2ltp,
                           "squareoff": "0",
                           "stoploss": "0",
                           "quantity": self.qty},
                                {"variety": "NORMAL",
                           "tradingsymbol": self.L3symbol,
                           "symboltoken": self.L3token,
                           "transactiontype": "BUY" if self.L3sign > 0 else "SELL",
                           "exchange": "NFO",
                           "ordertype": "LIMIT",
                           "producttype": "CARRYFORWARD",
                           "duration": "DAY",
                           "price": L3ltp,
                           "squareoff": "0",
                           "stoploss": "0",
                           "quantity": self.qty},
                                {"variety": "NORMAL",
                           "tradingsymbol": self.L4symbol,
                           "symboltoken": self.L4token,
                           "transactiontype": "BUY" if self.L4sign > 0 else "SELL",
                           "exchange": "NFO",
                           "ordertype": "LIMIT",
                           "producttype": "CARRYFORWARD",
                           "duration": "DAY",
                           "price": L4ltp,
                           "squareoff": "0",
                           "stoploss": "0",
                           "quantity": self.qty}]
            place_multiple_orders(orderparams_exit_list)
            self.entryflag = 0
            time.sleep(10)
            modify_all_orders_to_market()

# field names
fields = ['symbol', 'token', 'sign', 'step']
# name of csv file
filename = "arbritage_entries.csv"

if __name__ == '__main__':
    apikey = credentials.API_KEY
    username = credentials.USER_NAME
    pwd = credentials.PWD
    obj = SmartConnect(api_key=apikey)
    # login
    data = obj.generateSession(username, pwd)
    refreshToken = data['data']['refreshToken']
    # fetch the feedtoken
    feedToken = obj.getfeedToken()
    # fetch User Profile
    userProfile = obj.getProfile(refreshToken)
    print('LOGIN '+data['message'])
    credentials.SMART_API_OBJ = obj

    print("Available Balance: ",obj.rmsLimit()['data']['availablecash'])
    intializeSymbolTokenMap()
    lot = 1
    qty = lot*50
    time.sleep(1)
    arbritrage = PutCall(qty)
    arbritrage.read_entries()

    while True:
#        arbritrage.exit(-0.9, -1.1)
#        time.sleep(1)
#"""
        if arbritrage.entryflag == 0:
            arbritrage.entry(1.7, 1.95)
            time.sleep(0.6)
            #arbritrage.read_entries()
        elif arbritrage.entryflag == 1:
            arbritrage.exit(-1.5, -1.75)
            time.sleep(0.6)
        else:
            pass
#"""


