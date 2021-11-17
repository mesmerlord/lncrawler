from lncrawl.core.sources import *
import json
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from operator import itemgetter
import random
import logging
import urllib3
from colorama import Fore
import concurrent.futures
import traceback

urllib3.disable_warnings()

logging.basicConfig(
            level=logging.INFO,
            format=Fore.CYAN + '%(asctime)s '
            + Fore.RED + '[%(levelname)s] '
            + Fore.YELLOW + '(%(name)s)\n'
            + Fore.WHITE + '%(message)s' + Fore.RESET,
        )
logger = logging.getLogger(__name__)

allCrawlers = load_sources()
blocked_sources = ["anythingnovel","automtl" ]

novel_names = pd.read_csv("newfile3.csv")['Book Name'].values.tolist()
crawlers = []
errors = {}
not_found = []

for x in allCrawlers:
    pathStr = str(x)
    if (r"sources\en" in pathStr or r"sources/en" in pathStr) and "mtl" not in pathStr:
        try:
            crawl = allCrawlers[x][0]
            crawlers.append(crawl)
        except TypeError:
            pass

def get_chapters_len(crawler_instance):
    crawler_instance.read_novel_info()
    if len(crawler_instance.chapters) == 0:
        return
    elif len(crawler_instance.chapters) > 0:

        crawler_list[crawler_instance] += 1
        return [len(crawler_instance.chapters), crawler_instance.novel_url]
        
def get_info(crawler, query):
    newCrawl = crawler()
    novel_info = {}
    results = []
    url = newCrawl.base_url
    novel_info = newCrawl.search_novel(query=query)
    for novel in novel_info:
        if novel['title'] == query:
            newCrawl.novel_url = novel['url']
            logger.info(f"Found novel at : {novel['url']}")
            results =  get_chapters_len(newCrawl)

    newCrawl.destroy()
    if results:
        logger.info(f"{query} Novel found")
        return results
    else:
        return None

def single_search(query, crawler_instances):
    final_list = []
    num_of_crawlers = len(crawler_instances)
    with ThreadPoolExecutor(max_workers=num_of_crawlers) as executor:
        future_to_url = {executor.submit(get_info, crawler_instance, query):
                 crawler_instance for crawler_instance in crawler_instances}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                if result:
                    final_list.append(result)
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))

    return final_list
novels_list = {}

with open('data.json', 'r', encoding='utf-8') as json_file:
    novels_list = json.load(json_file)
with open('not_found.json', 'r', encoding='utf-8') as json_file_2:  
    not_found = json.load(json_file_2)

novel_names = [x for x in novel_names if x not in novels_list.keys()]
for num, novel in enumerate(novel_names):
    list_of_results = []
    final = []
    items_to_search = 20
    random.shuffle(crawlers)

    for x in range(0, len(crawlers), items_to_search):
        crawler_list_slice = crawlers[x : x + items_to_search]
        semi_final = single_search(novel, crawler_list_slice)
        if semi_final:
            final = final + semi_final
        logger.info(f"{len(final)} -- {novel}")
        if len(final) >= 5:
            break
    if final:
        data = sorted(final, key=itemgetter(0), reverse=True)
        novels_list[novel] = data
        logger.info(f"{num} --  Finished novel : {novel} ")
    else:
        logger.error(f"{num} --  Not found : {novel} ")
        novels_list[novel] = final
        not_found.append(novel)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(novels_list, f, ensure_ascii=False, indent=2)
    with open('not_found.json', 'w', encoding='utf-8') as not_f:
        json.dump(not_found, not_f, ensure_ascii=False, indent=2)

