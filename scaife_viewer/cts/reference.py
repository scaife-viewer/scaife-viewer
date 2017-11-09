from MyCapytain.common.reference import URN as BaseURN


class URN(BaseURN):

    def __hash__(self):
        return hash(str(self))
