import threading
import time
import requests
import os
from dotenv import load_dotenv
from modules.BinanceTraderBot import BinanceTraderBot
from binance.client import Client
from Models.StockStartModel import StockStartModel
import logging

# Carrega variáveis do .env
load_dotenv()
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Define o logger
logging.basicConfig(
    filename="src/logs/trading_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Função para enviar alertas via Telegram usando as credenciais do .env
def send_telegram_alert(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"  # Permite formatação em HTML
    }
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print("Erro ao enviar alerta para o Telegram:", response.text)
    return response.json()

# Função auxiliar para monitorar o saldo de BNB e comprar se estiver abaixo do mínimo
def maintain_bnb_balance(minimum_bnb=0.01, check_interval=300):
    """
    Verifica a cada 'check_interval' segundos se o saldo de BNB está abaixo de 'minimum_bnb'.
    Se estiver, utiliza 5% do saldo em USDT para comprar BNB a mercado.
    """
    client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
    while True:
        try:
            account = client.get_account()
            bnb_balance = 0.0
            usdt_balance = 0.0
            for asset in account['balances']:
                if asset['asset'] == 'BNB':
                    bnb_balance = float(asset['free'])
                elif asset['asset'] == 'USDT':
                    usdt_balance = float(asset['free'])
            # Se o saldo de BNB for insuficiente e houver USDT disponível
            if bnb_balance < minimum_bnb and usdt_balance > 10:
                # Define que 5% do saldo em USDT será usado para comprar BNB
                amount_to_spend = usdt_balance * 0.05
                ticker = client.get_symbol_ticker(symbol='BNBUSDT')
                bnb_price = float(ticker['price'])
                quantity = amount_to_spend / bnb_price
                try:
                    order = client.order_market_buy(symbol='BNBUSDT', quantity=quantity)
                    print("Comprado BNB:", order)
                    send_telegram_alert(f"✅ Comprado BNB automaticamente para manter saldo mínimo.\nOrdem: {order}")
                except Exception as e:
                    print("Erro ao comprar BNB:", e)
                    send_telegram_alert(f"❌ Erro ao comprar BNB: {e}")
            time.sleep(check_interval)
        except Exception as e:
            print("Erro no monitor de saldo de BNB:", e)
            time.sleep(check_interval)

from strategies.moving_average_antecipation import getMovingAverageAntecipationTradeStrategy
from strategies.moving_average import getMovingAverageTradeStrategy
# from strategies.vortex_strategy import getVortexTradeStrategy
from strategies.rsi_strategy import getRsiTradeStrategy
from strategies.vortex_strategy import getVortexTradeStrategy
from strategies.ma_rsi_volume_strategy import getMovingAverageRSIVolumeStrategy

# fmt: off
# -------------------------------------------------------------------------------------------------
# 🟢🟢🟢 CONFIGURAÇÕES - PODEM ALTERAR - INÍCIO 🟢🟢🟢

# Estratégia principal (exemplo com Vortex)
MAIN_STRATEGY = getVortexTradeStrategy
MAIN_STRATEGY_ARGS = {}

# Estratégia de fallback (reserva)
FALLBACK_ACTIVATED  = True      
FALLBACK_STRATEGY = getMovingAverageTradeStrategy
FALLBACK_STRATEGY_ARGS = {}

# Ajustes técnicos
ACCEPTABLE_LOSS_PERCENTAGE  = 0
STOP_LOSS_PERCENTAGE        = 3.5
TP_AT_PERCENTAGE =      [2, 4, 8]
TP_AMOUNT_PERCENTAGE =  [50, 50, 100]

# Ajustes de tempo
CANDLE_PERIOD = Client.KLINE_INTERVAL_15MINUTE
TEMPO_ENTRE_TRADES          = 30 * 60
DELAY_ENTRE_ORDENS          = 60 * 60

# Moedas negociadas
XRP_USDT = StockStartModel(
    stockCode="XRP",
    operationCode="XRPUSDT",
    tradedQuantity=3,
    mainStrategy=MAIN_STRATEGY, mainStrategyArgs=MAIN_STRATEGY_ARGS,
    fallbackStrategy=FALLBACK_STRATEGY, fallbackStrategyArgs=FALLBACK_STRATEGY_ARGS,
    candlePeriod=CANDLE_PERIOD, stopLossPercentage=STOP_LOSS_PERCENTAGE,
    tempoEntreTrades=TEMPO_ENTRE_TRADES, delayEntreOrdens=DELAY_ENTRE_ORDENS,
    acceptableLossPercentage=ACCEPTABLE_LOSS_PERCENTAGE,
    fallBackActivated=FALLBACK_ACTIVATED,
    takeProfitAtPercentage=TP_AT_PERCENTAGE,
    takeProfitAmountPercentage=TP_AMOUNT_PERCENTAGE
)

SOL_USDT = StockStartModel(
    stockCode="SOL",
    operationCode="SOLUSDT",
    tradedQuantity=0.1,
    mainStrategy=MAIN_STRATEGY, mainStrategyArgs=MAIN_STRATEGY_ARGS,
    fallbackStrategy=FALLBACK_STRATEGY, fallbackStrategyArgs=FALLBACK_STRATEGY_ARGS,
    candlePeriod=CANDLE_PERIOD, stopLossPercentage=STOP_LOSS_PERCENTAGE,
    tempoEntreTrades=TEMPO_ENTRE_TRADES, delayEntreOrdens=DELAY_ENTRE_ORDENS,
    acceptableLossPercentage=ACCEPTABLE_LOSS_PERCENTAGE,
    fallBackActivated=FALLBACK_ACTIVATED,
    takeProfitAtPercentage=TP_AT_PERCENTAGE,
    takeProfitAmountPercentage=TP_AMOUNT_PERCENTAGE
)

ADA_USDT = StockStartModel(
    stockCode="ADA",
    operationCode="ADAUSDT",
    tradedQuantity=10,
    mainStrategy=MAIN_STRATEGY, mainStrategyArgs=MAIN_STRATEGY_ARGS,
    fallbackStrategy=FALLBACK_STRATEGY, fallbackStrategyArgs=FALLBACK_STRATEGY_ARGS,
    candlePeriod=CANDLE_PERIOD, stopLossPercentage=STOP_LOSS_PERCENTAGE,
    tempoEntreTrades=TEMPO_ENTRE_TRADES, delayEntreOrdens=DELAY_ENTRE_ORDENS,
    acceptableLossPercentage=ACCEPTABLE_LOSS_PERCENTAGE,
    fallBackActivated=FALLBACK_ACTIVATED,
    takeProfitAtPercentage=TP_AT_PERCENTAGE,
    takeProfitAmountPercentage=TP_AMOUNT_PERCENTAGE
)

BTC_USDT = StockStartModel(
    stockCode="BTC",
    operationCode="BTCUSDT",
    tradedQuantity=0.001,
    mainStrategy=MAIN_STRATEGY, mainStrategyArgs=MAIN_STRATEGY_ARGS,
    fallbackStrategy=FALLBACK_STRATEGY, fallbackStrategyArgs=FALLBACK_STRATEGY_ARGS,
    candlePeriod=CANDLE_PERIOD, stopLossPercentage=STOP_LOSS_PERCENTAGE,
    tempoEntreTrades=TEMPO_ENTRE_TRADES, delayEntreOrdens=DELAY_ENTRE_ORDENS,
    acceptableLossPercentage=ACCEPTABLE_LOSS_PERCENTAGE,
    fallBackActivated=FALLBACK_ACTIVATED,
    takeProfitAtPercentage=TP_AT_PERCENTAGE,
    takeProfitAmountPercentage=TP_AMOUNT_PERCENTAGE
)

# Array com as moedas negociadas
stocks_traded_list = [ADA_USDT]

THREAD_LOCK = True  # True = execução sequencial; False = execução simultânea

# 🔴🔴🔴 CONFIGURAÇÕES - FIM 🔴🔴🔴
# -------------------------------------------------------------------------------------------------

# Inicia uma thread para monitorar o saldo de BNB
bnb_thread = threading.Thread(target=maintain_bnb_balance, args=(0.01, 300))
bnb_thread.daemon = True
bnb_thread.start()

# 🔁 LOOP PRINCIPAL

thread_lock = threading.Lock()

def trader_loop(stockStart: StockStartModel):
    MaTrader = BinanceTraderBot(
        stock_code=stockStart.stockCode,
        operation_code=stockStart.operationCode,
        traded_quantity=stockStart.tradedQuantity,
        traded_percentage=stockStart.tradedPercentage,
        candle_period=stockStart.candlePeriod,
        time_to_trade=stockStart.tempoEntreTrades,
        delay_after_order=stockStart.delayEntreOrdens,
        acceptable_loss_percentage=stockStart.acceptableLossPercentage,
        stop_loss_percentage=stockStart.stopLossPercentage,
        fallback_activated=stockStart.fallBackActivated,
        take_profit_at_percentage=stockStart.takeProfitAtPercentage,
        take_profit_amount_percentage=stockStart.takeProfitAmountPercentage,
        main_strategy=stockStart.mainStrategy,
        main_strategy_args=stockStart.mainStrategyArgs,
        fallback_strategy=stockStart.fallbackStrategy,
        fallback_strategy_args=stockStart.fallbackStrategyArgs
    )

    total_executed: int = 1

    while True:
        if THREAD_LOCK:
            with thread_lock:
                print(f"[{MaTrader.operation_code}][{total_executed}] '{MaTrader.operation_code}'")
                MaTrader.execute()
                print(f"^ [{MaTrader.operation_code}][{total_executed}] time_to_sleep = '{MaTrader.time_to_sleep/60:.2f} min'")
                print("------------------------------------------------")
                total_executed += 1
        else:
            print(f"[{MaTrader.operation_code}][{total_executed}] '{MaTrader.operation_code}'")
            MaTrader.execute()
            print(f"^ [{MaTrader.operation_code}][{total_executed}] time_to_sleep = '{MaTrader.time_to_sleep/60:.2f} min'")
            print("------------------------------------------------")
            total_executed += 1
        time.sleep(MaTrader.time_to_sleep)

# Criando e iniciando uma thread para cada ativo
threads = []

for asset in stocks_traded_list:
    thread = threading.Thread(target=trader_loop, args=(asset,))
    thread.daemon = True  # Permite finalizar as threads ao encerrar o programa
    thread.start()
    threads.append(thread)

print("Threads iniciadas para todos os ativos.")

# O programa principal continua executando sem bloquear
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nPrograma encerrado pelo usuário.")
