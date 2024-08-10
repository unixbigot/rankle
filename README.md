# Rankle - find out why you have gone metaviral

This program uses the python mastodon api to look at toots and determine which are the 
accounts with the highest follower count that retooted you.

The intent is to answer "halp, why have my notifications assplode"

## Example usage:

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
        JessTheUnstill@infosec.exchange (Jess👾), followed by REDACTED follows 996
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

```
❯ ./rankle.py --help
usage: rankle.py [-h] [-c [COUNT]] [-v] [--base [BASE]] [--tagged TAGGED] [--retoots RETOOTS] [--top TOP] [--followers FOLLOWERS] [--token [TOKEN]]

Rank toots by popularity

options:
  -h, --help            show this help message and exit
  -c [COUNT], --count [COUNT]
                        number of toots to examine
  -v, --verbose         include extra detail
  --base [BASE]         api base url
  --tagged TAGGED       consider toots with tag
  --retoots RETOOTS     consider toots with at least N retoots
  --top TOP             describe the top N retooters
  --followers FOLLOWERS
                        highlight retooters with at least N followers
  --token [TOKEN]       api authentication token
```

## Advanced usage

Inspect the last `500` toots that are tagged `#MicroFiction` and have at
least `100 boosts`, printing out the top boosters that have more than
`1000 followers`:

```
on No in rankle on  main [!?⇣] via 🐍 v3.12.4
❯ ./rankle.py --count 500 --followers 1000 --retoots 100 --tagged microfiction
Toot 112685247251950487 at 2024-06-26T22:20:18.274000+00:00: 159 retoots, 221 faves
     <p>The Unicode Consortium announces release 17.2.0 of the Unicode standa
    Tagged tootfic microfiction poweronstorytoot
    Significant boosters:
        zens@merveilles.town (Luci for dyeing), followed by 1696 follows 492
        stilgherrian@eigenmagic.net (Stilgherrian), followed by 1542 follows 856
        OctaviaConAmore@cutie.city (Octavia con Amore :pink_moon_and_stars:), followed by 1420 follows 1213
        MOULE@moule.world (MOULE #WheresRocky), followed by 1355 follows 1470
        oblomov@sociale.network (Oblomov), followed by 1234 follows 314
        quincy@chaos.social (Quincy), followed by 1052 follows 4325

Toot 112492699120335077 at 2024-05-23T22:12:46.949000+00:00: 104 retoots, 199 faves
     <p>The cheque said “AMOUNT: two dollars and forty cents BEING FOR: class
    Tagged tootfic microfiction poweronstorytoot
    Significant boosters:
        rc2014@oldbytes.space (RC2014), followed by 2261 follows 239
        diyelectromusic@mastodon.social (diyelectromusic), followed by 1485 follows 402
        stufromoz (Helpdesk Stu), followed by 1163 follows 611
        Dtl@mastodon.social (Dr David Mills), followed by 1143 follows 1664
        marnanel@queer.party (marnanel), followed by 1075 follows 971
        s0@cathode.church (s0: Soldering Saboteuse), followed by 1021
		follows 351
		
etc.etc.		
```
