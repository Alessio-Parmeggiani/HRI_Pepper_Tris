"""
Checking that all numbers in the range [0, NUMBERS_NO - 1] can be visited
by the sequence that starts at STARTING_NO and adds ADDED_NO at each step.

This should be true as long as ADDED_NO and NUMBERS_NO share no prime factors.

This is useful to know for easily generating non-boring user IDs.
"""

STARTING_NO =     0
ADDED_NO    =  1111
NUMBERS_NO  = 10000

visited = [False for i in range(NUMBERS_NO)]

for i in range(NUMBERS_NO):
    n = (STARTING_NO + i*ADDED_NO) % NUMBERS_NO
    visited[n] = True

all_ok = True
for i in range(NUMBERS_NO):
    if not visited[i]:
        all_ok = False
        print ("NOT VISITED", i)

if all_ok:
    print "All OK"
