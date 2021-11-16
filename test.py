from lncrawl.core.sources import *
import json
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from operator import itemgetter

allCrawlers = load_sources()
blocked_sources = ["anythingnovel","automtl", ]

novel_names = pd.read_csv("newfile3.csv")['Book Name'].values.tolist()
crawlers = []

for x in allCrawlers:
    pathStr = str(x)
    if (r"sources\en" in pathStr or r"sources/en" in pathStr) and "mtl" not in pathStr:

        crawlers.append(allCrawlers[x][0])

def get_chapters_len(crawler_instance):
    try:
        crawler_instance.read_novel_info()
        return [len(crawler_instance.chapters), crawler_instance.novel_url]
    except Exception as e:
        print(crawler_instance.novel_url, e,"\n")

def get_info(crawler, query):
    newCrawl = crawler()
    novel_info = {}
    results = []
    try:
        novel_info = newCrawl.search_novel(query=query)
        for novel in novel_info:
            if novel['title'] == query:
                newCrawl.novel_url = novel['url']
                results =  get_chapters_len(newCrawl)
        return results
    except Exception as e:
        # print("failed",newCrawl)
        # print(e)
        return None

def single_search(query):
    final_list = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(get_info, crawlers[:10], [query for x in range(len(crawlers))][:10])
        for result in results:
            if result:
                final_list.append(result)
    return final_list
novels_list = {}

for novel in novel_names[:5]:

    final = single_search(novel)
    if final:
        data = sorted(final, key=itemgetter(0), reverse=True)
        novels_list[novel] = data

    # for num, row in enumerate(data):
    #     novels_list[f"Source {num}"] = row[1]
    #     novels_list[f"Chapters {num}"] = row[0]

# df1 = pd.DataFrame.from_dict(novels_list)
# df1.to_csv('test.csv')

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(novels_list, f, ensure_ascii=False, indent=2)