import requests
import time
from bs4 import BeautifulSoup
from bs4.element import Comment

def send_request_with_retries(url, retries=5, delay=5, timeout=5):
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            attempt += 1
            time.sleep(delay)
    print("All retries failed.")
    return None

def fetch_job_listings(keywords="software%20engineer", refresh="1000"):
    url = f"https://www.linkedin.com/jobs/search/?keywords={keywords}&f_TPR=r{refresh}"
    response = send_request_with_retries(url)
    jobs = set()

    if not response:
        return jobs

    soup = BeautifulSoup(response.content, "html.parser")
    wall = soup.select_one('.jobs-search__results-list')

    if not wall:
        return jobs
    
    targets = list(wall.findChildren("div"))
    ids = set()
    for target in targets:
        if target and target.has_attr("data-entity-urn"):
            target_property = target["data-entity-urn"]
            ids.add(int(target_property[target_property.rfind(":") + 1:]))
    return ids

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True
   
def fetch_job(job_id):
    url = f"https://www.linkedin.com/jobs/view/{job_id}/"

    response = send_request_with_retries(url)
    if not response:
        return None
    
    soup = BeautifulSoup(response.content, "html.parser")

    container = soup.find_all('section', class_='description')

    texts_join = u" ".join(t.get_text(separator=" ", strip=True) for t in container).lower()

    return soup.find('title').get_text() if "internship" in texts_join or "intern " in texts_join else None
        
def controller(all_done_listings):
    set1 = fetch_job_listings()
    set2 = fetch_job_listings(keywords="software%20engineering%20intern")

    all_job_ids = (set1 | set2 - all_done_listings)
    jobs_response = set()

    for job_id in all_job_ids:
        response = fetch_job(job_id)
        print('run')
        if response:
            jobs_response.add((job_id, response))
    
    return all_job_ids, jobs_response
