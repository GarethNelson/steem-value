import web
import json
import thread
import requests
import collections
import functools
import time

class memoized(object):
   '''Decorator. Caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned
   (not reevaluated).
   '''
   def __init__(self, func):
      self.func = func
      self.cache = {}
      self.last_update = time.time()
   def __call__(self, *args):
      if not isinstance(args, collections.Hashable):
         # uncacheable. a list, for instance.
         # better to not cache than blow up.
         return self.func(*args)
      if (args in self.cache) and ((time.time()-self.last_update) < (60*5)):  # 5 minutes
         return self.cache[args]
      else:
         self.last_update = time.time()
         value = self.func(*args)
         self.cache[args] = value
         return value
   def __repr__(self):
      '''Return the function's docstring.'''
      return self.func.__doc__
   def __get__(self, obj, objtype):
      '''Support instance methods.'''
      return functools.partial(self.__call__, obj)


urls = (
       '/','index',
       '/exdata.json','exdata_json'
)

app = web.application(urls, globals())

render = web.template.render('templates/')

pairs = (('ltc', 'sbd'),
 ('sbd', 'eur'),
 ('usd', 'cny'),
 ('ltc', 'steem'),
 ('ltc', 'eur'),
 ('btc', 'usd'),
 ('ltc', 'btc'),
 ('ltc', 'cny'),
 ('btc', 'cny'),
 ('btc', 'steem'),
 ('cny', 'eur'),
 ('cny', 'sbd'),
 ('steem', 'cny'),
 ('ltc', 'usd'),
 ('btc', 'sbd'),
 ('usd', 'sbd'),
 ('usd', 'eur'),
 ('steem', 'eur'),
 ('steem', 'sbd'),
 ('btc', 'eur'),
 ('steem', 'usd'))

def get_poloniex_ticker():
    r = requests.get('https://poloniex.com/public?command=returnTicker')
    return r.json()

def get_btce_pair(a,b):
    r = requests.get('https://btc-e.com/api/2/%s_%s/ticker' % (a.lower(), b.lower()))
    return r.json()['ticker']

def get_btce_ticker():
    retval = {}
    for p in (('btc','usd'),('ltc','btc'),('ltc','usd')):
        retval['%s_%s' % (p[0].upper(), p[1].upper())] = get_btce_pair(*p)
    return retval

def get_poloniex_price(ticker,a,b):
    return float(ticker['%s_%s' % (a.upper(),b.upper())]['last'])

def get_btce_price(ticker,a,b):
    return float(ticker['%s_%s' % (a.upper(),b.upper())]['last'])


# i'm not implementing all of the pairs, you can figure it out easily enough
def get_ex_data():
    retval = {}
    p_ticker = get_poloniex_ticker()
    btce_ticker = get_btce_ticker()
    for pair in pairs:
        p_str = '%s_%s' % (pair[0].upper(), pair[1].upper())
        if p_ticker.has_key(p_str):
           retval[p_str] = get_poloniex_price(p_ticker,*pair)
        elif btce_ticker.has_key(p_str):
           retval[p_str] = get_btce_price(btce_ticker,*pair)
    return retval

class exdata_json:
   def GET(self):
       data = get_ex_data()
       return json.dumps(data)


class index:
   def GET(self,name=None):
       pass

if __name__ == "__main__":
   thread.start_new_thread(app.run,())
   input('hit enter to exit\n')
