from .history import checkHistory
from .modules import write_content, getEachLine
from concurrent.futures import ThreadPoolExecutor
from time import sleep

def process_domain(domain, adultList, pbnWordsList, proxies):

    print(domain)

    try:

        results = checkHistory(domain, adultList, pbnWordsList, proxies)

        if results:
            write_content(domain, results)

    except Exception as e :
        print(f"(Check Manually) {domain} : error :- {e}")


def main(tasks):

    domains = getEachLine("domains.txt")
    adultList = getEachLine("./Library/adult_words.txt")
    pbnWordsList = getEachLine("./Library/other_words.txt")
    proxies = getEachLine("proxies.txt")
    try:
        proxies = proxies[0]
        splitted = proxies.split(":")
        proxies = {
            'http' : f"http://{splitted[2]}:{splitted[3]}@{splitted[0]}:{splitted[1]}"
        }
        
    except Exception:
        proxies = None
        
    with open("result.txt", "w+"): pass
    
    tasks = 10 if ( tasks > 10 ) else tasks
    
    with ThreadPoolExecutor(max_workers=tasks) as executor: 
        for domain in domains: executor.submit(process_domain, domain, adultList, pbnWordsList, proxies); sleep(1)
