from smartapi import SmartConnect
# from smartapi import SmartWebSocket
from orders import *
from tokendata import *
import credentials
import schedule
import time
import csv
import concurrent.futures
from datetime import datetime

# NOTES
# Suitable for IV collapsing or High theta decay


class Ironfly1():
    def __init__(self, qty):
        self.qty = qty
        self.straddle_point = 0
        self.flag = 0
        self.adjustmentflag = 0
        self.target_hit = 0
        niftyltp = obj.ltpData('NSE', 'NIFTY', '26000').get('data').get('ltp')
        self.straddle_point = niftyltp
        ATMstrike = round(round(niftyltp/50)*50)
        #ironfly1
        self.BUYCEStrike = ATMstrike + 650
        self.BUYPEStrike = ATMstrike - 650
        self.SELLCEStrike = ATMstrike
        self.SELLPEStrike = ATMstrike
        #strike tokens
        BUYCEtoken = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.BUYCEStrike, 'CE').iloc[0]['token']
        BUYPEtoken = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.BUYPEStrike, 'PE').iloc[0]['token']
        SELLCEtoken = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.SELLCEStrike, 'CE').iloc[0]['token']
        SELLPEtoken = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.SELLPEStrike, 'PE').iloc[0]['token']
        #strike symbols
        BUYCEsymbol = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.BUYCEStrike, 'CE').iloc[0]['symbol']
        BUYPEsymbol = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.BUYPEStrike, 'PE').iloc[0]['symbol']
        SELLCEsymbol = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.SELLCEStrike, 'CE').iloc[0]['symbol']
        SELLPEsymbol = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.SELLPEStrike, 'PE').iloc[0]['symbol']
        #Creating object for orders
        self.buyCE = Order(obj, BUYCEtoken, BUYCEsymbol, self.qty, 'NFO', 'BUY', 'LIMIT', 'CARRYFORWARD')
        self.buyPE = Order(obj, BUYPEtoken, BUYPEsymbol, self.qty, 'NFO', 'BUY', 'LIMIT', 'CARRYFORWARD')
        self.sellCE = Order(obj, SELLCEtoken, SELLCEsymbol, self.qty, 'NFO', 'SELL', 'LIMIT', 'CARRYFORWARD')
        self.sellPE = Order(obj, SELLPEtoken, SELLPEsymbol, self.qty, 'NFO', 'SELL', 'LIMIT', 'CARRYFORWARD')

    def execute(self):
        niftyltp = obj.ltpData('NSE', 'NIFTY', '26000').get('data').get('ltp')
        self.straddle_point = niftyltp
        print("Straddle Point of IF-1: ", self.straddle_point)
        print("NIFTY LTP: ", niftyltp)
        ATMstrike = round(round(niftyltp/50)*50)
        print("NIFTY ATM Strike Price: ", ATMstrike)
        #ironfly1
        self.BUYCEStrike = ATMstrike + 650
        self.BUYPEStrike = ATMstrike - 650
        self.SELLCEStrike = ATMstrike
        self.SELLPEStrike = ATMstrike
        #strike tokens
        BUYCEtoken = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.BUYCEStrike, 'CE').iloc[0]['token']
        BUYPEtoken = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.BUYPEStrike, 'PE').iloc[0]['token']
        SELLCEtoken = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.SELLCEStrike, 'CE').iloc[0]['token']
        SELLPEtoken = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.SELLPEStrike, 'PE').iloc[0]['token']
        #strike symbols
        BUYCEsymbol = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.BUYCEStrike, 'CE').iloc[0]['symbol']
        BUYPEsymbol = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.BUYPEStrike, 'PE').iloc[0]['symbol']
        SELLCEsymbol = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.SELLCEStrike, 'CE').iloc[0]['symbol']
        SELLPEsymbol = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.SELLPEStrike, 'PE').iloc[0]['symbol']
        #Creating object for orders
        self.buyCE = Order(obj, BUYCEtoken, BUYCEsymbol, self.qty, 'NFO', 'BUY', 'LIMIT', 'CARRYFORWARD')
        self.buyPE = Order(obj, BUYPEtoken, BUYPEsymbol, self.qty, 'NFO', 'BUY', 'LIMIT', 'CARRYFORWARD')
        self.sellCE = Order(obj, SELLCEtoken, SELLCEsymbol, self.qty, 'NFO', 'SELL', 'LIMIT', 'CARRYFORWARD')
        self.sellPE = Order(obj, SELLPEtoken, SELLPEsymbol, self.qty, 'NFO', 'SELL', 'LIMIT', 'CARRYFORWARD')

        #Placing orders
        #if obj.rmsLimit()['data']['availablecash']/50000 >= self.qty
        bce = ex.submit(self.buyCE.fillinTsec, 9)
        bpe = ex.submit(self.buyPE.fillinTsec, 9)
        bce_status = bce.result()
        bpe_status = bpe.result()
        if bce_status != 0 and bpe_status != 0:#'complete'
            sce = ex.submit(self.sellCE.fillinTsec, 9)
            spe = ex.submit(self.sellPE.fillinTsec, 9)
            sce_status = sce.result()
            spe_status = spe.result()
            time.sleep(1)
            if sce_status != 0 and spe_status != 0:
                sellpeprice = obj.ltpData('NFO',self.sellPE.symbol, self.sellPE.token).get('data').get('ltp')
                sellceprice = obj.ltpData('NFO',self.sellCE.symbol, self.sellCE.token).get('data').get('ltp')
                if slpoints > round(round(sellpeprice*0.3/0.05)*0.05):
                    self.sellPE.SL(round(round(sellpeprice*0.3/0.05)*0.05))
                else:
                    self.sellPE.SL(slpoints)
                if slpoints > round(round(sellceprice*0.3/0.05)*0.05):
                    self.sellCE.SL(round(round(sellceprice*0.3/0.05)*0.05))
                else:
                    self.sellCE.SL(slpoints)
                print("Ironfly-1 deployed")
                self.flag = 1
                rows = [ [self.buyCE.symbol, self.buyCE.token, self.buyCE.OrderId, 0, self.BUYCEStrike, self.straddle_point],
                             [self.buyPE.symbol, self.buyPE.token, self.buyPE.OrderId, 0, self.BUYPEStrike, 0],
                             [self.sellCE.symbol, self.sellCE.token, self.sellCE.OrderId, self.sellCE.OrderIdSL,self.SELLCEStrike, 0],
                             [self.sellPE.symbol, self.sellPE.token, self.sellPE.OrderId, self.sellPE.OrderIdSL,self.SELLPEStrike, 0]
                             ]
                # writing to csv file
                with open("Ironfly1.csv", 'w') as csvfile:
                    # creating a csv writer object
                    csvwriter = csv.writer(csvfile)
                    # writing the fields
                    csvwriter.writerow(fields)
                    # writing the data rows
                    csvwriter.writerows(rows)
        else:
            print("BUY Orders not filled in time")


    def target_and_sl(self):# hunting
        if self.flag == 1:
            # get pnl from postions
            pnl = 0
            df_entries = pd.read_csv("Ironfly1.csv") # Ironfly.csv
            df = pd.DataFrame(obj.position()['data'])
            df['unrealised'] = df['unrealised'].astype('float')
            df['realised'] = df['realised'].astype('float')
            for i, r in df_entries.iterrows():
                unrealised = df[(df['symboltoken'] == str(r['token']))]['unrealised'].iloc[0]
                realised = df[(df['symboltoken'] == str(r['token']))]['realised'].iloc[0]
                pnl = pnl + unrealised + realised

            if (self.adjustmentflag == 0 and pnl > 70*self.qty) or (self.adjustmentflag == 1 and pnl > 40*self.qty): # 2000 per lot
                self.exit_all()

                if self.target_hit < 3:
                    self.execute()
                self.target_hit = self.target_hit + 1
                print("Net p&l of Ironfly-1: ", pnl)

    def exit_all(self):
        if self.flag == 1:
            obj.cancelOrder(self.sellPE.OrderIdSL,"NORMAL")
            obj.cancelOrder(self.sellCE.OrderIdSL,"NORMAL")
            self.sellPE.exit()
            self.sellCE.exit()
            self.buyPE.exit()
            self.buyCE.exit()
            self.flag = 0
            print("All positions of Ironfly-1 exited")
        """if self.flag == 1:
            obj.cancelOrder(self.sellPE.OrderIdSL, "NORMAL")
            obj.cancelOrder(self.sellCE.OrderIdSL, "NORMAL")
            sce = ex.submit(self.sellPE.exit)
            spe = ex.submit(self.sellCE.exit)
            sce_status = sce.result()
            spe_status = spe.result()
            bce = ex.submit(self.buyPE.exit)
            bpe = ex.submit(self.buyCE.exit)
            bce_status = bce.result()
            bpe_status = bpe.result()

            self.flag = 0
            print("All positions of Ironfly-1 exited")"""
    def read_entries(self):
        df_entries = pd.read_csv("Ironfly1.csv")
        self.straddle_point = int(float(df_entries['straddlepoint'][0]))
        self.buyCE.symbol = str(df_entries['symbol'][0])
        self.buyCE.token = str(int(df_entries['token'][0]))
        self.buyCE.OrderId = str(int(df_entries['orderid'][0]))
        self.BUYCEStrike = int(float(df_entries['strike'][0]))
        self.buyPE.symbol = str(df_entries['symbol'][1])
        self.buyPE.token = str(int(df_entries['token'][1]))
        self.buyPE.OrderId = str(int(df_entries['orderid'][1]))
        self.BUYPEStrike = int(float(df_entries['strike'][1]))
        self.sellCE.symbol = str(df_entries['symbol'][2])
        self.sellCE.token = str(int(df_entries['token'][2]))
        self.sellCE.OrderId = str(int(df_entries['orderid'][2]))
        self.sellCE.OrderIdSL = str(int(df_entries['SLorderid'][2]))
        self.SELLCEStrike = int(float(df_entries['strike'][2]))
        self.sellPE.symbol = str(df_entries['symbol'][3])
        self.sellPE.token = str(int(df_entries['token'][3]))
        self.sellCE.OrderId = str(int(df_entries['orderid'][3]))
        self.sellPE.OrderIdSL = str(int(df_entries['SLorderid'][3]))
        self.SELLPEStrike = int(float(df_entries['strike'][3]))
        print("Entries updated")
        self.flag = 1
class Ironfly2():
    def __init__(self, qty):
        self.qty = qty
        self.straddle_point = 0
        self.flag = 0
        self.adjustmentflag = 0
        self.target_hit = 0
        niftyltp = obj.ltpData('NSE', 'NIFTY', '26000').get('data').get('ltp')
        self.straddle_point = niftyltp
        ATMstrike = round(round(niftyltp/50)*50)

        #ironfly2
        self.BUYCEStrike = ATMstrike + 650
        self.BUYPEStrike = ATMstrike - 650
        self.SELLCEStrike = ATMstrike
        self.SELLPEStrike = ATMstrike
        #strike tokens
        BUYCEtoken = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.BUYCEStrike, 'CE').iloc[0]['token']
        BUYPEtoken = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.BUYPEStrike, 'PE').iloc[0]['token']
        SELLCEtoken = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.SELLCEStrike, 'CE').iloc[0]['token']
        SELLPEtoken = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.SELLPEStrike, 'PE').iloc[0]['token']
        #strike symbols
        BUYCEsymbol = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.BUYCEStrike, 'CE').iloc[0]['symbol']
        BUYPEsymbol = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.BUYPEStrike, 'PE').iloc[0]['symbol']
        SELLCEsymbol = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.SELLCEStrike, 'CE').iloc[0]['symbol']
        SELLPEsymbol = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.SELLPEStrike, 'PE').iloc[0]['symbol']
        #Creating object for orders
        self.buyCE = Order(obj, BUYCEtoken, BUYCEsymbol, self.qty, 'NFO', 'BUY', 'LIMIT', 'CARRYFORWARD')
        self.buyPE = Order(obj, BUYPEtoken, BUYPEsymbol, self.qty, 'NFO', 'BUY', 'LIMIT', 'CARRYFORWARD')
        self.sellCE = Order(obj, SELLCEtoken, SELLCEsymbol, self.qty, 'NFO', 'SELL', 'LIMIT', 'CARRYFORWARD')
        self.sellPE = Order(obj, SELLPEtoken, SELLPEsymbol, self.qty, 'NFO', 'SELL', 'LIMIT', 'CARRYFORWARD')

    def execute(self):
        niftyltp = obj.ltpData('NSE', 'NIFTY', '26000').get('data').get('ltp')
        self.straddle_point = niftyltp
        print("Straddle Point of IF-2: ", self.straddle_point)
        print("NIFTY LTP: ", niftyltp)
        ATMstrike = round(round(niftyltp/50)*50)
        print("NIFTY ATM Strike Price: ", ATMstrike)
        #ironfly2
        self.BUYCEStrike = ATMstrike + 650
        self.BUYPEStrike = ATMstrike - 650
        self.SELLCEStrike = ATMstrike
        self.SELLPEStrike = ATMstrike
        #strike tokens
        BUYCEtoken = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.BUYCEStrike, 'CE').iloc[0]['token']
        BUYPEtoken = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.BUYPEStrike, 'PE').iloc[0]['token']
        SELLCEtoken = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.SELLCEStrike, 'CE').iloc[0]['token']
        SELLPEtoken = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.SELLPEStrike, 'PE').iloc[0]['token']
        #strike symbols
        BUYCEsymbol = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.BUYCEStrike, 'CE').iloc[0]['symbol']
        BUYPEsymbol = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.BUYPEStrike, 'PE').iloc[0]['symbol']
        SELLCEsymbol = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.SELLCEStrike, 'CE').iloc[0]['symbol']
        SELLPEsymbol = getTokenInfo('NFO', 'OPTIDX', 'NIFTY', self.SELLPEStrike, 'PE').iloc[0]['symbol']
        #Creating object for orders
        self.buyCE = Order(obj, BUYCEtoken, BUYCEsymbol, self.qty, 'NFO', 'BUY', 'LIMIT', 'CARRYFORWARD')
        self.buyPE = Order(obj, BUYPEtoken, BUYPEsymbol, self.qty, 'NFO', 'BUY', 'LIMIT', 'CARRYFORWARD')
        self.sellCE = Order(obj, SELLCEtoken, SELLCEsymbol, self.qty, 'NFO', 'SELL', 'LIMIT', 'CARRYFORWARD')
        self.sellPE = Order(obj, SELLPEtoken, SELLPEsymbol, self.qty, 'NFO', 'SELL', 'LIMIT', 'CARRYFORWARD')

        #Placing orders
        #if obj.rmsLimit()['data']['availablecash']/50000 >= self.qty
        bce = ex.submit(self.buyCE.fillinTsec, 9)
        bpe = ex.submit(self.buyPE.fillinTsec, 9)
        bce_status = bce.result()
        bpe_status = bpe.result()
        if bce_status != 0 and bpe_status != 0:#'complete'
            sce = ex.submit(self.sellCE.fillinTsec, 9)
            spe = ex.submit(self.sellPE.fillinTsec, 9)
            sce_status = sce.result()
            spe_status = spe.result()
            time.sleep(1)
            if sce_status != 0 and spe_status != 0:

                sellpeprice = obj.ltpData('NFO',self.sellPE.symbol, self.sellPE.token).get('data').get('ltp')
                sellceprice = obj.ltpData('NFO',self.sellCE.symbol, self.sellCE.token).get('data').get('ltp')
                if slpoints > round(round(sellpeprice*0.3/0.05)*0.05):
                    self.sellPE.SL(round(round(sellpeprice*0.3/0.05)*0.05))
                else:
                    self.sellPE.SL(slpoints)
                if slpoints > round(round(sellceprice*0.3/0.05)*0.05):
                    self.sellCE.SL(round(round(sellceprice*0.3/0.05)*0.05))
                else:
                    self.sellCE.SL(slpoints)
                print("Ironfly-2 deployed")
                self.flag = 1
                rows = [ [self.buyCE.symbol, self.buyCE.token, self.buyCE.OrderId, 0, self.BUYCEStrike, self.straddle_point],
                             [self.buyPE.symbol, self.buyPE.token, self.buyPE.OrderId, 0, self.BUYPEStrike, 0],
                             [self.sellCE.symbol, self.sellCE.token, self.sellCE.OrderId, self.sellCE.OrderIdSL,self.SELLCEStrike, 0],
                             [self.sellPE.symbol, self.sellPE.token, self.sellPE.OrderId, self.sellPE.OrderIdSL,self.SELLPEStrike, 0]
                             ]
                # writing to csv file
                with open("Ironfly2.csv", 'w') as csvfile:
                    # creating a csv writer object
                    csvwriter = csv.writer(csvfile)
                    # writing the fields
                    csvwriter.writerow(fields)
                    # writing the data rows
                    csvwriter.writerows(rows)
        else:
            print("BUY Orders not filled in time")

    def target_and_sl(self):# hunting
        if self.flag == 1:
            # get pnl from postions
            pnl = 0
            df_entries = pd.read_csv("Ironfly2.csv") # Ironfly.csv
            df = pd.DataFrame(obj.position()['data'])
            df['unrealised'] = df['unrealised'].astype('float')
            df['realised'] = df['realised'].astype('float')
            for i, r in df_entries.iterrows():
                unrealised = df[(df['symboltoken'] == str(r['token']))]['unrealised'].iloc[0]
                realised = df[(df['symboltoken'] == str(r['token']))]['realised'].iloc[0]
                pnl = pnl + unrealised + realised

            if (self.adjustmentflag == 0 and pnl > 70*self.qty) or (self.adjustmentflag == 1 and pnl > 40*self.qty): # 2000 per lot
                self.exit_all()

                if self.target_hit < 3:
                    self.execute()
                self.target_hit = self.target_hit + 1
                print("Net p&l of Ironfly-2: ", pnl)

    def exit_all(self):
        if self.flag == 1:
            obj.cancelOrder(self.sellPE.OrderIdSL,"NORMAL")
            obj.cancelOrder(self.sellCE.OrderIdSL,"NORMAL")
            self.sellPE.exit()
            self.sellCE.exit()
            self.buyPE.exit()
            self.buyCE.exit()
            self.flag = 0
            print("All positions of Ironfly-2 exited")
        """if self.flag == 1:
            obj.cancelOrder(self.sellPE.OrderIdSL, "NORMAL")
            obj.cancelOrder(self.sellCE.OrderIdSL, "NORMAL")
            sce = ex.submit(self.sellPE.exit)
            spe = ex.submit(self.sellCE.exit)
            sce_status = sce.result()
            spe_status = spe.result()
            bce = ex.submit(self.buyPE.exit)
            bpe = ex.submit(self.buyCE.exit)
            bce_status = bce.result()
            bpe_status = bpe.result()

            self.flag = 0
            print("All positions of Ironfly-2 exited")"""
    def read_entries(self):
        df_entries = pd.read_csv("Ironfly2.csv")
        self.straddle_point = int(float(df_entries['straddlepoint'][0]))
        self.buyCE.symbol = str(df_entries['symbol'][0])
        self.buyCE.token = str(int(df_entries['token'][0]))
        self.buyCE.OrderId = str(int(df_entries['orderid'][0]))
        self.BUYCEStrike = int(float(df_entries['strike'][0]))
        self.buyPE.symbol = str(df_entries['symbol'][1])
        self.buyPE.token = str(int(df_entries['token'][1]))
        self.buyPE.OrderId = str(int(df_entries['orderid'][1]))
        self.BUYPEStrike = int(float(df_entries['strike'][1]))
        self.sellCE.symbol = str(df_entries['symbol'][2])
        self.sellCE.token = str(int(df_entries['token'][2]))
        self.sellCE.OrderId = str(int(df_entries['orderid'][2]))
        self.sellCE.OrderIdSL = str(int(df_entries['SLorderid'][2]))
        self.SELLCEStrike = int(float(df_entries['strike'][2]))
        self.sellPE.symbol = str(df_entries['symbol'][3])
        self.sellPE.token = str(int(df_entries['token'][3]))
        self.sellCE.OrderId = str(int(df_entries['orderid'][3]))
        self.sellPE.OrderIdSL = str(int(df_entries['SLorderid'][3]))
        self.SELLPEStrike = int(float(df_entries['strike'][3]))
        print("Entries updated")
        self.flag = 1
class Creditspread():
    def __init__(self,qty):
        self.qty = qty
        self.flag = 0
    def execute(self):
        bankniftyltp = obj.ltpData('NSE','BANKNIFTY','26009').get('data').get('ltp')
        print("BANKNIFTY LTP: ",bankniftyltp)
        ATMstrike = round(round(bankniftyltp/100)*100)
        print("BANKNIFTY ATM Strike Price: ", ATMstrike)
        #Debit Spread
        self.BUYCEStrike = ATMstrike-200
        self.SELLCEStrike = ATMstrike
        self.BUYPEStrike = ATMstrike+200
        self.SELLPEStrike = ATMstrike

        if datetime.today().strftime('%A') == "Thursday":
            #Strike tokens
            BUYCEtoken = getTokenInfo('NFO','OPTIDX','BANKNIFTY',self.BUYCEStrike,'CE').iloc[1]['token']
            BUYPEtoken = getTokenInfo('NFO','OPTIDX','BANKNIFTY',self.BUYPEStrike,'PE').iloc[1]['token']
            SELLCEtoken = getTokenInfo('NFO','OPTIDX','BANKNIFTY',self.SELLCEStrike,'CE').iloc[1]['token']
            SELLPEtoken = getTokenInfo('NFO','OPTIDX','BANKNIFTY',self.SELLPEStrike,'PE').iloc[1]['token']
            #strike symbols
            BUYCEsymbol = getTokenInfo('NFO','OPTIDX','BANKNIFTY',self.BUYCEStrike,'CE').iloc[1]['symbol']
            BUYPEsymbol = getTokenInfo('NFO','OPTIDX','BANKNIFTY',self.BUYPEStrike,'PE').iloc[1]['symbol']
            SELLCEsymbol = getTokenInfo('NFO','OPTIDX','BANKNIFTY',self.SELLCEStrike,'CE').iloc[1]['symbol']
            SELLPEsymbol = getTokenInfo('NFO','OPTIDX','BANKNIFTY',self.SELLPEStrike,'PE').iloc[1]['symbol']
        else:
            #Strike tokens
            BUYCEtoken = getTokenInfo('NFO','OPTIDX','BANKNIFTY', self.BUYCEStrike,'CE').iloc[0]['token']
            BUYPEtoken = getTokenInfo('NFO','OPTIDX','BANKNIFTY', self.BUYPEStrike,'PE').iloc[0]['token']
            SELLCEtoken = getTokenInfo('NFO','OPTIDX','BANKNIFTY', self.SELLCEStrike,'CE').iloc[0]['token']
            SELLPEtoken = getTokenInfo('NFO','OPTIDX','BANKNIFTY', self.SELLPEStrike,'PE').iloc[0]['token']
            #strike symbols
            BUYCEsymbol = getTokenInfo('NFO','OPTIDX','BANKNIFTY', self.BUYCEStrike,'CE').iloc[0]['symbol']
            BUYPEsymbol = getTokenInfo('NFO','OPTIDX','BANKNIFTY', self.BUYPEStrike,'PE').iloc[0]['symbol']
            SELLCEsymbol = getTokenInfo('NFO','OPTIDX','BANKNIFTY', self.SELLCEStrike,'CE').iloc[0]['symbol']
            SELLPEsymbol = getTokenInfo('NFO','OPTIDX','BANKNIFTY', self.SELLPEStrike,'PE').iloc[0]['symbol']
        #Creating object for orders
        self.buyCE = Order(obj, BUYCEtoken, BUYCEsymbol, self.qty, 'NFO', 'BUY', 'LIMIT','CARRYFORWARD')
        self.buyPE = Order(obj, BUYPEtoken, BUYPEsymbol, self.qty, 'NFO', 'BUY', 'LIMIT', 'CARRYFORWARD')
        self.sellCE = Order(obj, SELLCEtoken, SELLCEsymbol, self.qty, 'NFO', 'SELL', 'LIMIT', 'CARRYFORWARD')
        self.sellPE = Order(obj, SELLPEtoken, SELLPEsymbol, self.qty, 'NFO', 'SELL', 'LIMIT', 'CARRYFORWARD')

        #Check for direction
        NFtoken = getTokenInfo('NFO','FUTIDX','NIFTY',38000,'CE').iloc[0]['token']
        NFsymbol = getTokenInfo('NFO','FUTIDX','NIFTY',38000,'CE').iloc[0]['symbol']
        ncandleopen = pd.DataFrame(todayscandle(NFtoken,'NFO')['data']).iloc[0,1]
        nfltp = obj.ltpData('NFO',NFsymbol,NFtoken).get('data').get('ltp')

        #Check for direction
        BNFtoken = getTokenInfo('NFO','FUTIDX','BANKNIFTY',38000,'CE').iloc[0]['token']
        BNFsymbol = getTokenInfo('NFO','FUTIDX','BANKNIFTY',38000,'CE').iloc[0]['symbol']
        bncandleopen = pd.DataFrame(todayscandle(BNFtoken,'NFO')['data']).iloc[0,1]
        bnfltp = obj.ltpData('NFO',BNFsymbol,BNFtoken).get('data').get('ltp')
        #Placing orders
        if ncandleopen/nfltp < 0.9975 and bncandleopen/bnfltp < 0.9975:
            #time.sleep(1)
            if self.buyCE.fillinTsec(18) != 0:
                self.sellCE.fillinTsec(18)
                print("Spread created")
            else:
                print("BUY Order not filled in time")
        elif ncandleopen/nfltp > 1.0025 and bncandleopen/bnfltp > 1.0025:
            #time.sleep(1)
            if self.buyPE.fillinTsec(18) != 0:
                self.sellPE.fillinTsec(18)
                print("Spread created")
            else:
                print("BUY Order not filled in time")
        else:
            print("No spread created")

def ironfly_adjustments():
    orders = obj.orderBook()['data']
    dfo = pd.DataFrame(orders)
    def orderstatus(orderId, dfo = dfo):
        try:
            return dfo[(dfo['orderid'] == orderId)]['status'].iloc[0]
        except:
            print("Error in order status of adjustments")
    niftyltp = obj.ltpData('NSE', 'NIFTY', '26000').get('data').get('ltp')

    # SL modifying
    if ironfly1.flag == 1 and ironfly1.adjustmentflag == 0:
        if ironfly1.straddle_point == 0:
            ironfly1.straddle_point = ironfly1.SELLCEStrike
        if niftyltp > ironfly1.straddle_point:
            if orderstatus(ironfly1.sellPE.OrderIdSL) == 'complete':
                sellceprice = obj.ltpData('NFO',ironfly1.sellCE.symbol, ironfly1.sellCE.token).get('data').get('ltp')
                slpercentage = round(round(sellceprice*0.3/0.05)*0.05)
                if slpoints > slpercentage:
                    sl = sellceprice + slpercentage
                else:
                    sl = sellceprice + slpoints
                modify_sl(obj, ironfly1.sellCE.token, ironfly1.sellCE.symbol, ironfly1.sellCE.qty,ironfly1.sellCE.exch_seg, ironfly1.sellCE.buy_sell,"STOPLOSS_LIMIT", sl, ironfly1.sellCE.OrderIdSL,ironfly1.sellCE.producttype)
                print(ironfly1.sellCE.symbol,' SL modified')
                ironfly1.adjustmentflag = 1
        elif niftyltp < ironfly1.straddle_point:
            if orderstatus(ironfly1.sellCE.OrderIdSL) == 'complete':
                sellpeprice = obj.ltpData('NFO',ironfly1.sellPE.symbol, ironfly1.sellPE.token).get('data').get('ltp')
                slpercentage = round(round(sellpeprice*0.3/0.05)*0.05)
                if slpoints > slpercentage:
                    sl = sellpeprice + slpercentage
                else:
                    sl = sellpeprice + slpoints
                modify_sl(obj, ironfly1.sellPE.token, ironfly1.sellPE.symbol, ironfly1.sellPE.qty,ironfly1.sellPE.exch_seg, ironfly1.sellPE.buy_sell,"STOPLOSS_LIMIT", sl, ironfly1.sellPE.OrderIdSL,ironfly1.sellPE.producttype)
                print(ironfly1.sellPE.symbol,' SL modified')
                ironfly1.adjustmentflag = 1

    if ironfly2.flag == 1 and ironfly2.adjustmentflag == 0:
        if ironfly2.straddle_point == 0:
            ironfly2.straddle_point = ironfly2.SELLCEStrike
        if niftyltp > ironfly2.straddle_point:
            if orderstatus(ironfly2.sellPE.OrderIdSL) == 'complete':
                sellceprice = obj.ltpData('NFO',ironfly2.sellCE.symbol, ironfly2.sellCE.token).get('data').get('ltp')
                slpercentage = round(round(sellceprice*0.3/0.05)*0.05)
                if slpoints > slpercentage:
                    sl = sellceprice + slpercentage
                else:
                    sl = sellceprice + slpoints
                modify_sl(obj, ironfly2.sellCE.token, ironfly2.sellCE.symbol, ironfly2.sellCE.qty,ironfly2.sellCE.exch_seg, ironfly2.sellCE.buy_sell,"STOPLOSS_LIMIT", sl, ironfly2.sellCE.OrderIdSL,ironfly2.sellCE.producttype)
                print(ironfly2.sellCE.symbol,' SL modified')
                ironfly2.adjustmentflag = 1
        elif niftyltp < ironfly2.straddle_point:
            if orderstatus(ironfly2.sellCE.OrderIdSL) == 'complete':
                sellpeprice = obj.ltpData('NFO',ironfly2.sellPE.symbol, ironfly2.sellPE.token).get('data').get('ltp')
                slpercentage = round(round(sellpeprice*0.3/0.05)*0.05)
                if slpoints > slpercentage:
                    sl = sellpeprice + slpercentage
                else:
                    sl = sellpeprice + slpoints
                modify_sl(obj, ironfly2.sellPE.token, ironfly2.sellPE.symbol, ironfly2.sellPE.qty,ironfly2.sellPE.exch_seg, ironfly2.sellPE.buy_sell,"STOPLOSS_LIMIT", sl, ironfly2.sellPE.OrderIdSL,ironfly2.sellPE.producttype)
                print(ironfly2.sellPE.symbol,' SL modified')
                ironfly2.adjustmentflag = 1

    # Adjustments
    if ironfly1.flag == 1 and ironfly2.flag == 0 and (orderstatus(ironfly1.sellPE.OrderIdSL) == 'complete' or orderstatus(ironfly1.sellCE.OrderIdSL) == 'complete'):
        print("*-----------------------------------------*")
        ironfly2.execute()
        print("Ironfly - 2")

    elif ironfly2.flag == 1 and ironfly1.flag == 0 and (orderstatus(ironfly2.sellPE.OrderIdSL) == 'complete' or orderstatus(ironfly2.sellCE.OrderIdSL) == 'complete'):
        print("*-----------------------------------------*")
        ironfly1.execute()
        print("Ironfly - 1")

    elif ironfly1.flag == 1 and ironfly2.flag == 1 and orderstatus(ironfly1.sellCE.OrderIdSL) == 'complete' and orderstatus(ironfly2.sellCE.OrderIdSL) == 'complete':
        if orderstatus(ironfly1.sellPE.OrderIdSL) == 'complete':
            ironfly1.buyPE.exit()
            ironfly1.buyCE.exit()
            print("*-----------------------------------------*")
            ironfly1.execute()
        elif orderstatus(ironfly2.sellPE.OrderIdSL) == 'complete':
            ironfly2.buyPE.exit()
            ironfly2.buyCE.exit()
            print("*-----------------------------------------*")
            ironfly2.execute()
        else:
            if ironfly1.SELLCEStrike <= ironfly2.SELLCEStrike:
                ironfly1.exit_all()
                print("*-----------------------------------------*")
                ironfly1.execute()
                print("Ironfly - 1")
            else:
                ironfly2.exit_all()
                print("*-----------------------------------------*")
                ironfly2.execute()
                print("Ironfly - 2")

    elif ironfly2.flag == 1 and ironfly1.flag == 1 and orderstatus(ironfly1.sellPE.OrderIdSL) == 'complete' and orderstatus(ironfly2.sellPE.OrderIdSL) == 'complete':
        if orderstatus(ironfly1.sellCE.OrderIdSL) == 'complete':
            ironfly1.buyPE.exit()
            ironfly1.buyCE.exit()
            print("*-----------------------------------------*")
            ironfly1.execute()
        elif orderstatus(ironfly2.sellCE.OrderIdSL) == 'complete':
            ironfly2.buyPE.exit()
            ironfly2.buyCE.exit()
            print("*-----------------------------------------*")
            ironfly2.execute()
        else:
            if ironfly1.SELLPEStrike >= ironfly2.SELLPEStrike:
                ironfly1.exit_all()
                print("*-----------------------------------------*")
                ironfly1.execute()
                print("Ironfly - 1")
            else:
                ironfly2.exit_all()
                print("*-----------------------------------------*")
                ironfly2.execute()
                print("Ironfly - 2")

    elif ironfly2.flag == 1 and ironfly1.flag == 1 and orderstatus(ironfly1.sellPE.OrderIdSL) == 'complete' and orderstatus(ironfly2.sellCE.OrderIdSL) == 'complete' \
            and orderstatus(ironfly1.sellCE.OrderIdSL) != 'complete' and orderstatus(ironfly2.sellPE.OrderIdSL) != 'complete':
        ironfly1.buyPE.exit()
        ironfly1.buyPE.exitflag = 1
        ironfly2.buyCE.exit()
        ironfly2.buyCE.exitflag = 1
        #print("Iron-condor formed")
    elif ironfly2.flag == 1 and ironfly1.flag == 1 and orderstatus(ironfly2.sellPE.OrderIdSL) == 'complete' and orderstatus(ironfly1.sellCE.OrderIdSL) == 'complete' \
            and orderstatus(ironfly2.sellCE.OrderIdSL) != 'complete' and orderstatus(ironfly1.sellPE.OrderIdSL) != 'complete':
        ironfly2.buyPE.exit()
        ironfly2.buyPE.exitflag = 1
        ironfly1.buyCE.exit()
        ironfly1.buyCE.exitflag = 1
        #print("Iron-condor formed")

    # If the SL skips
    if niftyltp > ironfly1.straddle_point+(slpoints*2) and orderstatus(ironfly1.sellCE.OrderIdSL) != 'complete':
        modify_order(obj, ironfly1.sellCE.token, ironfly1.sellCE.symbol, ironfly1.qty, ironfly1.sellCE.exch_seg, 'BUY', 'MARKET', '0', ironfly1.sellCE.OrderIdSL, ironfly1.sellCE.producttype)
    if niftyltp < ironfly1.straddle_point-(slpoints*2) and orderstatus(ironfly1.sellPE.OrderIdSL) != 'complete':
        modify_order(obj, ironfly1.sellPE.token, ironfly1.sellPE.symbol, ironfly1.qty, ironfly1.sellPE.exch_seg, 'BUY','MARKET','0',ironfly1.sellPE.OrderIdSL, ironfly1.sellPE.producttype)
    if niftyltp > ironfly2.straddle_point+(slpoints*2) and orderstatus(ironfly2.sellCE.OrderIdSL) != 'complete':
        modify_order(obj, ironfly2.sellCE.token, ironfly2.sellCE.symbol, ironfly2.qty, ironfly2.sellCE.exch_seg, 'BUY','MARKET','0',ironfly2.sellCE.OrderIdSL, ironfly2.sellCE.producttype)
    if niftyltp < ironfly2.straddle_point-(slpoints*2) and orderstatus(ironfly2.sellPE.OrderIdSL) != 'complete':
        modify_order(obj, ironfly2.sellPE.token, ironfly2.sellPE.symbol, ironfly2.qty, ironfly2.sellPE.exch_seg, 'BUY','MARKET','0',ironfly2.sellPE.OrderIdSL, ironfly2.sellPE.producttype)
def portfolio_sl():
    try:
        # get pnl from postions
        pnl = 0
        df = pd.DataFrame(obj.position()['data'])
        df['unrealised'] = df['unrealised'].astype('float')
        df['realised'] = df['realised'].astype('float')
        unrealised = df['unrealised'].sum()
        realised = df['realised'].sum()
        pnl = pnl + unrealised + realised
        if pnl < portfolio_sl_amount:
            print("Portfolio SL HIT")
            exit_all_positions()
            cancel_all_orders()

            print("Net Loss:", pnl)
    except:
        print("Error in portfolio SL")
def cancel_all_sl_orders():
    try:
        obj.cancelOrder(ironfly1.sellPE.OrderIdSL,"NORMAL")
        obj.cancelOrder(ironfly1.sellCE.OrderIdSL,"NORMAL")
        obj.cancelOrder(ironfly2.sellPE.OrderIdSL,"NORMAL")
        obj.cancelOrder(ironfly2.sellCE.OrderIdSL,"NORMAL")
    except:
        print("Error while cancelling SL orders")
# field names
fields = ['symbol', 'token', 'orderid', 'SLorderid', 'strike', 'straddlepoint']
# name of csv file
#filename = "Ironcondor.csv"

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
    time.sleep(0.5)

    intializeSymbolTokenMap()
    lot = 50
    time.sleep(0.5)

    # Creating Object for Strategies
    ex = concurrent.futures.ThreadPoolExecutor()

    portfolio_sl_amount = -3000*2
    slpoints = 60 # must be less than 30%
    ironfly1 = Ironfly1(lot*2)
    ironfly2 = Ironfly2(lot*2)
    creditspread = Creditspread(lot*3)

# execute OR read_entries, NOT BOTH
    #ironfly1.execute()
    #ironfly2.execute()
    #creditspread.execute()

    #ironfly1.read_entries() # ONLY if there are active positions # to adjust positions
    #ironfly1.adjustmentflag = 1 # If SL got modified

    #ironfly2.read_entries() # ONLY if there are active positions # to adjust positions
    #ironfly2.adjustmentflag = 1 # If SL got modified

    exit_all_positions()


# Quick Actions

    #cancel_all_orders()
    #ironfly1.exit_all() # read entries first
    #ironfly2.exit_all() # read entries first

# Scheduling
    schedule.every().day.at("09:16").do(exit_all_positions)

    schedule.every().day.at("09:30").do(ironfly1.execute)

    schedule.every(10).seconds.do(ironfly_adjustments)


    schedule.every().day.at("15:25").do(exit_all_positions)
    schedule.every().day.at("15:27").do(cancel_all_sl_orders)

    #schedule.every().day.at("15:25").do(creditspread.execute)

    schedule.every(30).seconds.do(portfolio_sl)

    while True:
    # Checks whether a scheduled task
    # is pending to run or not
        schedule.run_pending()
        time.sleep(1)

    #logout

