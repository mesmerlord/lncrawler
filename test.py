from lncrawl.core.sources import *
import json
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from operator import itemgetter
import random
import traceback

allCrawlers = load_sources()
blocked_sources = ["anythingnovel","automtl" ]

novel_names = pd.read_csv("newfile3.csv")['Book Name'].values.tolist()
crawlers = []
errors = {}

for x in allCrawlers:
    pathStr = str(x)
    if (r"sources\en" in pathStr or r"sources/en" in pathStr) and "mtl" not in pathStr:

        crawlers.append(allCrawlers[x][0])

def get_chapters_len(crawler_instance):
    try:
        crawler_instance.read_novel_info()
        if len(crawler_instance.chapters) == 0:
            return
        elif len(crawler_instance.chapters) > 0:
            return [len(crawler_instance.chapters), crawler_instance.novel_url]
    except Exception as e:
        url = crawler_instance.base_url
        try:
            if type(crawler_instance.base_url) is list:
                url = ";".join(crawler_instance.base_url)
            if url in errors.keys():
                errors[url] += 1
                if errors[url] > 100 and type(crawler_instance) in crawlers:
                    crawlers.remove(type(crawler_instance))
            else:
                errors[url] = 0
        except:
            return None
def get_info(crawler, query, num):
    newCrawl = crawler()
    novel_info = {}
    results = []
    try:
        novel_info = newCrawl.search_novel(query=query)
        for novel in novel_info:
            if novel['title'] == query:
                newCrawl.novel_url = novel['url']
                results =  get_chapters_len(newCrawl)
        newCrawl.destroy()
        return results
    except Exception as e:
        try:
            url = newCrawl.base_url
            if type(newCrawl.base_url) is list:
                url = ";".join(newCrawl.base_url)
            if url in errors.keys():
                errors[url] += 1
                if errors[url] > 100 and type(newCrawl) in crawlers:
                    crawlers.remove(type(newCrawl))
            else:
                errors[url] = 0
                
        except:
            return None
        return None

def single_search(query, crawler_instances):
    final_list = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(get_info, crawler_instances, [query for x in range(len(crawler_instances))],
            [x for x in range(len(crawlers))])
        for result in results:
            if result:
                final_list.append(result)
    return final_list
novels_list = {}

for num, novel in enumerate(novel_names):
    list_of_results = []
    random.shuffle(crawlers)
    crawler_list = crawlers

    final = []
    for x in range(0, len(crawler_list), 40):
        crawler_list_slice = crawler_list[x : x+40]

        semi_final = single_search(novel, crawler_list_slice)
        if semi_final:
            final = final + semi_final
        if len(final) > 20:
            break

    if final:
        data = sorted(final, key=itemgetter(0), reverse=True)
        novels_list[novel] = data
        print(f"{num} --  Finished novel : {novel} ")

# df1 = pd.DataFrame.from_dict(novels_list)
# df1.to_csv('test.csv')

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(novels_list, f, ensure_ascii=False, indent=2)
with open('errors.json', 'w', encoding='utf-8') as error_file:
    json.dump(errors, error_file, ensure_ascii=False, indent=2)