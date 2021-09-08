import { InMemoryCache } from "@apollo/client/core";
import { SvelteApolloClient } from "svelte-apollo-client";

export const client = SvelteApolloClient({
  uri: "http://localhost:8000/graphql",
  cache: new InMemoryCache(),
  
});