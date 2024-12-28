from Bio import Entrez

#https://marcobonzanini.com/2015/01/12/searching-pubmed-with-python/



def search(query):
    Entrez.email = 'email@email.com'
    handle = Entrez.esearch(db='pubmed', sort='relevance', retmax='20', retmode='xml', term=query)
    results = Entrez.read(handle)
    return results

def fetch_details(id_list):
    ids = ','.join(id_list)
    handle = Entrez.efetch(db='pubmed', retmode='xml', id=ids)
    results = Entrez.read(handle)
    return results


search_key = 'dream and god'


if __name__ == '__main__':
    results = search(search_key)
    id_list = results['IdList']

    # for example if the search criteria is too narrow
    # or if no results are returned
    if not id_list:
        print('list is empty')
    
    else:
        papers = fetch_details(id_list)


        for i, paper in enumerate(papers['PubmedArticle']):
            pid = id_list[i]
            title = paper['MedlineCitation']['Article']['ArticleTitle']

            abstract = paper['MedlineCitation']['Article'].get('Abstract', {}).get('AbstractText', ['No abstract avilable'])[0]

            print(f"{i+1} PID: {pid}")
            print(f"    TitleL {title}")
            print(f"    Abstract : {abstract}\n")

    


print("completed operations")