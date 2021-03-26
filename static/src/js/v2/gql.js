import VueApollo from 'vue-apollo';
import { ApolloClient, HttpLink } from '@apollo/client/core';
import { InMemoryCache } from '@apollo/client/cache';
import router from '../router';

const link = new HttpLink({
  uri: process.env.VUE_APP_ATLAS_GRAPHQL_ENDPOINT
    || `${router.options.base}atlas/graphql/`,
});
const cache = new InMemoryCache({
  // NOTE: passageTextParts currently is not used
  // under Scaife Viewer v1
  // typePolicies: {
  //   Query: {
  //     fields: {
  //       passageTextParts: {
  //         merge: false,
  //       },
  //     },
  //   },
  // },
});
const client = new ApolloClient({ link, cache });

const apolloProvider = new VueApollo({
  defaultClient: client,
});

export default apolloProvider;
