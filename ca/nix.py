# coding=utf-8


def items_of_type(lst, the_type):
    return [x for x in lst if x.type == the_type]


def item_of_type(lst, the_type):
    items = items_of_type(lst, the_type)
    if len(items) != 1:
        raise RuntimeError("Bleh %d" % len(items))
    return items[0]
