from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import numpy as np
import time
import requests
import re
from sklearn.feature_extraction.text import CountVectorizer
from joblib import Parallel, delayed

#All URLs I would like to include:
breckinridge = 'https://www.airbnb.com/s/Breckenridge--CO/homes?adults=1&place_id=ChIJwecmbD32aocReqKAZn-PjWI&refinement_paths%5B%5D=%2Fhomes'
parkcity = 'https://www.airbnb.com/s/Park-City--UT/homes?adults=1&place_id=ChIJ_QNjLGMPUocRlFc3Jd_Ecdg&refinement_paths%5B%5D=%2Fhomes'
jacksonhole = 'https://www.airbnb.com/s/Jackson-Hole--WY/homes?adults=1&place_id=ChIJS3_P_FgaU1MRXIM6scsBHD0&refinement_paths%5B%5D=%2Fhomes'
vail = 'https://www.airbnb.com/s/Vail--CO/homes?adults=1&place_id=ChIJB89dUQVwaocRxKOafh_AzMk&refinement_paths%5B%5D=%2Fhomes'
steamboat = 'https://www.airbnb.com/s/Steamboat-Springs--CO/homes?adults=1&place_id=ChIJYUZWCYF7QocRfc9uSNGjqBs&refinement_paths%5B%5D=%2Fhomes'
bigsky = 'https://www.airbnb.com/s/Big-Sky--MT/homes?adults=1&place_id=ChIJNSw3_WUOUFMRyiuLqjtx-JU&refinement_paths%5B%5D=%2Fhomes'
telluride = 'https://www.airbnb.com/s/Telluride--CO/homes?adults=1&place_id=ChIJc_TmcHvYPocR4eO6cSF37jg&refinement_paths%5B%5D=%2Fhomes'
aspen = 'https://www.airbnb.com/s/Aspen--CO/homes?adults=1&place_id=ChIJfTxB93w5QIcRcvYseNxCK8E&refinement_paths%5B%5D=%2Fhomes'
tahoe = 'https://www.airbnb.com/s/Lake-Tahoe/homes?adults=1&place_id=ChIJUREfuaF4mYARILWv7q8fP4w&refinement_paths%5B%5D=%2Fhomes'
taos = 'https://www.airbnb.com/s/Taos--NM/homes?adults=1&place_id=ChIJsfwRf9pkF4cRgrepYYOR6pA&refinement_paths%5B%5D=%2Fhomes'

def getPage(url):
    result = requests.get(url)
    content = result.content
    BeautifulSoup(content, features = "lxml")
    return BeautifulSoup(content, features = "lxml")

#Information on different listings is shown with an image and information under the class '_8ssblpx'
def getRoomClasses(soupPage):
    rooms = soupPage.findAll("div", {"class": "_8ssblpx"})
    result = []
    for room in rooms:
        result.append(room)
    return result

def getListingLink(listing):
    return "http://airbnb.com" + listing.find("a")["href"]

def getListingTitle(listing):
    return listing.find("meta")["content"]

def getTopRow(listing):
    return listing.find("div", {"class": "_167qordg"}).text

def getRoomInfo(listing):
    return listing.find("div", {"class": "_kqh46o"}).text

def getBasicFacilities(listing):
    try:
        output = listing.findAll("div", {"class": "_kqh46o"})[1].text.replace(" ","")
    except:
        output = []
    return output

def getListingPrice(listing):
    return listing.find("div", {"class": "1fwiw8gv"}).text

def getListingRating(listing):
    return listing.find("span", {"class": "_krjbj"}).text

def getListingReviewNumber(listing):
    try:
        output = listing.findAll("span", {"class": "_krjbj"})[1].text
    except:
        output = -1
    return output

def extractInformation(soupPage):
    listings = getRoomClasses(soupPage)
    titles, links, toprows, roominfo, basicfacilities, prices, ratings, reviews = [], [], [], [], [], [], [], []
    for listing in listings:
        titles.append(getListingTitle(listing))
        links.append(getListingLink(listing))
        toprows.append(getListingLink(listing))
        roominfo.append(getListingLink(listing))
        basicfacilities.append(getListingLink(listing))
        prices.append(getListingLink(listing))
        ratings.append(getListingLink(listing))
        reviews.append(getListingLink(listing))
    dictionary = {"title": titles, "toprow": toprows, "roominfo": roominfo, "facilities": basicfacilities, "price": prices, "rating": ratings, "link": links, "review": reviews}
    return pd.DataFrame(dictionary)

def findNextPage(soupPage):
    try:
        nextpage = "https://airbnb.com" + soupPage.find("li", {"class": "_i66xk8d"}).find("a")["href"]
    except:
        nextpage = "no next page"
    return nextpage

def getPages(url):
    result = []
    while url != "no next page":
        page = getPage(url)
        result = result + [page]
        url = findNextPage(page)
    return result

def extractPages(url):
    pages = getPages(url)
    df = extractInformation(pages[0])
    for pagenumber in range(1, len(pages)):
        df = df.append(extractInformation(pages[pagenumber]))
    return df

urls = [["Breckinridge",breckinridge], 
           ["Park City", parkcity],
           ["Jacksonhole", jacksonhole],
           ["Vail", vail], 
           ["Steamboat Springs", steamboat],
           ["Big Sky", bigsky],
           ["Telluride", telluride],
           ["Aspen", aspen],
           ["Lake Tahoe", tahoe],
           ["Taos", taos]]

def scrapeURLs(listofURLs):
    print(listofURLs[0][0])
    df = extractPages(listofURLs[0][1])
    df.loc[:, "city"] = listofURLs[0][0]
    for i in range(1, len(listofURLs)):
        print(listofURLs[i][0])
        newrows = extractPages(listofURLs[i][1])
        newrows.loc[:, "city"] = listofURLs[i][0]
        df = df.append(newrows)
    return df

def getDescription(detailpage):
    return detailpage.find("div",{"class": "_eeq7h0"}).text

def getDetailedScores(detailpage):
    output = []
    scores = detailpage.findAll(class_ = '_a3qxec')
    try:
        for i in range(0, 6):
            split = scores[i].text.split(".")
            output.append(float(split[0][-1] + "." + split[1]))
    except:
        pass
    return output

def getHostInfo(detailpage):
    return detailpage.find(class_ = "_f47qa6").text

def setupDriver(url, waiting_time = 2.5):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(waiting_time)
    return driver

def getJSpage(url):
    driver = setupDriver(url)
    read_more_buttons = driver.find_elements_by_class_name("_1d079j1e")
    try:
        for i in range(2, len(read_more_buttons)):
            read_more_buttons[i].click()
    except:
        pass
    html = driver.page_source
    driver.close()
    return BeautifulSoup(html, features = "lxml")

def getAmenitiesPage(detailpage):
    
    link = detailpage.find(class_ = "_1v4ygly5")["href"]
    driver = setupDriver("https://airbnb.com" + link, 5)
    html = driver.page_source
    driver.close()
    return BeautifulSoup(html, features = "lxml")

first = True
scraped = 0
def getAddis(url):
    global first
    global scraped
    output = pd.DataFrame(columns=["details_page", "amenities_page", "link"])
    try:
        dp = getJSpage(url)
        output.loc[0] = [dp, getAmenitiesPage(dp), url]
    except:
        output.loc[0] = [-1, -1, url]
    if first:
        output.to_csv('intermediate_results_par.csv', mode='a', header=True, index=False)
        first = False
    else:
        output.to_csv('intermediate_results_par.csv', mode='a', header=False, index=False)
    scraped += 1
    print("Scraped: {}".format(scraped))

def getReviews(detailpage):
    reviews = detailpage.findAll(class_ = "_50mnu4")
    output = ""
    for review in reviews:
        output += review.text + "**-**"
    return output

def getAmenities(amenitiespage):
    amenities = amenitiespage.findAll(class_ = "_vzrbjl")
    output = ""
    for amenity in amenities:
        output += re.findall('[A-Z][^A-Z]*', amenity.text)[0] + "**-**"
    return output

def getResponseInfo(detailpage):
    try:
        output = detailpage.find(class_ = "_jofnfy").text
    except:
        output = ""
    return output

def cleanFacilities(df):
    df.loc[:, "facilities"] = df["facilities"].astype(str).str.replace("[","").str.replace("]","")
    vectorizer = CountVectorizer(decode_error = "ignore")
    X = vectorizer.fit_transform(df.facilities)
    bag_of_words = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names())
    return pd.concat([df.reset_index(drop=True).drop("facilities", axis=1), bag_of_words], axis=1)

def cleanTitle(df):
    df.loc[:, "name"] = df["title"].str.split(" null ", n=0, expand=True)[0].str.replace("-", "")
    df.loc[:, "location"] = df["title"].str.split(" null ", n=0, expand=True)[1].str.replace("-","").str.strip()
    return df.drop("title", axis=1)

def cleanTopRow(df):
    df.loc[:, 'roomtype'] = df["toprow"].str.split(" in ", n=0, expand=True)[0]
    df.loc[:, 'detailed_location'] = df["toprow"].str.split(" in ", n=0, expand=True)[1]
    return df.drop("toprow", axis=1)

def cleanRoomInfo(df):
    df.loc[:, "guests"] = df.loc[:, "roominfo"].str.split(" . ", n=0, expand=True)[0].str.replace("guests", "")
    df.loc[:, "bedrooms"] = df.loc[:, "roominfo"].str.split(" . ", n=0, expand=True)[1]
    df.loc[:, "beds"] = df.loc[:, "roominfo"].str.split(" . ", n=0, expand=True)[2].str.replace(" bed","").str.replace("s", "")
    df.loc[:, "bathrooms"] = df.loc[:, "roominfo"].str.split(" . ", n=0, expand=True)[3]
    df.loc[:, "guests"] = pd.to_numeric(df.guests, errors='coerce')
    df.loc[:, "beds"] = pd.to_numeric(df.beds, errors='coerce')
    df.loc[:, "bedrooms"] = pd.to_numeric(df.bedrooms.str.split(" ", n=0, expand=True)[0], errors="ignore")
    df.loc[:, "bathrooms"] = pd.to_numeric(df.bathrooms.str.split(" ", n=0, expand=True)[0], errors="ignore")
    return df.drop("roominfo", axis=1)

def cleanPrice(df):
    df.loc[:, "pricepernight"] = df.loc[:, "price"].str.split("Discounted", n=0, expand=True)[0].str.replace("$", "/").str.split("/", n=0, expand=True)[1]
    df.loc[:, "discountedpricepernight"] = df.loc[:, "price"].str.split("Discounted", n=0, expand=True)[1].str.replace("$", "/").str.split("/", n=0, expand=True)[1]
    df.loc[:, "price"] = pd.to_numeric(df.pricepernight.str.replace(",","").str.strip())
    df.loc[:, "discountedprice"] = pd.to_numeric(df.discountedpricepernight.str.replace(" ", "").str.replace(",",""), errors="coerce")
    return df.drop(["pricepernight", "discountedpricepernight"], axis=1)

def cleanRating(df):
    df.loc[:, "score"] = df.loc[:, "rating"].str.split(" ", n=0, expand=True)[1]
    df.loc[:, "score"] = pd.to_numeric(df.score, errors="coerce")
    return df.drop("rating", axis=1)

def cleanReviewNumber(df):
    df.loc[:, "reviewnumber"] = df.loc[:, "reviewnumber"].str.split(" ", n=0, expand=True)[0]
    df.loc[:, "reviewnumber"] = pd.to_numeric(df.reviewnumber, errors="coerce")
    return df

def clean(df):
    df = cleanTitle(df)
    df = cleanFacilities(df)
    df = cleanTopRow(df)
    df = cleanPrice(df)
    df = cleanRating(df)
    df = cleanReviewNumber(df)
    col1 = df.pop("price")
    df = pd.concat([df.reset_index(drop=True), col1], axis=1)
    col2 = df.pop("reviewnumber")
    df = pd.concat([df.reset_index(drop=True), col2], axis=1)
    col3 = df.pop("link")
    df = pd.concat([df.reset_index(drop=True), col3], axis=1)
    return df

def cleanAmenities(df):
    df.loc[:, "amenities"] = df.amenities.replace(np.nan, "", regex=True)
    df.loc[:, "amenities"] = df.amenities.str.replace(" ", "_").str.replace("-", " ").str.replace("*", "")
    vectorizer = CountVectorizer(decode_error="ignore")
    X = vectorizer.fit_transform(df.amenities)
    bag_of_words = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names())
    return pd.concat([df.reset_index(drop=True).drop("amenities", axis=1), bag_of_words], axis=1)

def cleanReviews(df):
    df.loc[:, "reviews"] = df.reviews.replace(np.nan, "", regex=True)
    df.loc[:, "reviews"] = df.reviews.str.split("-")
    return df

def getResponseTime(string):
    if "Response time" in string:
        output = string[string.find("Response time") + 15:]
    else:
        output = "Unknown"
    return output

def getResponseRate(string):
    if "Response rate" in string:
        temp = string[string.find("Response rate") + 15:string.find("Response rate")+20]
        output = ""
        for letter in temp:
            if letter in "0123456789":
                outpput += letter
    else:
        output = "Unknown"
        return output

def getLanguages(string):
    if "Language" in string:
        if "Response" in string:
            output = string[10:string.find("Response")].strip()
        else:
            output = string[10:].strip()
    else:
        output = "Unknown"
    return output

def cleanResponseTime(df):
    df.loc[:, "response_info"] = df.response_info.replace(np.nan, "", regex=True)
    df.loc[:, "response_time"] = df.response_info.apply(lambda x: getResponseTime(x))
    return df

def cleanResponseRate(df):
    df.loc[:, "response_rate"] = df.response_info.apply(lambda x: getResponseRate(x))
    return df

def cleanLanguages(df):
    df.loc[:, "languages"] = df.response_info.apply(lambda x: getLanguages(x))
    df.loc[:, "languages"] = df.languages.str.split(",")
    return df

def cleanResponseInfo(df):
    df = cleanResponseTime(df)
    df = cleanResponseRate(df)
    df = cleanLanguages(df)
    return df.drop("response_info", axis=1)

def scraper(urls, sample_size=None, random_state=1234):
    df = scrapeURLs(urls)
    df = clean(df)
    if sample_size is not None:
        df = df.sample(sample_size, random_state = random_state)
    Parallel(n_jobs=-1, prefer="threads")(delayed(getAddis)(url) for url in df.link)
    df2 = pd.read_csv("intermediate_results_par.csv")
    df = df.merge(df2, on="link")
    df.loc[:, "reviews"] = df.details_page.apply(lambda x: getReviews(BeautifulSoup(x, features="lxml")))
    df.loc[:, "response_info"] = df.details_page.apply(lambda x: getResponseInfo(BeautifulSoup(x, features="lxml")))
    df.loc[:, "amenities"] = df.amenities_page.apply(lambda x: getAmenities(BeautifulSoup(x, features="lxml")))
    df = cleanReviews(df)
    df = cleanResponseInfo(df)
    df = cleanAmenities(df)
    return df