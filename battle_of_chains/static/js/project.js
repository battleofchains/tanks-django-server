/* Project specific Javascript goes here. */

async function getAccount() {
  const accounts = await ethereum.request({ method: 'eth_requestAccounts' });
  return accounts[0];
}

function get_contract() {
    const web3 = new Web3(Web3.givenProvider);
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
        if (element.symbol === 'BOFCNFT') {
          abi = element.contract_definitions.abi;
          contract_address = element.address;
          console.log(contract_address);
        }
      })
    }
    return new web3.eth.Contract(abi, contract_address);
}

function set_account() {
    getAccount().then(function (account) {
      const csrftoken = getCookie('csrftoken');
      let xhr = new XMLHttpRequest();
      xhr.open('POST', '/api/wallets/', false);
      xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
      xhr.setRequestHeader('X-CSRFToken', csrftoken);
      xhr.send("address=" + account);
    });
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

function contract_buy_token(token_id, price) {
    const web3 = new Web3(Web3.givenProvider);
    getAccount().then(function (account) {
      let myContract = get_contract();
      let txn = myContract.methods.buy(token_id);
      let gas = txn.estimateGas({from: account, value: web3.utils.toWei(price)});
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
              value: web3.utils.toWei(price)
            }).then(function(receipt){
                console.log(receipt);
            });
          })
        })
       })
    });
}

function contract_list_token(token_id) {
    const web3 = new Web3(Web3.givenProvider);
    getAccount().then(function (account) {
      let myContract = get_contract();
      let txn = myContract.methods.updateListingStatus(token_id, true);
      let gas = txn.estimateGas({from: account});
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
              nonce: nonce
            }).then(function(receipt){
                console.log(receipt);
            });
          })
        })
       })
    });
}
