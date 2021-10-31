from enum import Enum


class Mutations(Enum):
  """
  Enum for mutations
  """
  CREATE_USER = '''\
    mutation CreateUser($email: String!, $name: String!, $username: String!) { 
      createUser(email: $email, name: $name, username: $username) {
        ... on CreateUserSuccess {
          __typename
          userId
        }
        ... on EmailAlreadyInUseError {
          __typename
          email
        }
        ... on UsernameAlreadyExistsError {
          __typename
          username
          alternativeUsername
        }
      }
    }
  '''

  CREATE_USER_INCOMPLETE = '''\
    mutation CreateUserIncomplete($email: String!, $name: String!) {
      createUser(email: $email, name: $name){
        ... on CreateUserSuccess {
          __typename
          userId
        }
      }
  }
  '''


class Queries(Enum):
  """
  Enum for queries
  """	
  
  GET_USER = '''\
    query GetUser($userId: Int!) {
      user(userId: $userId) {
        id
        name
        email
        username
      }
    }
  '''