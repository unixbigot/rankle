#!/usr/bin/env python
#
# A script from @unixbigot@aus.social et.al. to answer the question
# "how many theoretical imprints did my toots get, and who were the key boosters"?
#
# This is a work in progress, I've written enough to show that it CAN work, and
# it does query pagination to get results, but I susspect that mastodon does not
# give guaranteed access to all the boosters via the api.
#
# You will need to register an app on your server and pass the app token via environment
# or argument (see the README)
#
# You probably ought to read the docs for mastodon.py below
#
# Mastodon.py API docs: https://mastodonpy.readthedocs.io/en/stable/

import argparse
import os
import pprint
from mastodon import Mastodon

#
# Command line arguments
#

parser = argparse.ArgumentParser(description="Rank toots by popularity")
#parser.add_argument("ids", metavar="N", type=int, nargs="+", help="toot IDs to query")
parser.add_argument('-c', '--count',
                    type=int, nargs="?", default=20,
                    help="number of toots to examine")
parser.add_argument('-v', '--verbose', action="count", help="include extra detail",default=0)
parser.add_argument('--base', help="api base url", nargs="?", default=os.environ["APIURL"])
parser.add_argument('--boosts', help="consider toots with at least N boosts",type=int, default=10)
parser.add_argument('--followers',
                    type=int, default=1000,
                    help="highlight boosters with at least N followers")
parser.add_argument('--tagged', help="consider toots with tag")
parser.add_argument('-m', '--most-boosted-first',
                    help="sort by most-boosted-first",action="store_true")
parser.add_argument('--top', help="describe the top N boosters",type=int, default=5)
parser.add_argument('--token', nargs="?", default=os.environ["APITOKEN"],
                    help="api authentication token (see server's prefs->dev->new app)")
args = parser.parse_args()

pp = pprint.PrettyPrinter(indent=4)
if args.verbose>1:
    pp.pprint({"args":args})

#
# Get a mastodon api handle
#
mastodon = Mastodon(api_base_url=args.base,access_token=args.token)


#
# Helper functions
#
# If I was up to date with how to write lambdas in python these would probably be unnecessary
#

def toot_boosts(t): return t.reblogs_count
def account_followers(a): return a.followers_count
def get_toot_id(t): return t.id
def rec_name(rec): return rec.name
def toot_ids(l): return list(map(get_toot_id, l))
def min_id(l): return min(toot_ids(l))
def tag_names(t): return list(map(rec_name, t.tags))

# return whether a toot has a particular tag
def toot_has_tag(t, tag):
    return tag in tag_names(t)

#
# Remove the large {author} sub-record (hint: it's always you) and just keep an author_id
#
def remove_author(t):
    t.author_id=t.account.id
    del t["account"]
    return t



# Get the last {count} toots from an author (possibly restricting to tag {tagged} (no hash))
def get_last_toots(toot_id, count=100, tagged=None, min_boosts=0):
    # max_id tracks the most recent fetched toot, allowing us to get pages of older toots
    max_id = None

    # result will be accumulated in the {toots} array
    result_toots = []

    # We fetch pages of toots until we run out of results or surpass {count}
    while len(result_toots) < count:

        # Get a/next page of results
        new_toots = mastodon.account_statuses(id=toot_id, max_id=max_id, exclude_replies=True, exclude_reblogs=True, tagged=tagged)
        if args.verbose>1: print(f"  got {len(new_toots)} toots")

        # quit collating toots if we have reached the end of the paginated results
        if len(new_toots) == 0: break

        # update the "oldest toot seen" filter -- FIXME: maybe should use fetch_next here?
        max_id = min_id(new_toots)

        while len(new_toots) and len(result_toots)<count:
            # Loop over the page of toots and summarise some of the content
            # I'm sure there's a nicer way to do this in non-babytalk python
            candidate_toot = new_toots.pop(0)
            if min_boosts and (candidate_toot.reblogs_count < min_boosts): continue
            candidate_toot.tag_names = tag_names(candidate_toot)
            result_toots.append(remove_author(candidate_toot))

    if args.verbose: print(f"got total of {len(result_toots)} toots")
    return result_toots


#
# Get the list of boosters of toot with {toot_id}, f
# iltering by {min_followers} (ignoring self-boosts by {author}
#
def get_reblogs(toot_id, min_followers=args.followers, limit=args.top, author=None):
    pageno = 1
    total = 0
    page = mastodon.status_reblogged_by(toot_id)
    accounts = []
    while page is not None and len(accounts)<limit:
        if args.verbose: print(f"  processing page {pageno} of {len(page)} records")
        total += len(page)
        for account in page:
            if (account.followers_count >= min_followers) and (author is None or account.id != author):
                accounts.append(account)
        #if args.verbose>1: print("  get_reblogs: fetch next page");
        page = mastodon.fetch_next(page)
        if page:
            pageno = pageno + 1
            #if args.verbose>1: print(f"  get_reblogs: fetched page {pageno}");
    accounts.sort(key=account_followers, reverse=True)
    if args.verbose: print(f"  collated {len(accounts)} boosters from {pageno} pages totalling {total} boosts")
    if limit > 0:
        return accounts[:limit+1]
    return accounts

#
# Summarise a mastodon account, showing name, display name, follow-stats
#
def describe_acct(a):
    print(f"        {a.acct} ({a.display_name}), followed by {a.followers_count} follows {a.following_count}")

#
# Print a summary of a toot, then a list of the "most significant" boosters
#
def describe_boosts(t, slice_len=72):
    boost_count = t.reblogs_count
    if args.verbose or boost_count>=args.boosts:
        print(f"Toot {t.id} at {t.created_at.isoformat()}: {t.reblogs_count} boosts, {t.favourites_count} faves")
    if boost_count < args.boosts: return
    if args.verbose>1: pp.pprint(t)

    print("    ",t.content[slice(slice_len)])
    reblogs = get_reblogs(t.id, author=t.author_id)
    if len(reblogs)>0:
        if len(t.tag_names): print(f"    Tagged {' '.join(t.tag_names)}")
        print("    Significant boosters:")
        for a in reblogs: describe_acct(a)
    print("")

me=mastodon.me()


# fetch all toots (maybe filtering for ones with tag)
# the mastodon api returns tagged lowercase, so, lowercase the tag argument to match that
if args.tagged:
    args.tagged = args.tagged.lower()
    if args.verbose: print(f"Fetching toots matching #{args.tagged}")
toots = get_last_toots(me.id, count=args.count, tagged=args.tagged)
if args.most_boosted_first: toots.sort(key=toot_boosts,reverse=True)
for toot in toots: describe_boosts(toot)

