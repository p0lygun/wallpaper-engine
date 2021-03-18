class Storage:
    _global_store_file = None

    def __init__(self, local=False, **kwargs):
        self.local = local
        if not local and Storage._global_store_file is None:
            Storage._global_store_file = dict()
        if local:
            self._store_file = kwargs

    def get(self, key):
        if self.local:
            if key in self._store_file.keys():
                return self._store_file[key]
            else:
                return None
        else:
            if key in Storage._global_store_file.keys():
                return Storage._global_store_file[key]
            else:
                return None

    def store(self, key, value, dict_object=None):
        if key and value is not None or dict_object:
            if key and value is not None:
                if self.local:
                    self._store_file.update({key: value})
                else:
                    Storage._global_store_file.update({key: value})
            elif dict_object:
                if type(dict_object) == dict:
                    if self.local:
                        self._store_file.update(dict_object)
                    else:
                        Storage._global_store_file.update(dict_object)

    def get_storage_file(self):
        if self.local:
            return self._store_file
        else:
            return Storage._global_store_file
