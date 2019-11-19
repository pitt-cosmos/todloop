import os

def list2file(lst, filename):
    """Write a list to a given filename, overwrite if
    it exists"""
    with open(filename, "w") as f:
        for i in lst:
            f.write(i+'\n')

def file2list(filename):
    """Load a file into a list"""
    with open(filename, "r") as f:
        lines = f.readlines()
        return [l.strip() for l in lines]

def append2file(lst, filename):
    """Append a list to a given filename"""
    # if the file doesn't exist, create one
    if not os.path.exists(filename):
        list2file(lst, filename)
    else:  # if file exists, load the existing list
        lst_exist = file2list(filename)
        lst_new = list(set(lst_exist).union(set(lst)))
        list2file(lst_new, filename)
