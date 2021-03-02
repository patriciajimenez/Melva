# BaseClustererFactory.py


class BaseClustererFactory:

    @staticmethod
    def create(module_name, clazz_name, configuration):
        module = __import__(module_name)
        clazz = getattr(module, clazz_name)
        result = clazz(configuration)

        return result
