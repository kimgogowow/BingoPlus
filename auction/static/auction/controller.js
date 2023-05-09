var socket = null

function connectToServer() {
    setTimeout(function() {
        socket = new WebSocket("ws://" + window.location.host + "/auction/data/" + window.location.search)
        socket.onerror = function (error) {
            displayMessage("WebSocket Error: " + error)
        }
        socket.onopen = function (event) {
            displayMessage("WebSocket Connected")
        }
        socket.onclose = function (event) {
            displayMessage("WebSocket Disconnected")
        }
        socket.onmessage = function (event) {
            let metaResp = JSON.parse(event.data)
            console.log(metaResp.type)
            switch (metaResp.type) {
                case "auction_record":
                    displayRecord(metaResp.body)
                    break
                case "display_message":
                    displayMessage(metaResp.body)
                    break
                case "broadcast_timer":
                    displayTimer(metaResp.body)
                    break
                case "broadcast_control":
                    handleControl(metaResp.body)
                    break
                case "error":
                    displayError(metaResp.body)
                    break
                default:
                    displayMessage("Unknown response")
            }
        }
    }, 500)
}

function displayError(message) {
    let errorElement = document.getElementById("error")
    errorElement.innerHTML = message
}

function displayMessage(message) {
    let msgElement = document.getElementById("message")
    msgElement.innerHTML = message
}

function displayRecord(response) {
    console.log(response)
    document.getElementById("curr-price").innerHTML = "Current Price: " + response.bid_price
    document.getElementById("highest-bidder").innerHTML = "Highest Bidder: " + response.buyer

}

function displayTimer(response) {
    document.getElementById("countdown").innerHTML = "Countdown: " + response + "s"
}

function newBid() {
    let bid = document.getElementById("open-price").value
    let data = {
        "bid_price": bid,
        "action": "new"
    }
    socket.send(JSON.stringify(data))
}

function handleControl(response) {
    if (response.action === "end") {
        document.getElementById("bid-button").disabled = true
    }
}

function sendBid() {
    let bid = document.getElementById("bid-price").value
    let data = {
        "bid_price": bid,
        "action": "bid",
        // "auction_id":
    }
    socket.send(JSON.stringify(data))
}