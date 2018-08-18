import abc
import copy

from .helpers import get_database, get_collection, manager_factory, find_token
from ..exceptions import DocumentInitDataError

DOC_DATA = '#data'

DOC_INIT_DATA = '__init_data__'
DOC_DATABASE = '__database__'
DOC_COLLECTION = '__collection__'
DOC_ABSTRACT = '__abstract__'


class DocBaseMeta(type):
    def __new__(mcs, name, bases, clsargs):
        abstract = clsargs.pop(DOC_ABSTRACT, False)
        if abstract:
            return super().__new__(mcs, name, bases, clsargs)

        database_attrs = clsargs.pop(
            DOC_DATABASE, find_token(bases, DOC_DATABASE)
        )
        if not database_attrs:
            return super().__new__(mcs, name, bases, clsargs)

        collection_attrs = clsargs.pop(
            DOC_COLLECTION, find_token(bases, DOC_COLLECTION)
        )
        clsargs[DOC_INIT_DATA] = clsargs.pop(
            DOC_INIT_DATA, find_token(bases, DOC_INIT_DATA) or {}
        )

        cls = super().__new__(mcs, name, bases, clsargs)

        db = get_database(**database_attrs)
        collection = get_collection(cls, db, collection_attrs)

        cls.manager = manager_factory(cls, collection)

        return cls

    def __call__(cls, *args, **kwargs):
        instance = super().__call__()

        init_data = cls.get_init_data(*args, **kwargs)
        default_init_data = cls.get_default_init_data()

        row_init_data = {**default_init_data, **init_data}
        called_init_data = {k: v(instance) for k, v in row_init_data.items() if callable(v)}
        instance.__dict__[DOC_DATA] = {**row_init_data, **called_init_data}

        return instance

    def get_init_data(cls, *args, **kwargs):
        if args and kwargs:
            raise DocumentInitDataError('Only arg or only kwargs')

        init_data = copy.copy(args[0] if args else kwargs)
        cls.check_init_data(init_data)
        return init_data

    def get_default_init_data(cls):
        default_init_data = copy.copy(cls.__dict__.get(DOC_INIT_DATA, {}))
        cls.check_init_data(default_init_data)
        return default_init_data

    @staticmethod
    def check_init_data(init_data):
        if not isinstance(init_data, dict):
            raise DocumentInitDataError('Init data must be an instance of dict')


class DocMeta(DocBaseMeta, abc.ABCMeta):
    pass