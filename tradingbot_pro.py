from lbank.api_client import BLOCKHTTPCLIENT
import pandas as pd
from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator
import requests
import json
import sqlite3
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.scrollview import ScrollView
from kivy.uix.togglebutton import ToggleButton
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty

Window.size = (360, 640)

class ChatBot:
    def __init__(self):
        self.responses = {
            "سلام": "سلام داداش عزیزم! 😊 چطور می‌تونم بهت کمک کنم؟",
            "چارت رو تحلیل کن": "بذار چارتت رو نگاه کنم... قیمت ADA/USDT الان 0.7070 هست. RSI نزدیک اشباع فروشه (حدود 30-40)، که می‌تونه نشون‌دهنده یه برگشت به سمت بالا باشه. ولی MACD هنوز نزولیه و قیمت زیر MA قرار داره. به نظرم اگه قیمت از MA رد بشه و MACD یه تقاطع صعودی نشون بده، می‌تونی برای خرید اقدام کنی. نظرت چیه؟",
            "استراتژی ترید": "یه استراتژی خوب می‌تونه این باشه: صبر کن تا RSI از اشباع فروش خارج بشه و MACD یه تقاطع صعودی نشون بده. بعد با مدیریت ریسک (مثلاً 2% از سرمایه‌ت) وارد معامله بشی. همیشه استاپ‌لاس (Stop Loss) بذار که ضررت محدود بشه. می‌خوای بیشتر توضیح بدم؟",
            "بازار چطوره؟": "بازار الان یه کم نوسان داره. ADA/USDT تو روند نزولی کوتاه‌مدته، ولی اگه اخبار مثبتی بیاد یا حجم معاملات بالا بره، می‌تونه صعودی بشه. اخبار رو هم چک کن!",
            "بای": "بای داداش! 😘 اگه بازم سؤالی داشتی، برگرد پیشم!"
        }

    def get_response(self, message):
        message = message.lower().strip()
        for key in self.responses:
            if key in message:
                return self.responses[key]
        return "متوجه سؤالت نشدم. می‌تونی بیشتر توضیح بدی؟ 😊"

class TradingBotProApp(App):
    bg_color = ListProperty([0.1, 0.1, 0.1, 1])

    def build(self):
        self.db_setup()
        self.root = BoxLayout(orientation="vertical")
        self.show_splash_screen()
        return self.root

    def db_setup(self):
        conn = sqlite3.connect("trading_data.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS market_data
                          (symbol TEXT, timeframe TEXT, signal TEXT, rsi REAL, macd REAL)''')
        conn.commit()
        conn.close()

    def get_trading_pairs(self):
        api_key = "YOUR_API_KEY"
        api_secret = "YOUR_API_SECRET"
        client = BLOCKHTTPCLIENT(api_key, api_secret)
        response = client.get("currencyPairs.do")
        pairs_data = response.get("pairs", [])
        return [pair for pair in pairs_data]

    def fetch_news(self):
        url = "https://newsapi.org/v2/everything?q=cryptocurrency&apiKey=YOUR_NEWS_API_KEY"
        response = requests.get(url)
        news_data = response.json()
        articles = news_data.get("articles", [])
        news_text = ""
        sentiment_score = 0
        for article in articles[:5]:
            title = article.get("title", "No Title")
            news_text += f"- {title}\n"
            sentiment_score += 1 if "positive" in title.lower() else -1 if "negative" in title.lower() else 0
        sentiment = "Bullish" if sentiment_score > 0 else "Bearish" if sentiment_score < 0 else "Neutral"
        return news_text, sentiment

    def analyze_market(self, symbol):
        api_key = "YOUR_API_KEY"
        api_secret = "YOUR_API_SECRET"
        client = BLOCKHTTPCLIENT(api_key, api_secret)
        response = client.get("kline.do", symbol=symbol, type="hour1", size=100)
        kline_data = response.get("data", [])
        if not kline_data:
            return "No data available", "N/A"

        df = pd.DataFrame(kline_data, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["close"] = df["close"].astype(float)

        sma = SMAIndicator(df["close"], window=20).sma_indicator()
        macd = MACD(df["close"]).macd()
        rsi = RSIIndicator(df["close"]).rsi()

        latest_sma = sma.iloc[-1]
        latest_macd = macd.iloc[-1]
        latest_rsi = rsi.iloc[-1]

        analysis = f"SMA: {latest_sma:.2f}\nMACD: {latest_macd:.4f}\nRSI: {latest_rsi:.2f}"
        signal = "Buy" if latest_rsi < 30 and latest_macd > 0 else "Sell" if latest_rsi > 70 and latest_macd < 0 else "Hold"

        conn = sqlite3.connect("trading_data.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO market_data (symbol, timeframe, signal, rsi, macd) VALUES (?, ?, ?, ?, ?)",
                       (symbol, "1h", signal, latest_rsi, latest_macd))
        conn.commit()
        conn.close()

        return analysis, signal

    def show_splash_screen(self):
        splash_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        splash_label = Label(text="TradingBot Pro\nLoading...", font_size=30, halign="center")
        start_button = Button(text="Start", size_hint=(1, 0.2))
        start_button.bind(on_press=lambda x: self.show_main_screen(0))
        splash_layout.add_widget(splash_label)
        splash_layout.add_widget(start_button)
        self.root.add_widget(splash_layout)

    def show_main_screen(self, dt):
        self.tab_panel = TabbedPanel(do_default_tab=False)

        market_tab = TabbedPanelItem(text="Market Analysis")
        self.market_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        self.symbol_spinner = Spinner(text="Select Symbol", values=self.get_trading_pairs())
        self.analyze_button = Button(text="Analyze", size_hint=(1, 0.2))
        self.analyze_button.bind(on_press=self.start_analysis)
        self.result_label = Label(text="Analysis results will appear here", size_hint=(1, 0.6), halign="left", valign="top")
        self.result_label.bind(size=self.result_label.setter("text_size"))
        self.suggestion_label = Label(text="Suggestions will appear here", size_hint=(1, 0.2), halign="left", valign="top")
        self.suggestion_label.bind(size=self.suggestion_label.setter("text_size"))
        self.market_layout.add_widget(self.symbol_spinner)
        self.market_layout.add_widget(self.analyze_button)
        self.market_layout.add_widget(self.result_label)
        self.market_layout.add_widget(self.suggestion_label)
        market_tab.add_widget(self.market_layout)

        news_tab = TabbedPanelItem(text="Crypto News")
        self.news_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        self.news_button = Button(text="Fetch News", size_hint=(1, 0.2))
        self.news_button.bind(on_press=self.start_fetch_news)
        self.sentiment_label = Label(text="Market Sentiment: N/A", size_hint=(1, 0.1))
        self.news_scroll = ScrollView()
        self.news_label = Label(text="News will appear here", size_hint_y=None, height=dp(1000), halign="left", valign="top")
        self.news_label.bind(size=self.news_label.setter("text_size"))
        self.news_scroll.add_widget(self.news_label)
        self.news_layout.add_widget(self.news_button)
        self.news_layout.add_widget(self.sentiment_label)
        self.news_layout.add_widget(self.news_scroll)
        news_tab.add_widget(self.news_layout)

        settings_tab = TabbedPanelItem(text="Settings")
        settings_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        theme_button = ToggleButton(text="Toggle Theme (Dark/Light)", state="normal", size_hint=(1, 0.2))
        theme_button.bind(on_press=self.toggle_theme)
        settings_layout.add_widget(theme_button)
        settings_tab.add_widget(settings_layout)

        self.tab_panel.add_widget(market_tab)
        self.tab_panel.add_widget(news_tab)
        self.tab_panel.add_widget(settings_tab)

        self.add_chat_tab()

        with self.tab_panel.canvas.before:
            self.bg = Color(*self.bg_color)
            self.bg_rect = Rectangle(pos=self.tab_panel.pos, size=self.tab_panel.size)
        self.tab_panel.bind(pos=self.update_bg, size=self.update_bg)

        self.root.clear_widgets()
        self.root.add_widget(self.tab_panel)

    def add_chat_tab(self):
        chat_tab = TabbedPanelItem(text="Chat with AI")
        self.chat_layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        self.chat_scroll = ScrollView()
        self.chat_label = Label(text="سلام! من هوش مصنوعی رباتتم. باهام حرف بزن! 😊", size_hint_y=None, height=dp(1000), halign="left", valign="top")
        self.chat_label.bind(size=self.chat_label.setter("text_size"))
        self.chat_scroll.add_widget(self.chat_label)
        self.chat_input = TextInput(hint_text="پیامت رو اینجا بنویس...", size_hint=(1, 0.1), multiline=False)
        self.chat_input.bind(on_text_validate=self.send_message)
        send_button = Button(text="Send", size_hint=(1, 0.1))
        send_button.bind(on_press=self.send_message)
        self.chat_layout.add_widget(self.chat_scroll)
        self.chat_layout.add_widget(self.chat_input)
        self.chat_layout.add_widget(send_button)
        chat_tab.add_widget(self.chat_layout)
        self.tab_panel.add_widget(chat_tab)

    def send_message(self, instance):
        message = self.chat_input.text
        if not message:
            return
        self.chat_label.text += f"\n\nYou: {message}"
        chatbot = ChatBot()
        response = chatbot.get_response(message)
        self.chat_label.text += f"\n\nAI: {response}"
        self.chat_input.text = ""
        self.chat_scroll.scroll_y = 0

    def start_analysis(self, instance):
        symbol = self.symbol_spinner.text
        if symbol == "Select Symbol":
            self.result_label.text = "Please select a symbol!"
            return
        analysis, signal = self.analyze_market(symbol)
        self.result_label.text = analysis
        self.suggestion_label.text = f"Suggestion: {signal}"

    def start_fetch_news(self, instance):
        news_text, sentiment = self.fetch_news()
        self.news_label.text = news_text
        self.sentiment_label.text = f"Market Sentiment: {sentiment}"

    def toggle_theme(self, instance):
        if instance.state == "down":
            self.bg_color = [1, 1, 1, 1]
        else:
            self.bg_color = [0.1, 0.1, 0.1, 1]

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

if __name__ == "__main__":
    TradingBotProApp().run()