import ApolloClient from 'apollo-boost';
import { Base64 } from 'js-base64';


const apolloConfig = {
  uri: process.env.VUE_APP_ATLAS_GRAPHQL_ENDPOINT
    // @@@
    || '//localhost:8000/atlas/graphql/',
};

const client = new ApolloClient(apolloConfig);

const GraphQLPlugin = {
  install: (Vue) => {
    Vue.mixin({
      data: () => ({ gqlData: null }),
      computed: {
        gqlQuery: () => null,
      },
      watch: {
        gqlQuery: {
          immediate: true,
          handler() {
            if (this.gqlQuery) {
              this.$gql(this.gqlQuery).then((data) => {
                this.gqlData = data;
              });
            }
          },
        },
      },
    });

    // eslint-disable-next-line no-param-reassign
    Vue.prototype.$gql = q => client.query({ query: q }).then(data => data.data);
  },
};

export { client as gqlclient };
export default GraphQLPlugin;
