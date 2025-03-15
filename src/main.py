import threading
import time
import requests
import datetime
import os
from dotenv import load_dotenv
from modules.BinanceTraderBot import BinanceTraderBot
from binance.client import Client
from Models.StockStartModel import StockStartModel
import logging



# Carrega variáveis do .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Define o logger
logging.basicConfig(
    filename="src/logs/trading_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Função para enviar alertas via Telegram
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

# Função para formatar a mensagem com detalhes do trade
def format_telegram_message(MaTrader: BinanceTraderBot, total_executed: int) -> str:
    now = datetime.datetime.now().strftime("(%H:%M:%S) %d-%m-%Y")
    # Utilize atributos do MaTrader, se existentes, ou valores padrão de exemplo
    last_buy_date = getattr(MaTrader, 'last_buy_date', "(15:37:58) 14-03-2025")
    last_buy_price = getattr(MaTrader, 'last_buy_price', "0.7480")
    last_buy_qty = getattr(MaTrader, 'last_buy_qty', "10.0")
    position = getattr(MaTrader, 'position', "Comprado")
    balance = getattr(MaTrader, 'balance', "10.0000 (ADA)")
    current_price = getattr(MaTrader, 'current_price', "0.7408")
    min_sell_price = getattr(MaTrader, 'min_sell_price', "0.7481")
    stop_loss_info = getattr(MaTrader, 'stop_loss_info', "0.7219 (-3.50%)")
    variation = getattr(MaTrader, 'variation', "-0.98%")
    take_profit = getattr(MaTrader, 'take_profit', "2% (Venda de: 50%)")
    strategy_name = getattr(MaTrader, 'strategy_name', "Vortex")
    vi_plus = getattr(MaTrader, 'vi_plus', "1.25")
    vi_minus = getattr(MaTrader, 'vi_minus', "0.79")
    decision = getattr(MaTrader, 'decision', "Comprar")
    final_decision = getattr(MaTrader, 'final_decision', "Comprar")
    final_action = getattr(MaTrader, 'final_action', "Manter posição (Comprado)")

    message = f"""<b>🟢 Executado {now}</b>

<b>Última ordem de COMPRA executada para {MaTrader.operation_code}:</b>
 - <b>Data:</b> {last_buy_date} | <b>Preço:</b> {last_buy_price} | <b>Qnt.:</b> {last_buy_qty}
<b>Ordens de VENDA:</b> Não há ordens de VENDA executadas para {MaTrader.operation_code}.

-------
<b>Detalhes:</b>
 - <b>Posição atual:</b> {position}
 - <b>Balanço atual:</b> {balance}

 - <b>Preço atual:</b> {current_price}
 - <b>Preço mínimo para vender:</b> {min_sell_price}
 - <b>Stop Loss em:</b> {stop_loss_info}

 - <b>Variação atual:</b> {variation}
 - <b>Próxima meta Take Profit:</b> {take_profit}

-------
<b>📊 Estratégia:</b> {strategy_name}
 | <b>VI+:</b> {vi_plus}
 | <b>VI-:</b> {vi_minus}
 | <b>Decisão:</b> {decision}
-------
 - Não há ordens de compra abertas para {MaTrader.operation_code}.

--------------
<b>🔎 Decisão Final:</b> {final_decision}
<b>🏁 Ação final:</b> {final_action}
--------------
------------------------------------------------
^ [{MaTrader.operation_code}][{total_executed}] time_to_sleep = '{MaTrader.time_to_sleep/60:.2f} min'
------------------------------------------------
"""
    return message

from strategies.moving_average_antecipation import getMovingAverageAntecipationTradeStrategy
from strategies.moving_average import getMovingAverageTradeStrategy
# from strategies.vortex_strategy import getVortexTradeStrategy
from strategies.rsi_strategy import getRsiTradeStrategy
from strategies.vortex_strategy import getVortexTradeStrategy
from strategies.ma_rsi_volume_strategy import getMovingAverageRSIVolumeStrategy

# fmt: off
# -------------------------------------------------------------------------------------------------
# 🟢🟢🟢 CONFIGURAÇÕES - PODEM ALTERAR - INÍCIO 🟢🟢🟢

# ------------------------------------------------------------------
# 🚀 AJUSTES DE ESTRATÉGIA 🚀

# 🏆 ESTRATÉGIA PRINCIPAL 🏆

# MAIN_STRATEGY = getMovingAverageAntecipationTradeStrategy
# MAIN_STRATEGY_ARGS = {"volatility_factor": 0.5, "fast_window": 9, "slow_window": 21}

MAIN_STRATEGY = getVortexTradeStrategy
MAIN_STRATEGY_ARGS = {}

# MAIN_STRATEGY = getMovingAverageRSIVolumeStrategy
# MAIN_STRATEGY_ARGS = {"fast_window": 9, "slow_window": 21, "rsi_window": 14, "rsi_overbought": 70, "rsi_oversold": 30, "volume_multiplier": 1.5}

# MAIN_STRATEGY = getRsiTradeStrategy
# MAIN_STRATEGY_ARGS = {}

# -----------------

# 🥈 ESTRATÉGIA DE FALLBACK (reserva) 🥈

FALLBACK_ACTIVATED = True      
FALLBACK_STRATEGY = getMovingAverageTradeStrategy
FALLBACK_STRATEGY_ARGS = {}

# ------------------------------------------------------------------
# 🛠️ AJUSTES TÉCNICOS 🛠️

ACCEPTABLE_LOSS_PERCENTAGE = 0         # (% máximo de perda aceitável)
STOP_LOSS_PERCENTAGE = 2.0             # (% de perda para acionar venda a mercado)

TP_AT_PERCENTAGE = [1, 2, 4]           # Meta de Take Profit (%)
TP_AMOUNT_PERCENTAGE = [50, 50, 100]   # Percentual da posição a vender

# ------------------------------------------------------------------
# ⌛ AJUSTES DE TEMPO

# CANDLE_PERIOD = Client.KLINE_INTERVAL_1HOUR
CANDLE_PERIOD = Client.KLINE_INTERVAL_5MINUTE

TEMPO_ENTRE_TRADES = 5 * 60     # em segundos
DELAY_ENTRE_ORDENS = 5 * 60     # em segundos

# ------------------------------------------------------------------
# 🪙 MOEDAS NEGOCIADAS

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

# Array de moedas negociadas
stocks_traded_list = [XRP_USDT, SOL_USDT, ADA_USDT, BTC_USDT]

THREAD_LOCK = True  # True = execução sequencial; False = execução simultânea

# 🔴🔴🔴 CONFIGURAÇÕES - FIM 🔴🔴🔴
# -------------------------------------------------------------------------------------------------

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
        try:
            # Exibe mensagem no console (opcional)
            print(f"[{MaTrader.operation_code}][{total_executed}] '{MaTrader.operation_code}'")
            MaTrader.execute()
            print(f"^ [{MaTrader.operation_code}][{total_executed}] time_to_sleep = '{MaTrader.time_to_sleep/60:.2f} min'")
            print("------------------------------------------------")
            
            # Formata e envia a mensagem para o Telegram
            message = format_telegram_message(MaTrader, total_executed)
            send_telegram_alert(message)
            
            total_executed += 1
        except Exception as e:
            error_message = f"<b>Erro no trader {MaTrader.operation_code} na execução {total_executed}:</b> {e}"
            send_telegram_alert(error_message)
            print(error_message)
        time.sleep(MaTrader.time_to_sleep)

# Inicia uma thread para cada ativo
threads = []

for asset in stocks_traded_list:
    thread = threading.Thread(target=trader_loop, args=(asset,))
    thread.daemon = True  # Permite encerrar as threads junto com o programa
    thread.start()
    threads.append(thread)

print("Threads iniciadas para todos os ativos.")

# Mantém o programa em execução
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nPrograma encerrado pelo usuário.")
