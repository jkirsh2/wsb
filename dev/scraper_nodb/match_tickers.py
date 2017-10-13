from collections import Counter
from random import shuffle

class SymbolFinder:

    def __init__(self, symbol_list, dollar_sign = False):
        self.symbol_list = symbol_list
        self.dollar_sign = dollar_sign

    @staticmethod
    def tokenize(txt):
        return txt.split()

    @staticmethod
    def get_most_common(s):
        shuffle(s)
        return Counter(s).most_common()[0][0]

    @staticmethod
    def clean_tokens(tokens):
        return [x.strip('$') for x in tokens]

    def check_symbol(self, s):
        if self.dollar_sign and (s[0] != '$'):
            return False
        s = s.strip('$')
        if (s == s.upper()) and (len(s) < 5) and not (s.isdigit()):
            return True
        return False

    def filter_symbols(self, tokens):
        return [x for x in tokens if self.check_symbol(x)]

    def lookup_symbols(self, s):
        return [x for x in s if x in self.symbol_list]

    def get_primary_ticker(self, txt):
        tokens = self.tokenize(txt)
        possible_tickers = self.filter_symbols(tokens)
        possible_tickers = self.clean_tokens(possible_tickers)
        tickers = self.lookup_symbols(possible_tickers)
        if len(tickers) > 0:
            return self.get_most_common(tickers)
        return None




