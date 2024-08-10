#!/usr/bin/env python
#
# A script from @unixbigot@aus.social to answer the question
# "how many theoretical imprints did my toots get, and who were the key retooters"?
#
# This is a work in progress, I've written enough to show that it CAN work but it
# needs to do query pagination to get all the results properly
#
# You will need to register an app on your server and pass the app token via environment
# or argument.
#
# You probably ought to read the docs for mastodon.py below
#
# Mastodon.py API docs: https://mastodonpy.readthedocs.io/en/stable/

import argparse
from functools import reduce
import os
import pprint
from mastodon import Mastodon

pp = pprint.PrettyPrinter(indent=4)

parser = argparse.ArgumentParser(description="Rank toots by popularity")
#parser.add_argument("ids", metavar="N", type=int, nargs="+", help="toot IDs to query")
parser.add_argument('-c', '--count', type=int, nargs="?", help="number of toots to examine",default=20)
parser.add_argument('-v', '--verbose', action="count", help="include extra detail",default=0)
parser.add_argument('--base', help="api base url", nargs="?", default=os.environ["APIURL"])
parser.add_argument('--tagged', help="consider toots with tag")
parser.add_argument('--retoots', help="consider toots with at least N retoots",type=int, default=10)
parser.add_argument('--top', help="describe the top N retooters",type=int, default=5)
parser.add_argument('--followers', help="highlight retooters with at least N followers",type=int, default=1000)
parser.add_argument('--token', help="api authentication token", nargs="?", default=os.environ["APITOKEN"])
args = parser.parse_args()

if (args.verbose>1): pp.pprint({"args":args})


mastodon = Mastodon(api_base_url=args.base,access_token=args.token);

def type_census(s,a):
    t=s.type
    c=a[t] or 0
    a[t]=c+1
    return a

#pp.pprint(list(map(type_census, notes, {})))

def toot_boosts(t): return t.reblogs_count
def account_followers(a): return a.followers_count
def toot_id(t): return t.id
def rec_name(rec): return rec.name
def toot_ids(l): return list(map(toot_id, l))
def min_id(l): return min(toot_ids(l))
def tag_names(t): return list(map(rec_name, t.tags))

def toot_has_tag(t, tag):
    return tag in tag_names(t)

def get_last_toots(id, count=100, tagged=None):
    max_id = None
    toots = []
    while len(toots) < count:
        if tagged != None:
            new_toots = mastodon.account_statuses(id=id, max_id=max_id, exclude_replies=True, exclude_reblogs=True, tagged=tagged.lower())
        else:
            new_toots = mastodon.account_statuses(id=id, max_id=max_id, exclude_replies=True)
        if args.verbose>1: print(f"  got {len(new_toots)} toots")
        if (len(new_toots) == 0): break
        max_id = min_id(new_toots)
        while len(new_toots) and len(toots)<count:
            toot = new_toots.pop(0)
            toot.tag_names = tag_names(toot)
            toots.append(toot)
    if args.verbose: print(f"got total of {len(toots)} toots")
    return toots

def remove_author(t):
    t.author_id=t.account.id
    del t["account"]
    return t

def get_retoots(id, min_retoots=args.retoots, limit=args.count):
    toots = [remove_author(t) for t in get_last_toots(id, count=limit) if t.reblogs_count>=min_retoots]
    toots.sort(key=toot_boosts,reverse=True)
    return toots

def get_reblogs_bogus(id, min_followers=args.followers, limit=args.top, author=None):
    ## FIXME need to implement pagination here to get all rebloggers
    accounts = [a for a in mastodon.status_reblogged_by(id) if (a.followers_count >= min_followers) and (author==None or a.id != author)]
    accounts.sort(key=account_followers, reverse=True)
    if (limit > 0):
        return accounts[:limit]
    return accounts

def get_reblogs(id, min_followers=args.followers, limit=args.top, author=None):
    pageno = 1
    total = 0
    page = mastodon.status_reblogged_by(id)
    accounts = []
    while page != None and len(accounts)<limit:
        if args.verbose: print(f"  processing page {pageno} of {len(page)} records")
        total += len(page)
        for account in page:
            if (account.followers_count >= min_followers) and (author==None or account.id != author):
                accounts.append(account)
        #if args.verbose>1: print("  get_reblogs: fetch next page");
        page = mastodon.fetch_next(page)
        if page:
            pageno = pageno + 1
            #if args.verbose>1: print(f"  get_reblogs: fetched page {pageno}");
    accounts.sort(key=account_followers, reverse=True)
    if args.verbose: print(f"  collated {len(accounts)} boosters from {pageno} pages totalling {total} boosts")
    if (limit > 0):
        return accounts[:limit+1]
    return accounts


def describe_acct(a):
    print(f"        {a.acct} ({a.display_name}), followed by {a.followers_count} follows {a.following_count}")

def describe_reblogs(id):
    for a in get_reblogs(id): describe_acct(a)

def describe_retoots(t, slice_len=72):
    retoot_count = t.reblogs_count
    if args.verbose or retoot_count>=args.retoots:
        print(f"Toot {t.id} at {t.created_at.isoformat()}: {t.reblogs_count} retoots, {t.favourites_count} faves")
    if retoot_count < args.retoots: return
    if args.verbose>1: pp.pprint(t)

    print("    ",t.content[slice(slice_len)])
    reblogs = get_reblogs(t.id, author=t.author_id)
    if len(reblogs)>0:
        if len(t.tag_names): print(f"    Tagged {' '.join(t.tag_names)}")
        print("    Significant boosters:")
        for a in reblogs: describe_acct(a)
    print("")

me=mastodon.me()

if args.tagged != None:
    # fetch all toots and filter for ones with tag
    if (args.verbose): print(f"Fetching toots matching #{args.tagged}")
    toots = get_last_toots(me.id, count=args.count, tagged=args.tagged)
    for t in toots: describe_retoots(remove_author(t))
else:
    # Just get retooted posts
    retoots = get_retoots(me.id)
    for t in retoots: describe_retoots(t)



