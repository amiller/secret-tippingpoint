set -e
myAccountAddress="secret1vuslf45vatgly9p5px7g276jx4y5hzmgja360m"
# Test net seed, ok to leak
myAccountSeed="salon tower stereo fun you immense wrist raven ten armed scene pond"


# Deploy a contract.
secretcli config chain-id pulsar-2
secretcli config node  https://rpc.pulsar.scrttestnet.com
secretcli config output json
secretcli config keyring-backend test
secretcli config broadcast-mode block
secretcli keys delete SecretIDE-Deployment -y
echo $myAccountSeed | secretcli keys add SecretIDE-Deployment --recover || exit 1
clear
codeId=$(secretcli tx compute store contract.wasm.gz --from SecretIDE-Deployment --gas 772380 -y | jq '.logs[0].events[0].attributes[3].value')
echo "Contract stored successfully! Code ID: $codeId"


# Instantiate a contract. First parameter is contract deployment id, second parameter is contract arguments, passed to function
# 'init' in the contract.
#
contractAddress=$(secretcli tx compute instantiate $codeId '{"count": 100000000}' --label '7cx2dh2' --from 'SecretIDE-Deployment' -y | jq '.logs[0].events[0].attributes[4].value')

