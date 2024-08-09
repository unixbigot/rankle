# Rankle - find out why you have gone metaviral

This program uses the python mastodon api to look at toots and determine which are the 
accounts with the highest follower count that retooted you.

The intent is to answer "halp, why have my notifications assplode"

example usage:

```
❯ ./rankle.py
got 20 toots
Toot 112928492034667014 at 2024-08-08T21:20:39.104000+00:00: 13 retoots, 18 faves
     <p>SAN JOSÉ (AP) - AI startup upgrad.er offers an innovative air travel
    Reblogged by
        futzle@old.mermaid.town (Deborah Pickett), followed by 2770 follows 955

Toot 112923259880042838 at 2024-08-07T23:10:02.761000+00:00: 10 retoots, 20 faves
     <p>I PUT IT TO YOU, Mr Maggot that you were seen—by the witnesses from w
    Reblogged by
        JessTheUnstill@infosec.exchange (Jess👾), followed by 3890 follows 996
        futzle@old.mermaid.town (Deborah Pickett), followed by 2770 follows 955
        stufromoz (Helpdesk Stu), followed by 1161 follows 611

Toot 112922750541447114 at 2024-08-07T21:00:30.870000+00:00: 11 retoots, 24 faves
     <p>Who called it “The Return of the King” when “Gondor Reveal Party” was
    Reblogged by
        futzle@old.mermaid.town (Deborah Pickett), followed by 2770 follows 955
        stufromoz (Helpdesk Stu), followed by 1161 follows 611
```

Options (use --help) help can be used to control which toots are inspected and what cutoffs
to use for follower count etc.

This script is not finished, it does not correctly do paginated queries to find all retooters.
If you want it finished, bug me or help me.



