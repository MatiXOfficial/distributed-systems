import sys
import subprocess
from kazoo.client import KazooClient

class ZNode:

    def __init__(self, zk, path='', name='', app_path='cmd.exe', predecessors=None):
        self.zk = zk
        self.name = name
        self.full_path = path + name + '/'
        self.children = dict()
        self.app_path = app_path
        if predecessors is None:
            self.predecessors = []
        else:
            self.predecessors = predecessors

        if self.name == 'z':  # open the app
            self.app = subprocess.Popen(app_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.descendants = 0


    def start_watching(self):
        @self.zk.ChildrenWatch(self.full_path)
        def watch(children):
            for child in children:  # find children to add
                if child not in self.children:  # add the child
                    print('added', self.full_path + child)
                    child_znode = ZNode(self.zk, self.full_path, child, self.app_path, self.predecessors + [self])
                    child_znode.start_watching()
                    self.children[child] = child_znode

                    for predecessor in self.predecessors + [self]:  # inform the predecessors
                        predecessor.add_descendant()

            to_delete = []
            for child in self.children.keys():  # find children to delete
                if child not in children:  # add the child to be deleted
                    to_delete += [child]
            for child in to_delete:
                print('delete', self.full_path + child)
                self.children[child].stop()
                self.children.pop(child)  # delete the child

                for predecessor in self.predecessors + [self]:  # inform the predecessors
                    predecessor.delete_descendant()

    def stop(self):
        if self.name == 'z':
            self.app.terminate()
     
    def add_descendant(self):
        if self.name == 'z':
            self.descendants += 1
            print(f'{self.full_path[:-1]}: {self.descendants}')

    def delete_descendant(self):
        if self.name == 'z':
            self.descendants -= 1

    def get_descendant(self, path):
        if type(path) is str:
            path = [x for x in path.split('/') if x]
        if not path:
            return self
        return self.children[path[0]].get_descendant(path[1:])

    def __str__(self, indent=0, indent_unit=2):
        result = ' ' * indent * indent_unit + self.name
        if self.name == '':
            result += '/'
        for child in self.children.values():
            result += '\n' + child.__str__(indent + 1)
        return result


class ZWatcher:

    def __init__(self, app_path, hosts=['localhost:2181']):
        self.zk = KazooClient(hosts=hosts)
        self.app_path = app_path
        
    def start(self):
        print('Starting ZWatcher')
        self.zk.start()

        root = ZNode(self.zk, app_path=self.app_path)
        root.start_watching()

        print('type "print <path>" to print the tree from the path')
        while True:
            path = input().split(' ')[1]
            try:
                print(root.get_descendant(path))
            except:
                print('Wrong path!')


    def stop(self):
        print('Stopping ZWatcher')
        self.zk.stop()


if __name__ == '__main__':
    try:
        if len(sys.argv) != 3:
            raise ValueError('Wrong number of arguments! Try: python z_watcher.py <app_path> <server_address1,server_address2>')
        z_watcher = ZWatcher(app_path=sys.argv[1], hosts=sys.argv[2].split(','))
        z_watcher.start()
    except ValueError as err:
        print(err)
    except KeyboardInterrupt:
        z_watcher.stop()