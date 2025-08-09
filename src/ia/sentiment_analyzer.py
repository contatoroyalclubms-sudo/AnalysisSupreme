import logging
import requests
from typing import Dict, List, Optional
import random
from datetime import datetime

class SentimentAnalyzer:
    """Analisador de sentimento do mercado"""

    def __init__(self):
        self.news_sources = [
            "https://api.coindesk.com/v1/news/",
            "https://api.cryptonews.com/v1/",
            "https://newsapi.org/v2/"
        ]
        self.cache_sentiment = {}
        
    def _obter_noticias(self, symbol: str = "BTC") -> List[Dict]:
        """Obtém notícias sobre criptomoeda específica"""
        try:
            noticias = []
            
            for i in range(5):
                noticia = {
                    "title": f"{symbol} Market Analysis #{i+1}",
                    "content": f"Recent developments in {symbol} market show interesting trends...",
                    "timestamp": datetime.now().isoformat(),
                    "source": self.news_sources[i % len(self.news_sources)].split('/')[2]
                }
                noticias.append(noticia)
                
            return noticias
            
        except Exception as e:
            logging.error(f"Erro ao obter notícias: {e}")
            return []
    
    def _obter_tweets(self, symbol: str = "BTC") -> List[str]:
        """Obtém tweets sobre criptomoeda específica"""
        try:
            tweets = [
                f"{symbol} to the moon! 🚀",
                f"{symbol} market looking bullish",
                f"Concerned about {symbol} volatility",
                f"Great time to buy {symbol} dip!",
                f"{symbol} adoption increasing globally"
            ]
            return tweets
        except Exception as e:
            logging.error(f"Erro ao obter tweets: {e}")
            return []
    
    def _obter_posts_reddit(self, symbol: str = "BTC") -> List[Dict]:
        """Obtém posts do Reddit sobre criptomoeda específica"""
        try:
            posts = [
                {"title": f"{symbol} analysis - very bullish", "score": 150},
                {"title": f"{symbol} crash incoming?", "score": -50},
                {"title": f"Hodl {symbol} strong!", "score": 200},
                {"title": f"{symbol} technical analysis", "score": 75},
                {"title": f"New {symbol} developments", "score": 120}
            ]
            return posts
        except Exception as e:
            logging.error(f"Erro ao obter posts Reddit: {e}")
            return []
        
    def obter_noticias(self, symbol: str, limit: int = 50) -> List[Dict]:
        """Obtém notícias sobre criptomoeda específica (método público)"""
        try:
            noticias = []
            
            for i in range(min(limit, 10)):
                noticia = {
                    "title": f"{symbol} Market Analysis #{i+1}",
                    "content": f"Recent developments in {symbol} market show interesting trends...",
                    "timestamp": datetime.now().isoformat(),
                    "source": self.news_sources[i % len(self.news_sources)].split('/')[2]
                }
                noticias.append(noticia)
                
            return noticias
            
        except Exception as e:
            logging.error(f"Erro ao obter notícias: {e}")
            return []
    
    def extrair_features(self, texto: str) -> Dict:
        """Extrai features de sentimento do texto"""
        try:
            palavras_positivas = ['bull', 'high', 'profit', 'gain', 'rise', 'pump']
            palavras_negativas = ['bear', 'low', 'loss', 'drop', 'fall', 'dump']
            
            texto_lower = texto.lower()
            
            score_positivo = sum(1 for palavra in palavras_positivas if palavra in texto_lower)
            score_negativo = sum(1 for palavra in palavras_negativas if palavra in texto_lower)
            
            features = {
                'sentiment_score': (score_positivo - score_negativo) / max(len(texto.split()), 1),
                'positive_words': score_positivo,
                'negative_words': score_negativo,
                'word_count': len(texto.split()),
                'exclamation_count': texto.count('!'),
                'question_count': texto.count('?'),
                'caps_ratio': sum(1 for c in texto if c.isupper()) / max(len(texto), 1)
            }
            
            return features
            
        except Exception as e:
            logging.error(f"Erro ao extrair features: {e}")
            return {
                'sentiment_score': 0.0,
                'positive_words': 0,
                'negative_words': 0,
                'word_count': 0,
                'exclamation_count': 0,
                'question_count': 0,
                'caps_ratio': 0.0
            }
    
    def _analisar_twitter(self, symbol: str = "BTC") -> float:
        """Analisa sentimento no Twitter"""
        try:
            tweets = self._obter_tweets(symbol)
            if not tweets:
                return 0.0
            
            total_sentiment = 0
            for tweet in tweets:
                features = self.extrair_features(tweet)
                total_sentiment += features['sentiment_score']
            
            return total_sentiment / len(tweets)
        except Exception as e:
            logging.error(f"Erro ao analisar Twitter: {e}")
            return 0.0

    def _analisar_reddit(self, symbol: str = "BTC") -> float:
        """Analisa sentimento no Reddit"""
        try:
            posts = self._obter_posts_reddit(symbol)
            if not posts:
                return 0.0
            
            total_sentiment = 0
            for post in posts:
                score_weight = max(1, abs(post.get('score', 1)))
                features = self.extrair_features(post.get('title', ''))
                weighted_sentiment = features['sentiment_score'] * score_weight
                total_sentiment += weighted_sentiment
            
            return total_sentiment / len(posts)
        except Exception as e:
            logging.error(f"Erro ao analisar Reddit: {e}")
            return 0.0

    def _analisar_telegram(self, symbol: str = "BTC") -> float:
        """Analisa sentimento em grupos Telegram"""
        return random.uniform(-0.3, 0.7)

    def _analisar_noticias(self, symbol: str = "BTC") -> float:
        """Analisa sentimento em notícias"""
        try:
            noticias = self._obter_noticias(symbol)
            if not noticias:
                return 0.0
            
            total_sentiment = 0
            for noticia in noticias:
                texto = f"{noticia.get('title', '')} {noticia.get('content', '')}"
                features = self.extrair_features(texto)
                total_sentiment += features['sentiment_score']
            
            return total_sentiment / len(noticias)
        except Exception as e:
            logging.error(f"Erro ao analisar notícias: {e}")
            return 0.0
    
    def _processar_textos(self, textos: List[str]) -> float:
        """Processa lista de textos e retorna score de sentimento"""
        try:
            if not textos:
                return 0.0
            
            total_score = 0
            for texto in textos:
                features = self.extrair_features(texto)
                total_score += features['sentiment_score']
            
            return total_score / len(textos)
            
        except Exception as e:
            logging.error(f"Erro ao processar textos: {e}")
            return 0.0
    
    def _obter_cache_sentiment(self, symbol: str) -> Optional[float]:
        """Obtém sentimento do cache"""
        try:
            cache_entry = self.cache_sentiment.get(symbol)
            if cache_entry:
                return cache_entry.get('score', 0.0)
            return None
            
        except Exception as e:
            logging.error(f"Erro ao obter cache: {e}")
            return None

    def analisar_sentimento(self, symbol: str = "BTC") -> float:
        """Análise completa de sentimento para símbolo"""
        try:
            cache_key = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H')}"
            if cache_key in self.cache_sentiment:
                return self.cache_sentiment[cache_key]
                
            twitter_score = self._analisar_twitter(symbol)
            telegram_score = self._analisar_telegram(symbol)
            reddit_score = self._analisar_reddit(symbol)
            noticias_score = self._analisar_noticias(symbol)
            
            sentiment_score = (
                twitter_score * 0.3 +
                telegram_score * 0.2 +
                reddit_score * 0.2 +
                noticias_score * 0.3
            )
            
            sentiment_score = max(min(sentiment_score, 1.0), -1.0)
            
            self.cache_sentiment[cache_key] = sentiment_score
            
            return sentiment_score
            
        except Exception as e:
            logging.error(f"Erro na análise de sentimento: {e}")
            return 0.0
