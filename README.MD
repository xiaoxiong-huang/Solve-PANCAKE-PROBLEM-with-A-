# Homework 2 for CS131
Informed_search
Implemention of A* and Uninform search algo

## Usage
```bash
#   Run the program without pass in the pancake list:
python3 Informed_Search.py
#   Run the program by passing in the pancake list:
python3 Informed_Search.py 5 3 2 4 1
```
## input format
```bash
#   The way I have my pancake list is to have the plate
#   at very first place in the list, follow by pancakes.
#   Also after sorted, top pancake must be smaller than 
#   bottom pancake/plate.
#   Please pass in at least two pancakes.
8 6 5 4 3 2 1 7     #is a vaild input
8 6 5 3 2 1 7       #is not vaild, because miss 4
6 8 5 4 3 2 1 7     #is not vaild, because first index should be 8
```

## Detail
Detail about the code can be found in comment, I implemented both A* and Uninform in same file.
A* is about 5 times faster than Uninform, except for some edge case. After invoking the A*, it will
ask you if you want to start a uninform search for the same pancake list. No need to type in any thing, just control c if you want to exit, or hit enter to invoke the uninform search.
