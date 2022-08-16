"""
Defines a class to execute a normally blocking task asynchronously (like LED requests).

Essentially, it simply allows a shorthand syntax for defining a thread
that executes an arbitrary function and terminates.
So we con't have to create anonymous subclasses and start the thread and everything every time.

The thread starts automatically as soon as the Vow is created.
That's part of the shorthand effort.

The function cannot take no arguments as of now.
But we can use lambdas or partially applied functions anyway, so I'm not worried.

Use note: "lambda: some_function(...)" is an anonymous function that takes no argument
and executes some_function with the given arguments.
I expect to use this syntax when creating Vows, so I'm leaving this message for the others to know.

Also note, the concept of this is exactly the opposite of the BehaviorWaitable,
which is about waiting and blocking on a normally non-blocking task (the behavior call).

"Vow" is a synonym of "Promise".

P.S.: Turns out this solution was born dead as I soon found a better way to handle
the longer LED animations.
I think Vows may still have some general utility, so I'm leaving them here
in case we find another application for them.

TODO delete the P.S. or this whole file before turning in
     (depending on whether we found a use for Vows or not)
"""

import threading

class Vow(threading.Thread):
    def __init__(self, fn):
        threading.Thread.__init__(self)
        self.fn = fn;
        self.start();
    
    def run(self):
        self.fn()
    
    # use .join to wait