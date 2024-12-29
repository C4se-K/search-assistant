from Bio.Entrez import efetch, read

# https://stackoverflow.com/questions/17409107/obtaining-data-from-pubmed-using-python

def print_abstract(pmid):
    handle = efetch(db='pubmed', id=pmid, retmode='text', rettype='abstract')
    print (handle.read())



def fetch_abstract(pmid):
    handle = efetch(db='pubmed', id=pmid, retmode='xml')
    xml_data = read(handle)[0]
    try:
        article = xml_data['MedlineCitation']['Article']
        abstract = article['Abstract']['AbstractText'][0]
        return abstract
    except IndexError:
        return None