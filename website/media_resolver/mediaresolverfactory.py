from imageresolver import ImageResolver


class MediaResolverFactory:
    def __init__(self):
        pass

    resolvers = {
        'image': ImageResolver,
    }

    separator = '\r\n'.encode()
    @staticmethod
    def produce(type, data):
        if type in MediaResolverFactory.resolvers:
            return MediaResolverFactory.resolvers[type](type, data)
        raise Exception('such media type not supported')
