
class VfsTree(object):
    def __init__(self):
        self.root = VfsNode('')

    def follow_and_set(self, nodelist, inode):
        r = self.root
        for item in nodelist[1:]:
            r = r.add_or_get(item)
        if inode:
            r.set(inode)

    def sorted(self):
        return self.root.sorted()


class VfsNode(object):
    def __init__(self, name, data=None):
        self.name = name
        self.children = []
        self.data = data

    def add_or_get(self, name):
        for child in self.children:
            if child.name == name:
                return child
        new_child = VfsNode(name)
        self.children.append(new_child)
        return new_child

    def set(self, val):
        if self.data:
            raise Exception("item %s already set!" % self.name)
        else:
            self.data = val

    def sorted(self):
        if self.data:
            yield self.data
        for child in self.children:
            for item in child.sorted():
                yield item

