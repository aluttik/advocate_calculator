def print_collection(collection, depth=0, indent=2):
    whitespace = (' ' * indent)

    if type(collection) is dict:
        print (depth * whitespace) + '{'
        for key, val in collection.items():
            if hasattr(val, '__iter__'):
                print (whitespace * (depth + 1)) + key + ':'
                print_collection(val, depth + 1, indent)
            else:
                print (whitespace * (depth + 1)) + key + ': ' + val
        print (whitespace * depth) + '}'

    elif type(collection) is list:
        print (whitespace * depth) + '['
        for val in collection:
            if hasattr(val, '__iter__'):
                print_collection(val, depth + 1, indent)
            else:
                print (whitespace * (depth + 1)) +val
        print (whitespace * depth) + ']'

    else:
        print (whitespace * depth) + collection
