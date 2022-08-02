# Do a query, queries are handled the 'query' function in the contract
#
secretcli query compute query $contractAddress '{"get_count":{}}'

# Increment and reset, transactions are handled by the 'handle' function in the contract
#
yes | secretcli tx compute execute $contractAddress '{"increment":{}}' --from $myAccountAddress | jq
yes | secretcli tx compute execute $contractAddress '{"reset":{"count": 42}}' --from $myAccountAddress | jq