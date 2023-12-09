"""
Dataset preparation

1. Collect usernames of people who reported that they had been diagnosed w/ ADHD.
2. Create dataset:
    
    | username | post ID | comment text | reported ADHD diagnoses |
    ===============================================================
    | extasia  |  xyz    | "nice meme"  | false                   |
    ...

    2a. Make sure no data-leakage; i.e make sure there's a field for filtering all
        out comments where the user specifically discusses ADHD etc.
    2b. 
    
"""
import re
import requests
import html
import datetime

search_url = "https://hn.algolia.com/api/v1/search"
# TODO allow also 'I am diagnosed with ADHD'
query      = "I was diagnosed with ADHD"

def _clean_comment(comment: dict) -> tuple[str, datetime.datetime]:
    text = comment["comment_text"]
    unescaped = html.unescape(text)       # Remove the ampersands and stuff
    return (
        re.sub('<.*?>', '', unescaped), # Remove html tags e.g `<p>`, `</p>`
        datetime.datetime.fromtimestamp(comment["created_at_i"]),
    )

def get_users_who_report_an_adhd_diagnosis(max_usernames : int) -> set[str]:
    adhd_usernames = set()
    page = 0
    while 1:
        response = requests.get(search_url, params={
                "query"       : query,
                "tags"        : "comment",
                "page"        : page,
                # Max hits:
                # https://www.algolia.com/doc/guides/building-search-ui/ui-and-ux-patterns/pagination/js/#pagination-limitations
                "hitsPerPage" : 1000,
            }
        ).json()
        comments = response["hits"]
        adhd_usernames.update({c["author"] for c in comments})
        page += 1
        print("Page: ", page)
        if not comments:
            # We've gone through all the pages.
            return adhd_usernames

        if len(adhd_usernames) >= max_usernames:
            # We have enough usernames
            return set(list(adhd_usernames)[:max_usernames])

def get_control_users(users_who_report_an_adhd_diagnosis : set[str], max_usernames : int) -> set[str]:
    """Get a set of control users (who don't report having ADHD)."""
    non_adhd_usernames = set()
    page = 0
    while 1:
        response = requests.get(search_url, params={
                    "tags"        : "comment",
                    "page"        : page,
                    # Max hits:
                    # https://www.algolia.com/doc/guides/building-search-ui/ui-and-ux-patterns/pagination/js/#pagination-limitations
                    "hitsPerPage" : 1000,
                }
        ).json()
        comments = response["hits"]
        for c in comments:
            if c["author"] not in users_who_report_an_adhd_diagnosis:
                non_adhd_usernames.add(c["author"])

        page += 1
        print("Page: ", page)
        if not comments:
            # We've gone through all the pages.
            return non_adhd_usernames
        
        if len(non_adhd_usernames) >= max_usernames:
            # We have enough usernames
            return set(list(non_adhd_usernames)[:max_usernames])

big_query_dataset_last_date_unix_time = 1668556800
def get_comments_by_user(username: str, max_comments: int) -> list[tuple[str, datetime.datetime]]:
    # https://hn.algolia.com/api
    assert max_comments > 0
    assert max_comments <= 1000
    # XXX : Filters by created at after 
    url = f"{search_url}?tags=comment,author_{username}&hitsPerPage={max_comments}&numericFilters=created_at_i<{big_query_dataset_last_date_unix_time}"
    while True:
        try:
            response = requests.get(url)
            assert response.status_code == 200, response.status_code

            comments = requests.get(url).json()["hits"]
            return list(map(_clean_comment, sorted(comments, key=lambda c: c["created_at_i"],
                                                reverse=True))) # We want the most recent comments first!
        except Exception:
            pass


### Tests ###
if __name__ == "__main__":
    known_adhd_usernames = {'ryan90', 'skywhopper', 'ktsmith', 'lfowles', 'innguest', 'iron_codex',
            'kurage', 'Scienz', 'khorwitz', 'infoseek3', 'ddoolin', 'AJAr', 'austenallred',
            'rwbcxrz', 'eli_gottlieb', 'emotionalcode', 'zxcvcxz', 'eruditely', 'MichaelCrawford'}
    n_users = 1000
    adhd_usernames = get_users_who_report_an_adhd_diagnosis(n_users)
    non_adhd_usernames = get_control_users(adhd_usernames, n_users)

    assert known_adhd_usernames.issubset(adhd_usernames)
    assert len(known_adhd_usernames.intersection(non_adhd_usernames)) == 0
    print(len(adhd_usernames), len(non_adhd_usernames))
    
    comments = get_comments_by_user("bilekas", 30)
    assert isinstance(comments, list)
    assert isinstance(comments[0], tuple)
    
    # comment, datetime tuple
    assert isinstance(comments[0][0], str)
    assert isinstance(comments[0][1], datetime.datetime)

    assert len(comments) == 30
