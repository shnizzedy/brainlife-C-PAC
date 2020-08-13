#!python3

import os

bindings = set()

for dirpath, dirnames, filenames in os.walk("bids"):
    for file in [
        os.path.join(
            dirpath,
            filename
        ) for filename in filenames
    ]:
        if os.path.islink(file):
            bindings.add(
                os.path.dirname(os.path.abspath(
                    os.readlink(file)
                ))
            )
            
print(' '.join([f'-B {binding}' for binding in bindings]))