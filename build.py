import os
import logging

def main(target):
    os.makedirs(target,exist_ok=True)
    with open(f"{target}/index.html") as q:
        q.write('Hello World')

if __name__ == '__main__':
    main('./dist')