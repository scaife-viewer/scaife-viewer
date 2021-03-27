import graphene
from scaife_viewer.atlas import schema as atlas_schema


class Query(atlas_schema.Query, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass


schema = graphene.Schema(query=Query)
