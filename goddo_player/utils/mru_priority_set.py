import collections

class MRUPrioritySet:
    def __init__(self, max_size: int) -> None:
        self._deque = collections.deque()
        self._max_size = max_size

    def peek_last_item(self):
        return self._deque[-1] if len(self._list) > 0 else None

    def put(self, item):
        if self.peek_last_item() == item:
            pass
        elif item in self._list:
            self._deque.remove(item)
            self._deque.append(item)
        elif len(self._list) == self._max_size:
            self._deque.popLeft()
            self._deque.append(item)
        else:
            self._deque.append(item)

    def get_all(self):
        return list(self._deque)

    def clear(self):
        self._deque.clear()

