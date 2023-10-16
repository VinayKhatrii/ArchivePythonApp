from modules import (
    archiveText,
    unwantedLanguages,
    engTranslate,
    unwantedThings,
    finalResult,
    requests,
    sleep,
    dontSkip,
    archiveTimestamp
)
from langdetect import detect, LangDetectException
from time import sleep

def checkHistory(domain, adultList, pbnWordsList, proxies):
    
    time_stamp = archiveTimestamp(domain, proxies)
    
    if ( time_stamp[0] == "skipped" ) : 
        return
    
    return analyze_archive(domain, adultList, pbnWordsList, time_stamp, proxies)


def analyze_archive(domain, adultList, pbnWordsList, time_stamp, proxies):
    
    results = []
    
    for i, eachtimestamp in enumerate(time_stamp):
        
        if ( len(results) == 5 ) : break
        
        if dontSkip(i) :
            try:
                url = f"http://web.archive.org/web/{eachtimestamp[0]}/{domain}"
                
                textContent, pages = archiveText(url, domain, proxies)
                
                lang = detect(textContent)
                
                unwantedLang = unwantedLanguages(lang)
                
                if (unwantedLang) : 
                    results.append(f"{unwantedLang} detected in the year {eachtimestamp[0][:4]}\nURL: {url}")
                    break
                
                translatedText = engTranslate(textContent, lang)
                
                found_adult_pbn_words = unwantedThings(translatedText, adultList, pbnWordsList)
                
                results = finalResult(found_adult_pbn_words, pages, results, url)
            except (LangDetectException) : continue
            
            except requests.exceptions.HTTPError as e:
                
                if (e.response.status_code == 404) : continue
                
                elif (e.response.status_code == 429) : sleep(5); continue

            except Exception as e : 
                print(e)
                break
            
    return results