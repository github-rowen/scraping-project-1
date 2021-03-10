# import all the tools needed for scraping
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

base_url = 'https://books.toscrape.com/catalogue/category/'
# the start url for scraping
start_url = 'https://books.toscrape.com/catalogue/category/books_1/index.html'
# a function to get and parse the content of the url
def get_html(page):
	headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}

	r = requests.get(page, headers=headers)
	#check the status_code of the requests
	return BeautifulSoup(r.content, 'lxml')
	#return the parsed requested url and get the content
# a function to collect all the links of each book category
def get_all_category(url):

	soup = get_html(url)

	books = soup.find('ul', class_='nav nav-list').ul

	#get all the category of the book and
	#store all the url's of different book category to a list
	collected_categories_url = []

	for li in books.find_all('li'):#[:5]limiting the items to loop
		category_page_url = li.a['href'].replace('../','')
		#get the complete url of each category by concatinating base url and category page url
		#store in the categories list
		collected_categories_url.append(base_url + category_page_url)
	return collected_categories_url

book_categories_urls = get_all_category(start_url)
# create empty lists to store the data to be extracted
book_categories = []
names = []
prices = []
availability = []
ratings = []
# loop in book_categories_urls
for page in book_categories_urls:#loop in every page of every book category
	# print(page)
	soup = get_html(page)

	items = soup.find_all('li', class_='col-xs-6 col-sm-4 col-md-3 col-lg-3')
	# check if actual items of the present url page are less than 20

	items_in_item_collected = 0 # for visual checking purposes only

	# check if the items in the page is less than 20
	if len(items) < 20:
		# get the title which is the category of the items
		book_ctgry = soup.find('div', class_='page-header action').h1.text
		for i in range(len(items)):
			book_categories.append(book_ctgry)

		# exctracting the data
		for data in items:
			name = data.find('article', class_='product_pod').h3.a['title']
			names.append(name)
			
			price = data.find('p', class_='price_color').text
			prices.append(price)
			
			available = data.find('p', class_='instock availability').text.strip()
			availability.append(available)
			
			rating = data.find('p', class_='star-rating')['class'][1]
			ratings.append(rating)
				
		items_in_item_collected = len(items) # for visual checking purposes only

	# page has more than 20 items, which means there is next button available
	else:
		next_btn = soup.find('ul', class_='pager').find('li', class_='next')

		# if page have next button
		if next_btn is not None:
			# set the value of page_url to 'page' 
			page_url = page
			# make empty list for the subpages
			collected_url = []

			url_to_check = None
			url_condition = True
			check = True
			index_counter = 0
			
			while check:
				while url_condition:
					# append the first page_url to the collected url list
					collected_url.append(page_url)
					# set the value of url_condition to False
					url_condition = False
				# requests.get again the page which is in the collected_url[index_counter]
				soup = get_html(collected_url[index_counter])

				next_btn = soup.find('ul', class_='pager').find('li', class_='next')
				# print(next_btn.text)

				# if page have next button
				if next_btn is not None:
					# get the value of attribute of href of the next_btn
					page_val = next_btn.a['href']
					# print(page_val)
					# modify the value of the url stored in collected_url
					modified_url = collected_url[index_counter].split('/')
					del modified_url[-1]
					new_url = '/'.join(modified_url) + '/' + page_val
					collected_url.append(new_url)
					# print(new_url)

					# add 1 to the index_counter
					index_counter += 1
				else:
					check = False
			# loop in the collected_url list to extract data of each sub pages in each category that has more than 20 items
			items_in_item_collected = 0
			for item in collected_url:
				soup = get_html(item)

				items = soup.find_all('li', class_='col-xs-6 col-sm-4 col-md-3 col-lg-3')

				book_ctgry = soup.find('div', class_='page-header action').h1.text

				for i in range(len(items)):
					book_categories.append(book_ctgry)

				for data in items:
					name = data.find('article', class_='product_pod').h3.a['title']
					names.append(name)
				
					price = data.find('p', class_='price_color').text
					prices.append(price)
				
					available = data.find('p', class_='instock availability').text.strip()
					availability.append(available)
				
					rating = data.find('p', class_='star-rating')['class'][1]
					ratings.append(rating)
					
				# for visual checking purposes only
				items_in_item_collected += len(items)

				#pause the loop for a random time so that the website will not overloaded by requests
				time.sleep(random.randint(2,6))
		
	# for visual checking purposes only
	print('saving...' + book_ctgry + ' |' + 'total items :' + str(items_in_item_collected))
	#pause the loop for a random time so that the website will not overloaded by requests
	time.sleep(random.randint(2,6))

#make a data frame using pandas DataFrame
df = pd.set_option('max_rows', None, 'max_columns', None)
df = pd.DataFrame({
	'category': book_categories,
	'name': names,
	'price': prices,
	'stock': availability,
	'rating': ratings
	})
# print(df)
df.to_csv('finalVersion.csv', index=False)

print('done!')