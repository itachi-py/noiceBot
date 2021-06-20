import discord
import os
from dotenv import load_dotenv
import bs4 as bs
from bs4 import BeautifulSoup as BS
import yfinance as yf
from urllib.request import urlopen, Request
from discord.ext.tasks import loop
import asyncio
import pandas as pd
import datetime
from yahoo_fin import stock_info as si
from yahoo_fin import options
from urllib.error import HTTPError
import requests
from requests_html import HTMLSession
import robin_stocks.robinhood as r
import statistics as stat
from tabulate import tabulate
import math
import lxml
import praw
import re
from tqdm import tqdm

from praw.models import MoreComments

import nltk

from nltk.sentiment.vader import SentimentIntensityAnalyzer

load_dotenv()

from discord.ext import commands, tasks
import datetime


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="$")

try:
    r = praw.Reddit(client_id = "jB_QBbYNbnfsug", client_secret = "oh0Q-fogfrWlnjQxkrEDvP0Yt7Hm8A", user_agent = "oruc47")
    print("Wow you did it good job, you might amount to something")
except:
    print("Dumbass it doesn't work.")



def hot_posts(subreddit, number):
    page = r.subreddit(subreddit)
    posts = page.hot(limit=number)
    plink = []
    pTitle = []
    comments = []
    cList = []
    urls = []
    for i in posts:
        plink.append(i.permalink)
        pTitle.append(i.title)
    for i in plink:
        link = "https://www.reddit.com/" + str(i)
        urls.append(link)
        sub = r.submission(url = link)
        submission = r.submission(id = sub)
        for comment in submission.comments.list():
            if isinstance(comment, MoreComments):
                continue
            result = comment.body
            comments.append(result)
        cList.append(set(comments))

    return cList, pTitle, urls


def oSent(listoflists):
    polarity = []
    for cList in listoflists:
        polarity.append(SentimentIntensityAnalyzer().polarity_scores(''.join(cList)))
    return polarity

def sCount(ticker, listoflists):
    count = 0
    for cList in listoflists:
        temp = ''.join(cList)
        if str(ticker) in temp:
            count += 1
    return count

def movers():
    link = "http://thestockmarketwatch.com/markets/pre-market/today.aspx"
    req = Request(link, headers = {"User-Agent":'XYZ/3.0'})
    webpage = urlopen(req, timeout = 10).read()
    article = bs.BeautifulSoup(webpage, "lxml")
    percent_list = article.findAll("div", class_ = "chgUp")
    loss_list = article.findAll("div", class_ = "chgDown")
    stock_list = article.findAll("a", class_ = "symbol")
    rP = []
    rT = []
    rL = []

    for percent in percent_list:
        rP.append(percent.text)
    for loss in loss_list:
        rL.append(loss.text)
    for tick in stock_list:
        rT.append(tick.text)
    mega = rP + rL

    x = pd.DataFrame(mega, rT)

    return x[:5].to_string(), x[-5:].to_string()

@bot.command()
async def reddit(ctx, arg1, arg2):
    top = hot_posts(str(arg1), int(arg2))
    sent = oSent(top[0])
    for i, j, k in zip(top[1], sent, top[2]):
        output = discord.Embed(title = i, description = j, url = k)
        await ctx.send(embed = output)
@reddit.error
async def on_command_error(ctx, error):
  if isinstance(error,  discord.DiscordException):
      await ctx.send(error)
@bot.command()
async def rcount(ctx, arg1, arg2, arg3):
    top = hot_posts(str(arg1), int(arg2))
    result = sCount(str(arg3), top[0])
    await ctx.send(str(arg3) + " was found " + str(result) + " times")
@rcount.error
async def on_command_error(ctx, error):
  if isinstance(error,  discord.DiscordException):
      await ctx.send(error)

@bot.command()
async def mover(ctx):
    result = movers()

    await ctx.send(result[0])
    await ctx.send(result[1])


@bot.command()
async def reset(ctx):
    global switch
    switch = False

@bot.command()
async def news(ctx, arg):
    news_url="https://news.google.com/rss/search?q=" + arg
    Client=urlopen(news_url)
    xml_page=Client.read()
    Client.close()

    soup_page=BS(xml_page,"xml")
    news_list=soup_page.findAll("item")
    link_list = []
    title_list = []
    date_list=[]
    sentScores = []
    await ctx.send("Top news for: " + arg)
    for news in news_list[:5]:
        link_list.append(news.link.text)
        title_list.append(news.title.text)
        date_list.append(news.pubDate.text)
    for i in link_list[0:5]:
        link = i
        req = Request(link, headers = {"User-Agent":'XYZ/3.0'})
        webpage = urlopen(req, timeout = 10).read()
        article = bs.BeautifulSoup(webpage, "lxml")
        para = article.findAll("p")
        aText = ""
        for i in para:
            aText += i.text
        sentScores.append(SentimentIntensityAnalyzer().polarity_scores(aText))
    for i,j,k,z in tqdm(zip(link_list, title_list, date_list, sentScores)):
        output = discord.Embed(title = j, description = k, url = i, color = 0x00ff00)
        output.set_footer(text = z)
        await ctx.send(embed = output)
@news.error
async def on_command_error(ctx, error):
    if isinstance(error,  discord.DiscordException):
        await ctx.send(error)

@bot.command()
async def stonk(ctx):
    while not bot.is_closed():
        now = datetime.datetime.now()
        if (now.hour == 13) and (now.minute) == 20:
            news_url="https://news.google.com/rss/search?q=stock+market+news" 
            Client=urlopen(news_url)
            xml_page=Client.read()
            Client.close()

            soup_page=BS(xml_page,"xml")
            news_list=soup_page.findAll("item")
            link_list = []
            title_list = []
            date_list=[]
            sentScores = []
            for news in news_list[:5]:
              link_list.append(news.link.text)
              title_list.append(news.title.text)
              date_list.append(news.pubDate.text)
            for i in link_list[0:5]:
              link = i
              req = Request(link, headers = {"User-Agent":'XYZ/3.0'})
              webpage = urlopen(req, timeout = 10).read()
              article = bs.BeautifulSoup(webpage, "lxml")
              para = article.findAll("p")
              aText = ""
              for i in para:
                  aText += i.text
              sentScores.append(SentimentIntensityAnalyzer().polarity_scores(aText))
            for i,j,k,z in tqdm(zip(link_list, title_list, date_list, sentScores)):
              output = discord.Embed(title = j, description = k, url = i, color = 0x00ff00)
              output.set_footer(text = z)
              await ctx.send(embed = output)
            result = movers()
            await ctx.send("Biggest Movers PreMarket")
            await ctx.send(result[0])
            await ctx.send(result[1])

            break
        else:
            await asyncio.sleep(10)


@bot.command()
async def stop(ctx, arg1, arg2):
    percent = int(arg1)
    price = float(arg2)
    profit = ((1 + (percent/100)) * price)
    loss = ((1 - (percent/100)) * price)
    str_percent = str(round((percent), 2))
    str_price = str(price)
    str_profit = str(profit)
    str_loss = str(loss)
    out_put_1 = "Take " + str_percent + "% profits by selling at " + str_profit
    out_put_2 = "Stop losses at " + str_percent + "% by selling at " + str_loss
    await ctx.send(out_put_1)
    await ctx.send(out_put_2)

@stop.error
async def on_command_error(ctx, error):
    if isinstance(error,  discord.DiscordException):
        await ctx.send("There is a fat mama error. You are probs missing an argument.")


@bot.command()
async def mantra(ctx, arg1):
    await ctx.send("Buddhist Mantra Activated for " + arg1)
    await ctx.send("Dear Goddess Lakshmi and Lord Kubera, I pray to thee! Bless me with prosperity and wealth.")
    await ctx.send("Please make " + arg1 + " go the direction we want it to")


@bot.command()
async def strack(ctx, arg1, arg2):
    global switch
    switch = "on"
    while not bot.is_closed():
        ticker = str(round(si.get_live_price(arg1), 2))
        await ctx.send("Price of $" + arg1 + " is " + ticker)
        x = int(int(arg2) * 60)
        now = datetime.datetime.now()
        if (now.hour == 20) and (0 <= now.minute <= int(arg2)):
            await ctx.send("Market is closed. Stopping tracking...")
            break
        elif switch == "off":
            await ctx.send("Tracking reset...")
            break
        else:
            await asyncio.sleep(x)
@strack.error
async def on_command_error(ctx, error):
    if isinstance(error,  discord.DiscordException):
        await ctx.send("There is a fat mama error. You are probs missing an argument.")
@bot.command()
async def oscreen(ctx, arg1, arg2, arg3, arg4, arg5):
    try:
        login = r.login("straightberry", "Jjk2019Oruc1!")
    except:
        await ctx.send("Robinhood API login failed")

    '''
    arg1 = ticker
    arg2 = base price
    arg3 = call
    arg4 = date
    arg5 = capital
    '''

    price = int(arg2)

    #await ctx.send(price)

    strike = []

    for i in range(0,5):
        price += 1
        str_price = str(price)
        strike.append(str_price)
    #await ctx.send(strike)
    sample = []
    comp_total = 0
    delta_list = []
    theta_list = []
    IV_list = []
    ask_price_list = []
    ip = []
    interest = []
    volume = []

    for i in strike:
        try:
            test = r.options.get_option_market_data(arg1, arg4, i, arg3)
        except:
            await ctx.send("Error in get_option_market_data. ur an idiot")  
        delta = float(test[0][0]['delta'])
        delta_list.append(delta)
        gamma = float(test[0][0]['gamma'])
        IV = 1 - float(test[0][0]['implied_volatility'])
        IV_list.append(float(test[0][0]['implied_volatility']))
        theta = 1 - float(test[0][0]['theta'])
        theta_list.append(float(test[0][0]['theta']))
        price = float(test[0][0]['ask_price'])
        ask_price_list.append(price)
        #await ctx.send(float(arg5))
        multiplier = math.floor(float(arg5) / (price*100))
        #await ctx.send(multiplier)
        i_total = multiplier * (price * 100)
        #await ctx.send(i_total)
        percent = i_total / (float(arg5))
        #await ctx.send(percent)
        ip.append(percent)
        compound = (price)/(delta + gamma + IV + theta)
        comp_total += compound
        sample.append(compound)
        oi = test[0][0]['open_interest']
        interest.append(oi)
        vol = test[0][0]['volume']
        volume.append(vol)

    #await ctx.send(sample)
    mean = comp_total/5
    var = stat.stdev(sample)

    for i,j in zip(strike,sample):
        z = (j - mean)/var
        #await ctx.send("Z-Score Appoximation for $" + i)
        #await ctx.send(z)

    table = zip(strike, sample, delta_list, theta_list, IV_list, ask_price_list, ip, interest, volume)
    headers = ['Stirke Price', 'Z-Score', 'Delta', 'Theta', 'IV', "Price", "Percent", "OI", "Volume"]
    await ctx.send(tabulate(table, headers=headers, floatfmt=".2f", tablefmt="simple", numalign="right", stralign = "right"))
    await ctx.send(table)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')



bot.run(DISCORD_TOKEN)

