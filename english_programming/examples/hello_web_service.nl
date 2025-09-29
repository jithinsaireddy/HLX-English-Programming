# Fetch a public API and print a processed field
set url to "https://example.com/api"
http get from url and store result in body
parse json body and store result in obj
get json obj key "status" and store result in st
print st
