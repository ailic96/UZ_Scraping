import os
import requests
import re
import time
import datetime
from bs4 import BeautifulSoup 
from csv import writer
import csv
import json


# Timer start
start = time.time()

# Deletes portal_articles.csv in order to have
# a clean start on every run
if os.path.exists('portal_articles.csv'):
    os.remove('portal_articles.csv')

# Number of lines / URLS to be processed
processed_urls = 1
url_counter = len(open('portal_urls.txt').readlines())
print('Found ' + str(url_counter) + ' urls')

# Opens portal_urls for reading article links
file = open('portal_urls.txt', 'r')


# Create .csv file and write column headers to it
with open('portal_articles.csv', 'a', encoding = 'utf-8') as csv_file:
    csv_writer = writer(csv_file, 
    delimiter=',', 
    quotechar='"', 
    quoting = csv.QUOTE_MINIMAL, 
    lineterminator='\n')  

    headers = ['ID', 'Title', 'Subtitle', 'URL', 
    'Section','Article_text', 'Published_time', 'Modified_time',    #csv.QUOTE_MINIMAL
    'Author', 'Comments', 'Reaction_love',
    'Reaction_laugh', 'Reaction_hug', 'Reaction_ponder',
    'Reaction_sad', 'Reaction_mad', 'Reaction_mind_blown']
    
    csv_writer.writerow(headers)

    print('Finished creating .csv headers...')

    requests_session = requests.Session()
    for url in file:
        #test data with comment, works
        #url = 'https://www.dalmacijadanas.hr/novo-dalmatinsko-zariste-od-sutra-stroge-mjere-zabranjuje-se-odrzavanje-mise/#comment-11944tinsko-zariste-od-sutra-stroge-mjere-zabranjuje-se-odrzavanje-mise/#comment-11944'
        #test data with br, works
        #url = 'https://www.dalmacijadanas.hr/zbog-najjace-bure-ovog-studenog-u-prekidu-sve-katamaranske-veze-na-dinari-osjet-hladnoce-skoro-20-stupnjeva/' 

        # Returns 403 Forbidden without headers
        response = requests_session.get(url, headers={'User-Agent': 'Mozilla/5.0'})

        # URL Counter
        print('Processed ' + str(processed_urls) + ' / ' + str(url_counter) + ' URL-s')
        print('Processing URL:\n' + url)

        # Check if site is reachable
        if response.status_code != requests.codes.ok:
            print("Error Code: " + str(response.status_code))

        else:
            # BeautifulSoup object initialization
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Initializing variables to prevent missing element errors
            id = int(processed_urls)
            title = ''
            subtitle = ''
            url = ''
            section = ''
            whole_text = ''
            published_time = ''
            modified_time = ''
            author = ''
            comments = '0'          # Default comment value
            reaction_love = ''
            reaction_laugh = ''
            reaction_blushy = ''
            reaction_ponder = ''
            reaction_sad = ''
            reaction_mad = ''
            reaction_mind_blown = ''

            # Title
            title = soup.find(property='og:title').get('content')
            
            # Article subtitle
            # Strip removes extra new lines
            if (soup.find(class_ = 'td-post-sub-title')):
                subtitle = soup.find(class_ = 'td-post-sub-title').get_text().strip()
                subtitle.replace('\n', '\\n')

            #Article URL
            article_url = soup.find(property='og:url').get('content')
            
            #Article section
            section = soup.find(property='article:section').get('content')
            
            # Date on which article was added / Parsing
            published_time_raw = soup.find(property='article:published_time').get('content')
            published_time_obj = datetime.datetime.strptime(published_time_raw, '%Y-%m-%dT%H:%M:%S%z')
            published_time = published_time_obj.date()

            # Last time article has been modified / Parsing
            modified_time_raw = soup.find(property='article:modified_time').get('content')
            modified_time_obj = datetime.datetime.strptime(modified_time_raw, '%Y-%m-%dT%H:%M:%S%z')  
            modified_time = published_time_obj.date()

            # Author of article/photo        
            for aut in soup.find_all(class_='td-post-author-name'):
                author = aut.get_text()
                
            # Fetching article text
            whole_text = []

            paragraphs = soup.find_all(class_ = 'td-post-content tagdiv-type')

            for paragraph in paragraphs:
                for tekst in paragraph.find_all('p'):
                    # Condition ignores ads and empty <p> elements
                    if (tekst.get_text() == ''):
                        continue
                    # Usef for getting bolded strings
                    elif (tekst.find('strong')):   
                        whole_text.append(tekst.find('strong').get_text().strip('<br>')) 
                        whole_text.append(tekst.get_text())  

                     # Used for getting paragraph header (summary)
                    elif (tekst.find('h2')):
                        whole_text.append(tekst.find('h2').get_text())
                        whole_text.append(tekst.get_text()) 

                    # Used for getting paragraph header (summary)    
                    elif (tekst.find('h3')):
                        whole_text.append(tekst.find('h2').get_text())
                        whole_text.append(tekst.get_text()) 

                    # Used for getting default <p> tag strings
                    else:
                        whole_text.append(tekst.get_text())


            # Turning list into string using join function 
            whole_text = ' '.join(whole_text)

            # Editing string and getting rid of \n 
            whole_text.replace('\n', ' ').replace('\r', '')
            whole_text.replace('\n', '\\n')
        

            # Comment section
            if (soup.find(class_ = 'td-comments-title block-title')):
                comment = soup.find('h4').get_text()
            
                regex = re.search('(\d*).*', comment)

                if regex:
                    comments = regex.group(1)

            # Identify reactions html elements
            for react_element in soup.find_all(class_='wpra-call-to-action'):
                    reactions = react_element.next_sibling.next_sibling.get_text()
            
            # Splitting reaction string, assigning emoji strings to variables
            reactions = reactions.split('   ')

            reaction_love = int(reactions[1])
            reaction_laugh = int(reactions[3])
            reaction_blushy = int(reactions [5])
            reaction_ponder = int(reactions [7])
            reaction_sad = int(reactions[9])
            reaction_mad = int(reactions[11])
            reaction_mind_blown = int(reactions[13])

            #print(title)
            #print(subtitle)
            #print(article_url)
            #print(section)
            #print(whole_text)
            #print(published_time)
            #print(modified_time)
            #print(author)      
            #print(reaction_love)        #js element
            #print(reaction_laugh)       #js element
            #print(reaction_blushy)      #js element
            #print(reaction_ponder)     #js element
            #print(reaction_sad)         #js element
            #print(reaction_mad)         #js element
            #print(reaction_mind_blown)  #js element
            
            csv_writer.writerow([id, title, subtitle, article_url, 
            section, whole_text, published_time, modified_time,
            author, comments, reaction_love,reaction_laugh,reaction_blushy,
            reaction_ponder, reaction_sad, reaction_mad,
            reaction_mind_blown])

            processed_urls += 1


print('\nCreating a .JSON file...')

csv_file_path = 'portal_articles.csv'
json_file_path = 'portal_articles.json'

# Writing csv to json
data = {}
with open(csv_file_path, encoding = 'utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for rows in csv_reader:
        id = rows['ID']
        data[id] = rows

with open(json_file_path, 'w', encoding = 'utf-8') as json_file:
    json_file.write(json.dumps(data, indent=4, ensure_ascii=False))

print('JSON file created.')

# End execution timer and present results
end = time.time()
print("\nTime spent processing data: " + str(end - start))