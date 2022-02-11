/* Project specific Javascript goes here. */
const web3 = new Web3(Web3.givenProvider);

async function getAccount() {
  const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
  return accounts[0];
}

async function getChainId() {
    return await ethereum.request({ method: 'eth_chainId' });
}

async function setNetwork() {
    let xhr = new XMLHttpRequest();
    let network;
    xhr.open('GET', '/api/settings/', false);
    xhr.send();
    if (xhr.status !== 200) {
      console.log( xhr.status + ': ' + xhr.statusText );
      return false;
    } else {
      let data = JSON.parse(xhr.responseText);
      network = data['active_network'];
    }
    try {
      await ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: network['chain_id'] }],
      });
      return true;
    } catch (switchError) {
      // This error code indicates that the chain has not been added to MetaMask.
      if (switchError.code === 4902) {
        try {
          await ethereum.request({
            method: 'wallet_addEthereumChain',
            params: [
              {
                chainId: network['chain_id'],
                chainName: network['name'],
                rpcUrls: [network['rpc_url']],
                blockExplorerUrls: [network['url_explorer']],
                nativeCurrency: {symbol: network['ticker']},
              },
            ],
          });
          return true;
        } catch (addError) {
          console.log(addError);
        }
      } else {
          console.log(switchError);
      }
    }
}

function get_contract() {
    let xhr = new XMLHttpRequest();
    let abi;
    let contract_address;
    xhr.open('GET', '/api/contracts/', false);
    xhr.send();
    if (xhr.status !== 200) {
      console.log( xhr.status + ': ' + xhr.statusText );
    } else {
      let data = JSON.parse(xhr.responseText);
      data.forEach((element) => {
        if (element.symbol === 'TNKNFT') {
          abi = element.contract_definitions.abi;
          contract_address = element.address;
          console.log(contract_address);
        }
      })
    }
    return new web3.eth.Contract(abi, contract_address);
}

async function set_account() {
    const address = await getAccount();
    const csrftoken = getCookie('csrftoken');
    let xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/wallets/', false);
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    xhr.setRequestHeader('X-CSRFToken', csrftoken);
    xhr.send("address=" + address);
    return address;
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function contract_buy_token(account, token_id, price) {
    let myContract = get_contract();
    price = web3.utils.toWei(price.toString());
    let txn = myContract.methods.buy(token_id);
    make_txn(txn, account, price)
}

function contract_buy_mint_token(account, token_id, token_uri, price) {
    let myContract = get_contract();
    price = web3.utils.toWei(price.toString());
    let txn = myContract.methods.buyAndMint(token_id, token_uri, price);
    make_txn(txn, account, price)
}

function contract_list_token(account, token_id) {
    let myContract = get_contract();
    let txn = myContract.methods.updateListingStatus(token_id, true);
    make_txn(txn, account, 0)
}

function contract_set_token_price(account, token_id, price) {
    let myContract = get_contract();
    price = web3.utils.toWei(price.toString());
    let txn = myContract.methods.updatePrice(token_id, price);
    make_txn(txn, account, price)
}

function make_txn(txn, account, value) {
    let gas = txn.estimateGas({from: account, value: value});
    gas.then(function (gasAmount) {
        console.log(gasAmount);
        web3.eth.getTransactionCount(account).then(function (nonce) {
            console.log(nonce);
            web3.eth.getGasPrice().then(function (gas_price) {
                console.log(gas_price);
                txn.send({
                    gas: gasAmount,
                    from: account,
                    gasPrice: gas_price,
                    nonce: nonce,
                    value: value
                }).on('transactionHash', (hash) => {
                    console.log(hash);
                }).on('receipt', (receipt) => {
                    const csrftoken = getCookie('csrftoken');
                    let xhr = new XMLHttpRequest();
                    xhr.open('POST', '/api/read-events/', false);
                    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
                    xhr.setRequestHeader('X-CSRFToken', csrftoken);
                    xhr.send("to=" + receipt['to'] + "&transactionHash=" + receipt['transactionHash']);
                    document.getElementById("tx-spinner").style.display = 'none';
                    if (xhr.status !== 200) {
                      let data = JSON.parse(xhr.responseText);
                      alert(data['error']);
                    } else {
                      document.getElementById('success-modal').style.display = 'block';
                    }
                }).on('error', (e) => {
			        console.error(e);
                    document.getElementById("tx-spinner").style.display = 'none';
                });
            })
        })
    }).catch(err => {console.log(err)});
}

function buy_token(token_id, price) {
    document.getElementById("tx-spinner").style.display = "block";
    getAccount().then(account => {
        contract_buy_token(account, token_id, price);
    });
}
function buy_and_mint_token(tank_id, token_uri, price) {
    document.getElementById("tx-spinner").style.display = "block";
    getAccount().then(account => {
      let xhr = new XMLHttpRequest();
      xhr.open('GET', '/api/new_token_id/' + tank_id, false);
      xhr.send();
      if (xhr.status !== 200) {
          console.log( xhr.status + ': ' + xhr.statusText );
      } else {
          let data = JSON.parse(xhr.responseText);
          const token_id = data['token_id']
          contract_buy_mint_token(account, token_id, token_uri, price);
      }
    });
}
