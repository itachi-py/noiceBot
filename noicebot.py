import discord
import os
from dotenv import load_dotenv
import bs4
from bs4 import BeautifulSoup as BS
import yfinance as yf
from urllib.request import urlopen, Request
from discord.ext.tasks import loop
import asyncio
#import gspread
#from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime
from yahoo_fin import stock_info as si
from yahoo_fin import options
from urllib.error import HTTPError
#from fake_useragent import UserAgent
import requests
from requests_html import HTMLSession
import robin_stocks.robinhood as r
import statistics as stat
from tabulate import tabulate
import math



load_dotenv()

from discord.ext import commands, tasks
import datetime


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="$")


@bot.command()
async def reset(ctx):
	global switch
	switch = "off"

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
	await ctx.send("Top news for: " + arg)
	# Print news title, url and publish date
	for news in news_list[:5]:
		#print(news.title.text)
		link_list.append(news.link.text)
		title_list.append(news.title.text)
		date_list.append(news.pubDate.text)
		#print("-"*60)
	for i,j,k in zip(link_list, title_list, date_list):
		output = discord.Embed(title = j, description = k, url = i, color = 0x00ff00)
		await ctx.send(embed = output)


	#bot.add_command(test)

@news.error
async def on_command_error(ctx, error):
	if isinstance(error,  discord.DiscordException):
		await ctx.send("There is a fat mama error. You are probs missing an argument.")

@bot.command()
async def business(ctx):
	while not bot.is_closed():
		news_url="https://news.google.com/news/rss/headlines/section/topic/BUSINESS"
		Client=urlopen(news_url)
		xml_page=Client.read()
		Client.close()

		soup_page=BS(xml_page,"xml")
		news_list=soup_page.findAll("item")
		link_list = []
		title_list = []
		date_list=[]
		for news in news_list[:5]:
			#print(news.title.text)
			link_list.append(news.link.text)
			title_list.append(news.title.text)
			date_list.append(news.pubDate.text)
		for i,j,k in zip(link_list, title_list, date_list):
			output = discord.Embed(title = j, description = k, url = i, color = 0x00ff00)
			await ctx.send(embed = output)
		await asyncio.sleep(43200)

def get_current_price(symbol):
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    return todays_data['Close'][0]
@bot.command()
async def stonk(ctx):
	while not bot.is_closed():
		now = datetime.datetime.now()
		if (now.hour == 13) and (now.minute) == 20:
			await ctx.send("Good morning! Stock market news for today: ")
			news_url="https://news.google.com/rss/search?q=stock+market+news"
			Client=urlopen(news_url)
			xml_page=Client.read()
			Client.close()

			soup_page=BS(xml_page,"xml")
			news_list=soup_page.findAll("item")
			link_list = []
			title_list = []
			date_list=[]
			for news in news_list[:5]:
				#print(news.title.text)
				link_list.append(news.link.text)
				title_list.append(news.title.text)
				date_list.append(news.pubDate.text)
			for i,j,k in zip(link_list, title_list, date_list):
				output = discord.Embed(title = j, description = k, url = i, color = 0x00ff00)
				await ctx.send(embed = output)

			spy = get_current_price("^SPX")
			str_spy = str(round((spy/10), 2))
			spy_output = "Price of S&P 500 is $" + str_spy
			apple = get_current_price("AAPL")
			str_apple = str(round((apple), 2))
			apple_output = "Price of Apple is $" + str_apple
			await ctx.send(spy_output)
			await ctx.send(apple_output)
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
async def octrack(ctx, arg1, arg2, arg3, arg4):
	global switch
	switch = "on"
	while not bot.is_closed():
		df = options.get_calls(str(arg1), str(arg3))
		strike = df['Strike'].values.tolist()
		IV = df['Implied Volatility'].values.tolist()
		price = df['Last Price'].values.tolist()
		y = strike.index(int(arg2))
		x = int(int(arg4) * 60)
		await ctx.send("Call for " + arg1 + " " + arg2 + " strike price on " + arg3)
		await ctx.send("Price: " + str(price[y]))
		await ctx.send("Implied Volatility: " + str(IV[y]))
		now = datetime.datetime.now()
		if (now.hour == 20) and (0 <= now.minute <= int(arg4)):
			await ctx.send("Market is closed. Stopping tracking...")
			break
		elif switch == "off":
			await ctx.send("Tracking reset...")
			break
		else:
			await asyncio.sleep(x)
@octrack.error
async def on_command_error(ctx, error):
	if isinstance(error,  discord.DiscordException):
		await ctx.send("There is a fat mama error. You are probs missing an argument.")
@bot.command()
async def optrack(ctx, arg1, arg2, arg3, arg4):
	global switch
	switch = "on"
	while not bot.is_closed():
		df = options.get_puts(str(arg1), str(arg3))
		strike = df['Strike'].values.tolist()
		IV = df['Implied Volatility'].values.tolist()
		price = df['Last Price'].values.tolist()
		y = strike.index(int(arg2))
		x = int(int(arg4) * 60)
		await ctx.send("Put for " + arg1 + " " + arg2 + " strike price on " + arg3)
		await ctx.send("Price: " + str(price[y]))
		await ctx.send("Implied Volatility: " + str(IV[y]))
		now = datetime.datetime.now()
		if (now.hour == 20) and (0 <= now.minute <= int(arg4)):
			await ctx.send("Market is closed. Stopping tracking...")
		elif switch == "off":
			await ctx.send("Tracking reset...")
			break
		else:
			await asyncio.sleep(x)
@optrack.error
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

