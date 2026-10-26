"""TEST ONLY: stand next to an item ball (argv: x z of the ball's south tile), face it, press A, screenshot the pickup message. env DS_ROM/DS_OUT as ds_session."""
import sys
sys.path.insert(0, '/home/thatanarchydude/code/corvus-workshop/yellow-heartgold/tools')
import ds_session as d
UP, A = 4, 8
d.boot()
d.run(12, UP); d.run(30)
for i in range(4):
    d.run(6, A); d.run(60); d.shot('p%d.png' % i)
