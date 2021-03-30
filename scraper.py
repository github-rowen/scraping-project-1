from bs4 import BeautifulSoup
import requests
import pandas as pd
import time

base_url = 'https://books.toscrape.com/'
url ='https://books.toscrape.com/index.html'
r = requests.get(url)
soup = BeautifulSoup(r.content, 'lxml')

links = soup.find('ul', class_='nav nav-list').find('ul').find_all('li')

category_names = [category.a.text.strip() for category in links]
all_links = [base_url + link.a['href'] for link in links]

names = []
prices = []
availability = []
ratings = []
categories = []
#for link in links:
index_num = 0
for url in all_links[:]:
	#temporary storage of url
	page = [url]
	while True:
		debug = page[0].split('/')[-2:]#for debugging
		print('.....' + '/'.join(debug))
		#requests http and parse page
		r = requests.get(page[0])
		soup = BeautifulSoup(r.content, 'lxml')
		#extract data
		items = soup.find('ol', class_='row').find_all('li', class_='col-xs-6 col-sm-4 col-md-3 col-lg-3')
		
		for item in items:
			name = item.find('h3').a['title']
			names.append(name)
			
			price = item.find('p', class_='price_color').text
			prices.append(price)
			
			available = item.find('p', class_='instock availability').text.strip()
			availability.append(available)
			
			rating = item.find('p', class_='star-rating')['class'][1]
			ratings.append(rating)
			
			categories.append(category_names[index_num])

		#check if there is next button
		try:
			nxt_btn = soup.find('ul', class_='pager').find('li', class_='next')
			if nxt_btn is not None:
				#update "page[0] = href value of nxt btn"
				href = nxt_btn.a['href']
				u = page[0].split('/')[:-1]
				nxt_page = '/'.join(u) + '/' +  href
				#update page[0] value
				page[0] = nxt_page
			else:
				break
		except:
			break
			
		#time.sleep(2)
			
	index_num += 1
	
	#time.sleep(5)

#create data frame
df = pd.set_option('max_rows', None, 'max_columns', None)
df = pd.DataFrame({
	'category': categories,
	'name': names,
	'ratings': ratings,
	'price': prices,
	'availability': availability
	})
df.to_csv('books.csv', index=False)
#print(df)
print(len(names))
