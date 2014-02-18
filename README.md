infoquery
=========

Query infoblox appliance via api

Currently, supports hostname query, does a greedy match against -n option
i.e.

./infoquery.py -n mail
would return results like
Host o2.email.schoolfeed.com has IP 208.117.51.136
Host ndbmail0245.iad1.classmates.com has IP 208.84.41.108
Host ndbmail02.prod.las1.cmates.com has IP 10.14.113.12
Host mail-ext.prod.iad1.cmates.com has IP 10.12.60.43
Host ndbmail0248.prod.iad1.cmates.com has IP 10.12.113.48

Basically, anything that has mail as part of it's fqdn.  Does not currently
understand file globbing or RE

Also, if infoblox doesn't create a host object as the result of dhcp lease, it
won't show up in this query.


├── config
│   └── infoquery.conf
├── LICENSE
├── Makefile
├── Makefile.common
├── packaging
│   ├── authors.sh
│   ├── deb
│   │   └── infoquery.in
│   └── rpm
│       └── infoquery.spec.in
├── README.md
└── src
    └── infoquery.py

