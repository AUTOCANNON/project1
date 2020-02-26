def main():

    def filter_list(l):
    #'return a new list with the strings filtered out'
        filtered_list = []
        bad_stuff = []
        for element in l:
            if element * 0 == 0:
                filtered_list.append(element)
            else:
                bad_stuff.append(element)

        return filter_list

    filter_list([1,2,'a','b'])
    filter_list([1,'a','b',0,15])
    filter_list([1,2,'aasf','1','123',123])

main()