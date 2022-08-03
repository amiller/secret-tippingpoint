#!/bin/python
# Call this from the project root directory, not from inside tests
#

walletAdress = "secret1vuslf45vatgly9p5px7g276jx4y5hzmgja360m"
walletSeed = "salon tower stereo fun you immense wrist raven ten armed scene pond \n" #Test net seed, ok to leak
PROJECT_PATH = "./"

from gc import get_count
import subprocess
import sys
import os
import string, random, json


def runcmd(cmd, canFail = False):
  fail = False
  try:
    cmd = f"{cmd}"
    print(cmd)
    result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    if result.returncode != 0:
      match result.returncode:
        case _:
          print(f"UNKNOWN ERROR {result.returncode}")
      raise BaseException("Failed")
  except subprocess.CalledProcessError as e:
    result = e
    fail = True
  except BaseException as e:
    fail = True
  finally:
    print(result.stdout.decode("utf8"))
    if fail and not canFail:
      os._exit(-1)
  return fail, result.stdout.decode("utf8")


def randomHexStr(len=10):
  return "".join([random.choice(string.ascii_letters + string.digits) for n in range(len)])

def changeWallet(seed=None):
  runcmd("secretcli config chain-id pulsar-2")
  runcmd("secretcli config node https://rpc.pulsar.scrttestnet.com")
  runcmd("secretcli config output json")
  runcmd("secretcli config keyring-backend test")
  runcmd("secretcli config broadcast-mode block")
  runcmd("secretcli keys delete SecretIDE-Deployment -y", True)
  _, data = runcmd(f"echo '{seed}' | secretcli keys add SecretIDE-Deployment --recover || exit 1")
  address = json.loads(data)['address'].strip()
  return address  

def publishAndInitContract(name, /, *, params='{"counter": 100000}', path=PROJECT_PATH, seed=walletSeed):
  addr = changeWallet(seed)
  os.chdir(PROJECT_PATH)
  runcmd("make build")
  _, codeId = runcmd("secretcli tx compute store contract.wasm.gz --from SecretIDE-Deployment --gas 2000000 -y")
  codeId = json.loads(codeId.strip())['logs'][0]['events'][0]['attributes'][3]['value']
  print(f"Contract stored successfully! Code ID: {codeId}")
  _, contractAddress = runcmd(f"secretcli tx compute instantiate {codeId} '{params}' --label '{name}' --from 'SecretIDE-Deployment' -y")
  contractAddress = json.loads(contractAddress.strip())['logs'][0]['events'][0]['attributes'][4]['value']
  return codeId, contractAddress

def queryContract(contractAddress, functionName, arg={}):
  err, rv = runcmd(f"secretcli query compute query {contractAddress} '{{\"{functionName}\":{json.dumps(arg)}}}'", True)
  if not err:
    return json.loads(rv)
  else:
    return rv

def executeContract(contractAddress, functionName, arg={}, /, *, caller=walletAdress):
  err, rv = runcmd(f"secretcli tx compute execute {contractAddress} '{{\"{functionName}\":{json.dumps(arg)}}}' --from '{caller}' -y", True)
  if not err:
    return json.loads(rv)
  else:
    return rv

#

def testCreation():
  name = randomHexStr()
  id, addr = publishAndInitContract(name, params='{"count": 100000}')
  rv = queryContract(addr, 'get_count', {'id': 1})
  assert rv == ""
  rv = executeContract(addr, 'create', {'id': 1})
  rv = queryContract(addr, 'get_count', {'id': 1})
  assert(rv['count'] == 0)
  rv = queryContract(addr, 'get_count', {'id': 0})
  assert rv == ""
  rv = queryContract(addr, 'get_count', {'id': 2})
  assert rv == ""
  rv = executeContract(addr, 'create', {'id': 0})
  rv = queryContract(addr, 'get_count', {'id': 0})
  assert(rv['count'] == 0)
  rv = executeContract(addr, 'create', {'id': 2})
  rv = queryContract(addr, 'get_count', {'id': 2})
  assert(rv['count'] == 0)

  # Double creation:
  #
  rv = executeContract(addr, 'create', {'id': 0})
  assert rv['code'] == 3

  # UNDONE():
  # Non leader creation:
  #
  
def testIncrement():
  name = randomHexStr()
  id, addr = publishAndInitContract(name, params='{"count": 100000}')
  assert executeContract(addr, 'create', {'id': 1})['code'] == 0
  assert executeContract(addr, 'create', {'id': 0})['code'] == 0
  assert queryContract(addr, 'get_count', {'id': 0})['count'] == 0
  assert queryContract(addr, 'get_count', {'id': 1})['count'] == 0
  rv = executeContract(addr, 'increment', {'id': 1})
  assert rv['code'] == 0
  assert queryContract(addr, 'get_count', {'id': 0})['count'] == 0
  assert queryContract(addr, 'get_count', {'id': 1})['count'] == 1

  rv = executeContract(addr, 'increment', {'id': 0})
  assert rv['code'] == 0
  assert queryContract(addr, 'get_count', {'id': 0})['count'] == 1
  assert queryContract(addr, 'get_count', {'id': 1})['count'] == 1

  assert executeContract(addr, 'create', {'id': 2})['code'] == 0
  assert executeContract(addr, 'create', {'id': 3})['code'] == 0
  assert queryContract(addr, 'get_count', {'id': 2})['count'] == 0
  assert queryContract(addr, 'get_count', {'id': 3})['count'] == 0
  rv = executeContract(addr, 'increment', {'id': 2})
  assert rv['code'] == 0
  rv = executeContract(addr, 'increment', {'id': 3})
  assert rv['code'] == 0

  assert queryContract(addr, 'get_count', {'id': 0})['count'] == 1
  assert queryContract(addr, 'get_count', {'id': 1})['count'] == 1
  assert queryContract(addr, 'get_count', {'id': 2})['count'] == 1
  assert queryContract(addr, 'get_count', {'id': 3})['count'] == 1

if __name__ == "__main__":
  testCreation()
  testIncrement()