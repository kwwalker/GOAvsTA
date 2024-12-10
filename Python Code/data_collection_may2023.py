# %% [markdown]
# # Data Collection

# %%
# Data collected on May 4, 2023

# https://chemrxiv.org/engage/chemrxiv/public-api/documentation

# Get all items:
# https://chemrxiv.org/engage/chemrxiv/public-api/v1/items

# for paging (example)
# https://chemrxiv.org/engage/chemrxiv/public-api/v1/items?limit=50&skip=5001

# Get metadata for a single preprint (example)
# https://chemrxiv.org/engage/chemrxiv/public-api/v1/items/60fcd0dc0b093e6b49e354b4

# %%
# import libraries
import json
import requests
from pprint import pprint
from time import sleep
import pandas as pd

# %%
# here is an example
api = "https://chemrxiv.org/engage/chemrxiv/public-api/v1/"
query = "items"
limit = "?limit=50" # max page size
page = "&skip=8000"

# %%
api_data = requests.get(api + query + limit + page).json()

# view first record
api_data["itemHits"][0]

# %%
# testing out the indexing....

# ChemRXiv item ID
print(api_data["itemHits"][0]["item"]["id"])

# ChemRXiv DOI
print(api_data["itemHits"][0]["item"]["doi"])

# version of record doi
# N.B. if no vorDOI, api_data["itemHits"][idx]["item"]["vor"] is None
print(api_data["itemHits"][0]["item"]["vor"]["vorDoi"])

# title
print(api_data["itemHits"][0]["item"]["title"])

# Date info for ChemRXiv
print(api_data["itemHits"][0]["item"]["status"])
print(api_data["itemHits"][0]["item"]["statusDate"])

# first author
print(api_data["itemHits"][0]["item"]["authors"][0]["firstName"])
print(api_data["itemHits"][0]["item"]["authors"][0]["lastName"])

# metrics
print(api_data["itemHits"][0]["item"]["metrics"])

# Abstract views
print(api_data["itemHits"][0]["item"]["metrics"][0]["description"])
print(api_data["itemHits"][0]["item"]["metrics"][0]["value"])

# Citations
print(api_data["itemHits"][0]["item"]["metrics"][1]["description"])
print(api_data["itemHits"][0]["item"]["metrics"][1]["value"])

# Downloads
print(api_data["itemHits"][0]["item"]["metrics"][2]["description"])
print(api_data["itemHits"][0]["item"]["metrics"][2]["value"])

# authors
pprint(api_data["itemHits"][0]["item"]["authors"])

# %%
len(api_data["itemHits"][0]["item"]["authors"])

# %%
print(api_data["itemHits"][0]["item"]["authors"][0]["institutions"][0]["name"])

# %%
# Now loop through one page and put everything in a dictionary
api = "https://chemrxiv.org/engage/chemrxiv/public-api/v1/"
query = "items"
limit = "?limit=50" # max page size
page = "&skip=8000" # example
api_data = requests.get(api + query + limit + page).json()

# %%
api_data_dict = {}
for idx in range(len(api_data["itemHits"])):
    # setting the key as the ChemRXiv ID
    key = api_data["itemHits"][idx]["item"]["id"]
    
    # add selected data fields
    doi = api_data["itemHits"][idx]["item"]["doi"]
    status = api_data["itemHits"][idx]["item"]["status"]
    statusDate = api_data["itemHits"][idx]["item"]["statusDate"]      
    title = api_data["itemHits"][idx]["item"]["title"]
    
    # get first author info
    first_au_firstName = api_data["itemHits"][idx]["item"]["authors"][0]["firstName"]
    first_au_lastName = api_data["itemHits"][idx]["item"]["authors"][0]["lastName"]
    
    # note if author has multiple instituion info, this gets first one listed
    first_au_inst = api_data["itemHits"][idx]["item"]["authors"][0]["institutions"][0]["name"]
    first_au_country = api_data["itemHits"][idx]["item"]["authors"][0]["institutions"][0]["country"]
   
    # get last author
    len_authors = len(api_data["itemHits"][idx]["item"]["authors"])
    
    if len_authors > 1:
        last_au_firstName = api_data["itemHits"][idx]["item"]["authors"][len_authors-1]["firstName"]
        last_au_lastName = api_data["itemHits"][idx]["item"]["authors"][len_authors-1]["lastName"]
        
        last_au_inst = api_data["itemHits"][idx]["item"]["authors"][len_authors-1]["institutions"][0]["name"]
        last_au_country = api_data["itemHits"][idx]["item"]["authors"][len_authors-1]["institutions"][0]["country"]               
    else:
        last_au_firstName = "None"
        last_au_lastName = "None"
        
        last_au_inst = "None"
        last_au_country = "None"
      
    # metrics
       
    if api_data["itemHits"][idx]["item"]["metrics"][0]["description"] == "Abstract Views":
        abstractViews = api_data["itemHits"][idx]["item"]["metrics"][0]["value"]
    else:
        abstractViews = "no_data"
        
    if api_data["itemHits"][idx]["item"]["metrics"][1]["description"] == "Citations":
        citations = api_data["itemHits"][idx]["item"]["metrics"][1]["value"]
    else:
        citations = "no_data"
        
    if api_data["itemHits"][idx]["item"]["metrics"][2]["description"] == "Content Downloads":
        downloads = api_data["itemHits"][idx]["item"]["metrics"][2]["value"]
    else:
        downloads = "no_data"
        
    # handle version of record doi
    if api_data["itemHits"][idx]["item"]["vor"] is None:
        vorDoi = "None"
    else:
        vorDoi = api_data["itemHits"][idx]["item"]["vor"]["vorDoi"]
    
    # add data to dictionary    
    api_data_dict[key] = {"doi": doi,"status": status, "statusDate": statusDate,
                          "first_au_firstName": first_au_firstName, "first_au_lastName": first_au_lastName,
                          "first_au_inst": first_au_inst, "first_au_country": first_au_country,
                          "last_au_firstName": last_au_firstName, "last_au_lastName": last_au_lastName,                          
                          "last_au_inst": last_au_inst, "last_au_country": last_au_country,
                          "title":title, "abstractViews": abstractViews, "citations": citations,
                          "contentDownloads": downloads, "vorDoi": vorDoi}

# %%
list(api_data_dict)[0]

# %%
list(api_data_dict.values())[0]

# %%
df = pd.DataFrame.from_dict(api_data_dict,orient="index")
df.head(5)

# %%
# now loop through with pagination
api = "https://chemrxiv.org/engage/chemrxiv/public-api/v1/"
query = "items"
limit = "?limit=50" # max page size
page = "&skip="

api_data = requests.get(api + query + limit).json()
num_preprints = api_data["totalCount"]
print(num_preprints)

# %%
# get range of numbers for pages needed by skipping 50 each time
pages = list(range(0,int(num_preprints/50)+1))
skips = [i * 50 for i in pages]
len(skips)

# %%
api + query + limit + page + str(skips[0])

# %%
####### loop through all ~355 pages of preprint data
####### this will take ~ 30 min.

api_data_dict = {}
for skip in skips:
    api_data = requests.get(api + query + limit + page + str(skip)).json()
    sleep(2)    
    for idx in range(len(api_data["itemHits"])):
        # setting the key as the ChemRXiv ID
        key = api_data["itemHits"][idx]["item"]["id"]
    
        # add selected data fields
        doi = api_data["itemHits"][idx]["item"]["doi"]
        status = api_data["itemHits"][idx]["item"]["status"]
        statusDate = api_data["itemHits"][idx]["item"]["statusDate"]    
        title = api_data["itemHits"][idx]["item"]["title"]
        
        # get first author info
        first_au_firstName = api_data["itemHits"][idx]["item"]["authors"][0]["firstName"]
        first_au_lastName = api_data["itemHits"][idx]["item"]["authors"][0]["lastName"]
    
        # note if author has multiple instituion info, this gets first one listed
        # also sometimes there is country data without institutions and vice versa
        
        len_first_au_inst = len(api_data["itemHits"][idx]["item"]["authors"][0]["institutions"])
        
        if len_first_au_inst >= 1:
            first_au_inst = api_data["itemHits"][idx]["item"]["authors"][0]["institutions"][0]["name"]
            first_au_country = api_data["itemHits"][idx]["item"]["authors"][0]["institutions"][0]["country"]           
        else:
            first_au_inst = "no_data"
            first_au_country = "no_data"
                 
        # get last author info
        len_authors = len(api_data["itemHits"][idx]["item"]["authors"])
    
        if len_authors > 1:
            last_au_firstName = api_data["itemHits"][idx]["item"]["authors"][len_authors-1]["firstName"]
            last_au_lastName = api_data["itemHits"][idx]["item"]["authors"][len_authors-1]["lastName"]          
            
        else:
            last_au_firstName = "None"
            last_au_lastName = "None"
            
          
        len_last_au_inst = len(api_data["itemHits"][idx]["item"]["authors"][len_authors-1]["institutions"])
        
        if len_authors > 1 and len_last_au_inst >=1:
            last_au_inst = api_data["itemHits"][idx]["item"]["authors"][len_authors-1]["institutions"][0]["name"]
            last_au_country = api_data["itemHits"][idx]["item"]["authors"][len_authors-1]["institutions"][0]["country"]  
         
        else:
            last_au_inst = "no_data"
            last_au_country = "no_data"
           
        # metrics
       
        if api_data["itemHits"][idx]["item"]["metrics"][0]["description"] == "Abstract Views":
            abstractViews = api_data["itemHits"][idx]["item"]["metrics"][0]["value"]
        else:
            abstractViews = "no_data"
        
        if api_data["itemHits"][idx]["item"]["metrics"][1]["description"] == "Citations":
            citations = api_data["itemHits"][idx]["item"]["metrics"][1]["value"]
        else:
            citations = "no_data"
        
        if api_data["itemHits"][idx]["item"]["metrics"][2]["description"] == "Content Downloads":
            downloads = api_data["itemHits"][idx]["item"]["metrics"][2]["value"]
        else:
            downloads = "no_data"
        
        # handle version of record doi
        if api_data["itemHits"][idx]["item"]["vor"] is None:
            vorDoi = "None"
        else:
            vorDoi = api_data["itemHits"][idx]["item"]["vor"]["vorDoi"]
    
        # add data to dictionary       
        api_data_dict[key] = {"doi": doi,"status": status, "statusDate": statusDate,
                             "first_au_firstName": first_au_firstName, "first_au_lastName": first_au_lastName,
                             "first_au_inst": first_au_inst, "first_au_country": first_au_country,
                             "last_au_firstName": last_au_firstName, "last_au_lastName": last_au_lastName,                          
                             "last_au_inst": last_au_inst, "last_au_country": last_au_country,
                             "title":title, "abstractViews": abstractViews, "citations": citations,
                             "contentDownloads": downloads, "vorDoi": vorDoi}

# %%
len(api_data_dict)

# %%
list(api_data_dict)[0]

# %%
list(api_data_dict.values())[0]

# %%
df1 = pd.DataFrame.from_dict(api_data_dict,orient="index")
df1.head(5)

# %%
# save to CSV
df1.to_csv('chemrxiv_data_2023-05-04-ALL.tsv', sep='\t', header=True)

# %%
# create a dataframe with only the preprints that have a version of record DOI
df2 = df1.loc[~df1['vorDoi'].str.contains("None")]
df2.head(5)

# %%
len(df2)

# %%
df2.to_csv('chemrxiv_data_2023-05-04-vor_only.tsv', sep='\t', header=True)

# %% [markdown]
# # Get Scopus PlumX Data for ChemRxiv records with a published version of record

# %%
# load data
df2 = pd.read_csv('chemrxiv_data_2023-05-04-vor_only.tsv', sep='\t',index_col=0)
df2.head(5)

# %%
# testing
from pybliometrics.scopus import PlumXMetrics
plum1 = PlumXMetrics('10.1002/anie.202116658', id_type='doi', refresh=True)
print(plum1)

# %%
plum1.category_totals

# %%
# view all data for save to a dataFrame:
df_capture1 = pd.DataFrame(plum1.capture)
df_citation1 = pd.DataFrame(plum1.citation)
df_mention1 = pd.DataFrame(plum1.mention)
df_social1 = pd.DataFrame(plum1.social_media)
df_use1 = pd.DataFrame(plum1.usage)

frames1 = [df_capture1, df_citation1, df_mention1, df_social1, df_use1]
df_totals1 = pd.concat(frames1)
df_totals1

# %%
# OK, get all vorDois
vorDois = df2.loc[:,"vorDoi"].tolist()
len(vorDois)

# %%
# Get all PlumX data in a loop
plum_df_all = pd.DataFrame()

for doi in vorDois:
        
    try:
    
        # query search
        plum = PlumXMetrics(doi, id_type='doi',refresh=True)
    
        # delay between api calls to be nice to Elsevier
        sleep(0.25)
    
        # account for when the API returns no data
        if plum.category_totals is None:
        
            # create a dataframe with an empty row and note
            category_totals = pd.Series(['NOTES'])
            total = pd.Series(['API returned plum.category_totals as None'])
            plum_df = pd.DataFrame({'name': category_totals, 'total': total})
            plum_df = plum_df.set_index('name')
            plum_df = plum_df.transpose()
            plum_df['doi'] = doi
            first_column = plum_df.pop('doi')
            plum_df.insert(0, 'doi', first_column)
      
        # account for when API returns data
        if plum.category_totals is not None:
          # save to dataframes
            df_capture = pd.DataFrame(plum.capture)
            df_citation = pd.DataFrame(plum.citation)
            df_mention = pd.DataFrame(plum.mention)
            df_social = pd.DataFrame(plum.social_media)
            df_use = pd.DataFrame(plum.usage)
    
            # concatenate frames and set new index
            frames = [df_capture, df_citation, df_mention, df_social, df_use]
            plum_df = pd.concat(frames)
            plum_df = plum_df.set_index('name')
            plum_df = plum_df.transpose()
            plum_df['doi'] = doi
            first_column = plum_df.pop('doi')
            plum_df.insert(0, 'doi', first_column)
    
        # add to overall frame
        plum_df_all = pd.concat([plum_df_all, plum_df])
    
    except:
     # handle the case when Scopus returns a 404 or some other error
     # create a dataframe with an empty row and note
            category_totals = pd.Series(['NOTES'])
            total = pd.Series(['exception error: API returned Scopus error'])
            plum_df = pd.DataFrame({'name': category_totals, 'total': total})
            plum_df = plum_df.set_index('name')
            plum_df = plum_df.transpose()
            plum_df['doi'] = doi
            first_column = plum_df.pop('doi')
            plum_df.insert(0, 'doi', first_column)
            plum_df_all = pd.concat([plum_df_all, plum_df])
            
plum_df_all.head(10)

# %%
# save
plum_df_all.to_csv("PlumX_chemrxiv_data_2023-05-04-vor_only.tsv", sep = '\t', index=True)

# %%
# Collect the metadata for each vor DOI
from pybliometrics.scopus import ScopusSearch

q1 = ScopusSearch('DOI(10.1021/acs.jcim.9b01014)', download=True)
#df1 = pd.DataFrame(q1.results)
q1.get_results_size()

# %%
q1_df = pd.DataFrame(q1.results)
q1_df.columns

# %%
metadata = []
for i,doi in enumerate(vorDois):
    q = ScopusSearch('DOI('+ doi + ')', download=True)    
    num = q.get_results_size()
    sleep(0.25)
    print(i)
    
    if num == 0:
        metadata.append([doi,"Not able to get metadata, DOI not found in ScopusSearch"])
    
    else:
       # create a dataframe
        q_df = pd.DataFrame(q.results)
        
       # save metadata
       # There is definetely a better way to do this....but it works.
        
        author_names = q_df.author_names.tolist()[0]
        author_ids = q_df.author_ids.tolist()[0]
        author_afids = q_df.author_afids.tolist()[0]
        afid = q_df.afid.tolist()[0]
        affilname = q_df.affilname.tolist()[0]
        affiliation_city = q_df.affiliation_city.tolist()[0]
        affiliation_country = q_df.affiliation_country.tolist()[0]
        author_count = q_df.author_count.tolist()[0]
        title = q_df.title.tolist()[0]
        coverDate = q_df.coverDate.tolist()[0]
        publicationName = q_df.publicationName.tolist()[0]
        issn = q_df.issn.tolist()[0]
        volume = q_df.volume.tolist()[0]
        issueIdentifier = q_df.issueIdentifier.tolist()[0]
        article_number = q_df.article_number.tolist()[0]
        pageRange = q_df.pageRange.tolist()[0]
        openaccess = q_df.openaccess.tolist()[0]
        freetoread = q_df.freetoread.tolist()[0]
        freetoreadLabel = q_df.freetoreadLabel.tolist()[0]
        
        metadata.append([doi,
                         author_names,
                         author_ids,
                         author_afids,
                         afid,
                         affilname,
                         affiliation_city,
                         affiliation_country,
                         author_count,
                         title,
                         coverDate,
                         publicationName,
                         issn,
                         volume,
                         issueIdentifier,
                         article_number,
                         pageRange,
                         openaccess,
                         freetoread,
                         freetoreadLabel])
        
metadata_df = pd.DataFrame(metadata)
metadata_df.rename(columns={0: "doi",1: "author_names",2: "author_ids", 3: "author_afids",
                            4: "afid", 5: "affilname", 6: "affiliation_city", 7: "affiliation_country",
                            8: "author_count", 9: "title", 10: "coverDate", 11: "publicationName",
                            12: "issn", 13: "volume", 14: "issueIdentifier", 15: "article_number",
                            16: "pageRange", 17: "openaccess", 18: "freetoread", 19: "freetoreadLabel"},
                            inplace=True)

# %%
metadata_df.head(3)

# %%
len(metadata_df)

# %%
plum_df_all = pd.read_csv('PlumX_chemrxiv_data_2023-05-04-vor_only.tsv', sep='\t',index_col=0)
len(plum_df_all)

# %%
# There appears to be a few duplicate vDOIs from the ChemRXiv data, so we will remove these rows before merging
metadata_df.drop_duplicates('doi',keep=False, inplace=True)
print(len(metadata_df))

# %%
plum_df_all.drop_duplicates('doi',keep=False, inplace=True)
print(len(plum_df_all))

# %%
# merge data
plum_and_metadata = pd.merge(metadata_df, plum_df_all, on='doi')
plum_and_metadata.head(3)

# %%
len(plum_and_metadata)

# %%
plum_and_metadata.to_csv("metadata_AND_PlumX_chemrxiv_data_2023-05-04-vor_only.tsv", sep = '\t', index=True)

# %%


# %%
# next compile a comparison dataset
# First, grab a list of DOIs from selected journals
  
name_dictionary = {
    "1520-5126": "Journal of the American Chemical Society",
    "2041-6539": "Chemical Science",
    "1521-3773": "Angewandte Chemie - International Edition",
    "1549-9626": "Journal of Chemical Theory and Computation",
    "1463-9084": "Physical Chemistry Chemical Physics",
    "1521-3765": "Chemistry - A European Journal",
    "1932-7455": "Journal of Physical Chemistry C",
    "1549-960X": "Journal of Chemical Information and Modeling",
    "1520-5002": "Chemistry of Materials",
    "1089-7690": "Journal of Chemical Physics",
    "1364-548X": "Chemical Communications",
    "1520-5215": "Journal of Physical Chemistry A",
    "1944-8252": "ACS Applied Materials and Interfaces",
    "1520-5207": "Journal of Physical Chemistry B",
    "1520-6882": "Analytical Chemistry",
    "1523-7052": "Organic Letters",
    "1520-6904": "Journal of Organic Chemistry",
    "1520-510X": "Inorganic Chemistry",
    "2050-7488": "Journal of Materials Chemistry A"
}

email = "email_address"
mailto = "&mailto=" + email

# %%
# create a function to get DOIs based on issn and year

def listOfDois(issn, year, rows = 1000):
    jbase_url = "https://api.crossref.org/journals/"  # the base url for api calls
    journal_works = "/works?filter=from-pub-date:"+year+",until-pub-date:"+year+"&select=DOI"  # query to get DOIs for year
    rows = "&rows=" + str(rows)
    requestData = requests.get(jbase_url + issn + journal_works + rows + mailto).json()
    numResults = requestData["message"]["total-results"]
    sleep(1)
    
    doi_list = []
    for n in range(int(numResults/1000)+1): # list(range(int(numberOfResults/1000)+1)) = [0,1]
        query = requests.get(jbase_url + issn + journal_works + rows + "&offset=" + str(1000*n) + mailto).json()
        sleep(1)
        for doi in range(len(query["message"]["items"])):
            doi_list.append(query["message"]["items"][doi]["DOI"])  
    print(requestData["message"]["total-results"])
    return doi_list

# %%
from time import time
start = time()
# query crossref to get DOIs
compare_dois = {}
for issn in name_dictionary.keys():
    years = {}
    for year in range(2017,2024):
        dois = listOfDois(issn, str(year))
        years[str(year)] = dois
    compare_dois[issn] = years
print(f"Runtime = {(time() - start)}")

# %%
from time import time
start = time()
# get all dois into one list
compare_dois_list = []
for issn in compare_dois:
    for year in compare_dois[issn]:
        for dois in compare_dois[issn][year]:
            compare_dois_list.append(dois)
print(f"Runtime = {(time() - start)}")

# %%
from time import time
start = time()
# same but list compehension
compare_dois_list = [dois for issn in compare_dois for year in compare_dois[issn] for dois in compare_dois[issn][year]]
print(f"Runtime = {(time() - start)}")

# %%
len(compare_dois_list)

# %%
# get a sample of 5000
import random
random.seed(30)
compare_dois_sample = random.sample(compare_dois_list,5000)
compare_dois_sample[0:50]

# %%
len(compare_dois_sample)

# %%
# Grab all of the PlumX data for comparison DOIs
# Get all PlumX data in a loop

# Get all PlumX data in a loop
plum_df_all_compare = pd.DataFrame()

for doi in compare_dois_sample:
        
    try:
    
        # query search
        plum = PlumXMetrics(doi, id_type='doi',refresh=True)
    
        # delay between api calls to be nice to Elsevier
        sleep(0.25)
    
        # account for when the API returns no data
        if plum.category_totals is None:
        
            # create a dataframe with an empty row and note
            category_totals = pd.Series(['NOTES'])
            total = pd.Series(['API returned plum.category_totals as None'])
            plum_df = pd.DataFrame({'name': category_totals, 'total': total})
            plum_df = plum_df.set_index('name')
            plum_df = plum_df.transpose()
            plum_df['doi'] = doi
            first_column = plum_df.pop('doi')
            plum_df.insert(0, 'doi', first_column)
      
        # account for when API returns data
        if plum.category_totals is not None:
          # save to dataframes
            df_capture = pd.DataFrame(plum.capture)
            df_citation = pd.DataFrame(plum.citation)
            df_mention = pd.DataFrame(plum.mention)
            df_social = pd.DataFrame(plum.social_media)
            df_use = pd.DataFrame(plum.usage)
    
            # concatenate frames and set new index
            frames = [df_capture, df_citation, df_mention, df_social, df_use]
            plum_df = pd.concat(frames)
            plum_df = plum_df.set_index('name')
            plum_df = plum_df.transpose()
            plum_df['doi'] = doi
            first_column = plum_df.pop('doi')
            plum_df.insert(0, 'doi', first_column)
    
        # add to overall frame
        plum_df_all_compare = pd.concat([plum_df_all_compare, plum_df])
    
    except:
     # handle the case when Scopus returns a 404 or some other error
     # create a dataframe with an empty row and note
            category_totals = pd.Series(['NOTES'])
            total = pd.Series(['exception error: API returned Scopus error'])
            plum_df = pd.DataFrame({'name': category_totals, 'total': total})
            plum_df = plum_df.set_index('name')
            plum_df = plum_df.transpose()
            plum_df['doi'] = doi
            first_column = plum_df.pop('doi')
            plum_df.insert(0, 'doi', first_column)
            plum_df_all_compare = pd.concat([plum_df_all_compare, plum_df])
            
plum_df_all_compare.head(10)

# %%
len(plum_df_all_compare)

# %%
# next get the metadata
metadata_compare = []
for i,doi in enumerate(compare_dois_sample):
    q = ScopusSearch('DOI('+ doi + ')', download=True)    
    num = q.get_results_size()
    sleep(0.25)
    print(i)
    
    if num == 0:
        metadata_compare.append([doi,"Not able to get metadata, DOI not found in ScopusSearch"])
    
    else:
       # create a dataframe
        q_df = pd.DataFrame(q.results)
        
       # save metadata
       # There is definetely a better way to do this....but it works.
        
        author_names = q_df.author_names.tolist()[0]
        author_ids = q_df.author_ids.tolist()[0]
        author_afids = q_df.author_afids.tolist()[0]
        afid = q_df.afid.tolist()[0]
        affilname = q_df.affilname.tolist()[0]
        affiliation_city = q_df.affiliation_city.tolist()[0]
        affiliation_country = q_df.affiliation_country.tolist()[0]
        author_count = q_df.author_count.tolist()[0]
        title = q_df.title.tolist()[0]
        coverDate = q_df.coverDate.tolist()[0]
        publicationName = q_df.publicationName.tolist()[0]
        issn = q_df.issn.tolist()[0]
        volume = q_df.volume.tolist()[0]
        issueIdentifier = q_df.issueIdentifier.tolist()[0]
        article_number = q_df.article_number.tolist()[0]
        pageRange = q_df.pageRange.tolist()[0]
        openaccess = q_df.openaccess.tolist()[0]
        freetoread = q_df.freetoread.tolist()[0]
        freetoreadLabel = q_df.freetoreadLabel.tolist()[0]
        
        metadata_compare.append([doi,
                         author_names,
                         author_ids,
                         author_afids,
                         afid,
                         affilname,
                         affiliation_city,
                         affiliation_country,
                         author_count,
                         title,
                         coverDate,
                         publicationName,
                         issn,
                         volume,
                         issueIdentifier,
                         article_number,
                         pageRange,
                         openaccess,
                         freetoread,
                         freetoreadLabel])
        
metadata_df_compare = pd.DataFrame(metadata_compare)
metadata_df_compare.rename(columns={0: "doi",1: "author_names",2: "author_ids", 3: "author_afids",
                            4: "afid", 5: "affilname", 6: "affiliation_city", 7: "affiliation_country",
                            8: "author_count", 9: "title", 10: "coverDate", 11: "publicationName",
                            12: "issn", 13: "volume", 14: "issueIdentifier", 15: "article_number",
                            16: "pageRange", 17: "openaccess", 18: "freetoread", 19: "freetoreadLabel"},
                            inplace=True)

# %%
len(metadata_df_compare)

# %%
# not sure why there are a few duplicates from crossref...maybe overlap of year
metadata_df_compare.drop_duplicates('doi',keep=False, inplace=True)
print(len(metadata_df_compare))

# %%
plum_df_all_compare.drop_duplicates('doi',keep=False, inplace=True)
print(len(plum_df_all_compare))

# %%
# merge data
plum_and_metadata_compare = pd.merge(metadata_df_compare, plum_df_all_compare, on='doi')
plum_and_metadata_compare.head(3)

# %%
len(plum_and_metadata_compare)

# %%
plum_and_metadata_compare.to_csv("metadata_AND_PlumX_comparison_data_2023-05-04.tsv", sep = '\t', index=True)




