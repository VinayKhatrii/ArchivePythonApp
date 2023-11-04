import requests
from googletrans import Translator
from bs4 import BeautifulSoup
from time import sleep

TRANSLATOR = Translator()

def getEachLine(fileLocation: str) -> list:

    with open(fileLocation, "r") as f:
        return [line.strip() for line in f if line.strip()!="" ]

def write_content(domain, result_content) -> None:

    with open("result.txt", "a") as f:
        f.write( f"{domain}\n" + "\n".join(result_content) + "\n\n")

def dontSkip(i: int) -> bool:
    if i < 10:
        return i % 1 == 0
    if i < 50:
        return i % 2 == 0
    if i < 70:
        return i % 3 == 0
    if i < 100:
        return i % 4 == 0
    if i < 200:
        return i % 5 == 0

    return i % 10 == 0


def archiveTimestamp(domain, proxies) -> list:

    try:
        api_url = f"https://web.archive.org/cdx/search/cdx?url={domain}&output=json&fl=timestamp"
        response = requests.get(api_url)
        response.raise_for_status()
        dates = response.json()

        return list(reversed(dates[1:]))

    except requests.exceptions.RequestException as e:

        print(f"An error occurred: {e}")
        sleep(5)

        return ["skipped"]

    except Exception as e:

        print(f"An unexpected error occurred: {e}")

        return ["skipped"]
    
def archiveText(url, domain, proxies) -> (str, int):
    response = requests.get(url, proxies=proxies)
    response.encoding = 'utf-8'
    response.raise_for_status()
    html = response.text
    return resultList(domain, html)

def resultList(domain, html) -> (str, int):

    soup = BeautifulSoup(html, "html.parser")
    hrefs = soup.find_all("a")
    text = soup.get_text()
    replaceList  = ["\n", ".", ",","$","%","^","#","?", "/", ")", "(", ">", "<", "'", '"', "&", "@", "=", "-", ":", ";", "!", "{", "}", "|", "/", "~", "`", "+", "*"]

    for char in replaceList:
        text = text.replace(char, " ")

    pages= noOfPages(hrefs, domain)

    return text, pages

def noOfPages(hrefs, domain) -> int:

    pages = 0

    def condition(i, a, domain) -> bool:
        
        conditionList = [f"/page/{i}", f"/page/{i}/", f"?page={i}/", f"?page={i}"]

        cond = any(str(a['href']).endswith(suffix) and domain in str(a['href']) for suffix in conditionList)

        return cond

    for a in hrefs:
        for i in range(2, 20):
            try:
                pages = max(pages, i) if condition(i, a, domain) else pages
                if condition(i, a, domain):
                    pages = max(pages, i)

            except Exception:
                continue

    return pages

def engTranslate(text:str, language: str) -> str:
    if language == 'en':
        return text
    else:
        translated = TRANSLATOR.translate(text).text
        return translated


def unwantedLanguages(x_short) -> str | None:
    shorts = ['ar', 'he', 'th','hi', 'mr', 'fa','zh-tw', 'zh-cn', "zh-hk", 'ja','ko', "ja-jp", "ko-kr", "ko-kp", "zh-hant",  "zh-mo", 'zh-sg', 'ar-x','ar-eg', 'he-il', "ja-jp-u-ca-japanese", "ja-jp-u-ca-japanese-t-ca-japanese"]

    x_language = {'zh-tw':"Chinese", 'zh-cn':"Chinese",'ja':'Japanese','ko':'Korean',"ja-jp":"Japanese","ja-jp-u-ca-japanese":"Japanese", "ja-jp-u-ca-japanese-t-ca-japanese":"Japanese", "ko-kr":"Korean","zh-hant":"Chinese","zh-hk":"Chinese","zh-mo":"Chinese","zh-sg":"Chinese","ar":"Arabic","ar-x":"Arabic","ar-eg":"Arabic",'he':"Hebrew",'he-il':"Hebrew",'th':"Thai",'hi':"Hindi",'mr':"Marathi",'fa':"Parsi"}

    return x_language[x_short] if x_short.lower() in shorts else None

def unwantedThings(text, adultList, pbnWordsList) -> list:

    catchedWords = []

    lower_text = text.lower()
    lower_text_words = set(lower_text.split())
    adult_list_set = set(adultList)
    common_words = adult_list_set.intersection(lower_text_words)
    catchedWords.extend(list(common_words))

    for word in pbnWordsList:
        if ( word in lower_text ) and (word not in catchedWords):
            catchedWords.append(word)

    return catchedWords


def samePattern(results, generalInfo, url) -> list:

    found = False

    if len(results) > 0:

        for i, result in enumerate(results):

            if len(results[i].split("\n")) > 4 and generalInfo in result:
                return results

            elif generalInfo in result:

                results[i] += f"\nURL: {url}"
                found = True
                break

        if not found:
            results.append(f"{generalInfo}\nURL: {url}")

    else:
        results.append(f"{generalInfo}\nURL: {url}")

    return results


def finalResult(found_adult_pbn_words, pages, results, url) -> list:

    joinedWords = ', '.join(found_adult_pbn_words)

    if found_adult_pbn_words and pages != 0:
        generalInfo = f"{pages} Pages, " + joinedWords
        return samePattern(results, generalInfo, url)

    elif found_adult_pbn_words:
        return samePattern(results,joinedWords, url)

    elif pages != 0:
        generalInfo = f"{pages} Pages"
        return samePattern(results, generalInfo, url)

    return results