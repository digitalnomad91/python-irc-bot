from google.appengine.api import search

# a query string like this comes from the client
query = "stories"
try:
  index = search.Index(INDEX_NAME)
  search_results = index.search(query)
  for doc in search_results:
    # process doc ..
  except search.Error:
    print search.Error
    # ...

