/**
 * Apollo Client configuration for HireMeBahamas.
 * 
 * Features:
 * - HTTP Link for queries and mutations
 * - WebSocket Link for subscriptions
 * - In-Memory Cache with type policies for pagination
 * - Automatic persistence to IndexedDB for offline support
 * - Request deduplication and batching
 */
import {
  ApolloClient,
  InMemoryCache,
  ApolloLink,
  HttpLink,
  split,
  Observable,
  NormalizedCacheObject,
} from '@apollo/client';
import { GraphQLWsLink } from '@apollo/client/link/subscriptions';
import { getMainDefinition } from '@apollo/client/utilities';
import { createClient } from 'graphql-ws';
import { onError } from '@apollo/client/link/error';
import { get, set, del } from 'idb-keyval';
import { API_BASE_URL } from '@/lib/api';

// Use safe URL builder for GraphQL endpoint
const GRAPHQL_ENDPOINT = `${API_BASE_URL}/api/graphql`;
const WS_ENDPOINT = GRAPHQL_ENDPOINT.replace(/^http/, 'ws');

// Cache persistence keys
const CACHE_PERSISTENCE_KEY = 'apollo-cache';

/**
 * Get auth token from localStorage
 */
const getAuthToken = (): string | null => {
  return localStorage.getItem('token');
};

/**
 * HTTP Link for queries and mutations
 */
const httpLink = new HttpLink({
  uri: GRAPHQL_ENDPOINT,
  credentials: 'include',
});

/**
 * Auth Link - adds authorization header
 */
const authLink = new ApolloLink((operation, forward) => {
  const token = getAuthToken();
  
  operation.setContext(({ headers = {} }) => ({
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : '',
    },
  }));
  
  return forward(operation);
});

/**
 * Error handling link
 */
const errorLink = onError(({ graphQLErrors, networkError, operation }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path }) => {
      console.error(
        `[GraphQL error]: Message: ${message}, Location: ${locations}, Path: ${path}, Operation: ${operation.operationName}`
      );
    });
  }
  
  if (networkError) {
    console.error(`[Network error]: ${networkError}`);
  }
});

/**
 * WebSocket Link for subscriptions (created lazily)
 */
let wsLink: GraphQLWsLink | null = null;

const createWsLink = () => {
  if (!wsLink) {
    const client = createClient({
      url: WS_ENDPOINT,
      connectionParams: () => {
        const token = getAuthToken();
        return token ? { authorization: `Bearer ${token}` } : {};
      },
      retryAttempts: 5,
      shouldRetry: () => true,
    });
    
    wsLink = new GraphQLWsLink(client);
  }
  return wsLink;
};

/**
 * Split link - routes subscriptions to WS, everything else to HTTP
 */
const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return (
      definition.kind === 'OperationDefinition' &&
      definition.operation === 'subscription'
    );
  },
  // For subscriptions, create/use WS link
  new ApolloLink((operation) => {
    const link = createWsLink();
    return link.request(operation) || Observable.of();
  }),
  // For queries/mutations, use HTTP
  ApolloLink.from([errorLink, authLink, httpLink])
);

/**
 * InMemory Cache with type policies
 */
const cache = new InMemoryCache({
  typePolicies: {
    Query: {
      fields: {
        // Relay-style pagination for posts
        posts: {
          keyArgs: ['userId'],
          merge(existing, incoming, { args }) {
            if (!existing || !args?.after) {
              return incoming;
            }
            return {
              ...incoming,
              edges: [...(existing.edges || []), ...(incoming.edges || [])],
            };
          },
        },
        // Relay-style pagination for messages
        messages: {
          keyArgs: ['conversationId'],
          merge(existing, incoming, { args }) {
            if (!existing || !args?.after) {
              return incoming;
            }
            return {
              ...incoming,
              edges: [...(existing.edges || []), ...(incoming.edges || [])],
            };
          },
        },
        // Relay-style pagination for notifications
        notifications: {
          keyArgs: ['unreadOnly'],
          merge(existing, incoming, { args }) {
            if (!existing || !args?.after) {
              return incoming;
            }
            return {
              ...incoming,
              edges: [...(existing.edges || []), ...(incoming.edges || [])],
            };
          },
        },
      },
    },
    PostType: {
      keyFields: ['id'],
    },
    UserType: {
      keyFields: ['id'],
    },
    MessageType: {
      keyFields: ['id'],
    },
    ConversationType: {
      keyFields: ['id'],
    },
    NotificationType: {
      keyFields: ['id'],
    },
  },
});

/**
 * Persist cache to IndexedDB
 */
const persistCache = async () => {
  try {
    const serializedCache = cache.extract();
    await set(CACHE_PERSISTENCE_KEY, serializedCache);
  } catch (error) {
    console.error('Failed to persist cache:', error);
  }
};

/**
 * Restore cache from IndexedDB
 */
const restoreCache = async (): Promise<boolean> => {
  try {
    const serializedCache = await get(CACHE_PERSISTENCE_KEY);
    if (serializedCache) {
      cache.restore(serializedCache);
      return true;
    }
    return false;
  } catch (error) {
    console.error('Failed to restore cache:', error);
    return false;
  }
};

/**
 * Clear persisted cache
 */
export const clearPersistedCache = async (): Promise<void> => {
  try {
    await del(CACHE_PERSISTENCE_KEY);
    cache.reset();
  } catch (error) {
    console.error('Failed to clear cache:', error);
  }
};

/**
 * Apollo Client instance
 */
export const apolloClient: ApolloClient<NormalizedCacheObject> = new ApolloClient({
  link: splitLink,
  cache,
  defaultOptions: {
    watchQuery: {
      fetchPolicy: 'cache-and-network',
      nextFetchPolicy: 'cache-first',
    },
    query: {
      fetchPolicy: 'cache-first',
    },
    mutate: {
      fetchPolicy: 'no-cache',
    },
  },
  // Enable query deduplication
  queryDeduplication: true,
});

/**
 * Initialize Apollo Client with cache restoration
 */
export const initializeApolloClient = async (): Promise<ApolloClient<NormalizedCacheObject>> => {
  // Try to restore cache from IndexedDB
  await restoreCache();
  
  // Set up cache persistence on changes
  apolloClient.onClearStore(async () => {
    await del(CACHE_PERSISTENCE_KEY);
  });
  
  // Persist cache periodically (every 5 minutes to balance performance and data persistence)
  setInterval(persistCache, 300000);
  
  // Also persist cache when user navigates away
  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', () => {
      persistCache();
    });
    
    // Persist on visibility change (user switches tabs)
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') {
        persistCache();
      }
    });
  }
  
  return apolloClient;
};

/**
 * Prefetch a query (for hover prefetching)
 */
export const prefetchQuery = async <TVariables = Record<string, unknown>>(
  query: Parameters<typeof apolloClient.query>[0]['query'],
  variables?: TVariables
) => {
  try {
    await apolloClient.query({
      query,
      variables: variables as Record<string, unknown>,
      fetchPolicy: 'cache-first',
    });
  } catch (error) {
    // Silently fail for prefetch - not critical
    console.debug('Prefetch failed:', error);
  }
};

export default apolloClient;
