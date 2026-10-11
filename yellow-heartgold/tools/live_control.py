#!/usr/bin/env python3
"""Agent bridge for /video on, /video off and explicit DS controller presses."""
import argparse,json,os
from urllib.request import Request,urlopen

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['on','off','status','press','stop'])
    p.add_argument('button',nargs='?')
    p.add_argument('--frames',type=int,default=8)
    p.add_argument('--url',default='http://127.0.0.1:8080')
    a=p.parse_args(); headers={'X-Live-Token':os.environ.get('LIVE_TEST_TOKEN','')}
    if a.command=='status': request=Request(a.url+'/status',headers=headers)
    else:
        body={'video':a.command=='on'} if a.command in ('on','off') else {'stop':True} if a.command=='stop' else {'button':a.button,'frames':a.frames}
        headers['Content-Type']='application/json'
        request=Request(a.url+'/control',data=json.dumps(body).encode(),headers=headers)
    with urlopen(request,timeout=5) as response: print(response.read().decode())

if __name__=='__main__':main()
