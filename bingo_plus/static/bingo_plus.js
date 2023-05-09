var socket = null
var curr_mutation = null

function loadWait() {
    const queryString = window.location.search
    const urlParams = new URLSearchParams(queryString)
    var game_username = urlParams.getAll('username')
    var game_towait = urlParams.get('numplayer')
    var game_token = urlParams.get('token')
    //console.log(game_id)

    //console.log(document.getElementById('id_of_game'))

    document.getElementById('id_token').value = game_token.toString()
    document.getElementById('id_token').innerHTML = game_token.toString()

    construct_username_str = ""
    game_username.forEach(item => {
        construct_username_str += item.toString() + "<br> ?" + `<img src="../profile/${item.toString()}" />`

    })
    if (document.getElementById('id_waiting_players').value !== construct_username_str) {
        document.getElementById('id_waiting_players').value = construct_username_str
        document.getElementById('id_waiting_players').innerHTML = construct_username_str
    }


    document.getElementById('id_num_to_wait').value = game_towait.toString()
    document.getElementById('id_num_to_wait').innerHTML = game_towait.toString()


}

function loadGame() {
    let game_mode_ele = document.getElementById('id_game_mode')
    if (game_mode_ele.innerHTML == "") {

        const queryString = window.location.search
        const urlParams = new URLSearchParams(queryString)
        var game_mode = urlParams.get('mode')
        document.getElementById('id_game_mode').innerHTML = game_mode.toString()
    }

}

function loadErrorPage() {
    const queryString = window.location.search
    const urlParams = new URLSearchParams(queryString)
    var game_error = urlParams.get('error')
    console.log(game_error)

    document.getElementById('id_err_msg').innerHTML = game_error.toString()
}

function updateError(xhr) {
    var new_url = "redirect/?"
    //new_url += "&username="+items.username
    let response = JSON.parse(xhr.responseText)
    new_url += "error=" + response.error
    console.log("what is the error" + response.error)
    //new_url.searchParams.append('player',items.username)
    //new_url.searchParams.append('cap',items.cap)

    window.location.href = new_url

}

function reloadWait() {
    let token = $('#id_token').val()
    $.ajax({
        url: "bingo_plus/reload-game",
        dataType: "json",
        type: "POST",
        data: `token=${token}&csrfmiddlewaretoken=${getCSRFToken()}`,
        success: function (items) {
            //console.log("wtf???"+items.cap)

            var game_username = items.username
            var game_towait = items.cap - game_username.length
            var game_token = items.token
            //console.log(game_id)

            //console.log(document.getElementById('id_of_game'))

            document.getElementById('id_token').value = game_token.toString()
            document.getElementById('id_token').innerHTML = game_token.toString()

            construct_username_str = ""
            game_username.forEach(item => {
                construct_username_str += item.toString() + "<br>" + `<img src="../profile/${item.toString()}" alt="oauth login has no avatar yet" />` + "<br>"

            })
            if (document.getElementById('id_waiting_players').value !== construct_username_str) {
                document.getElementById('id_waiting_players').value = construct_username_str
                document.getElementById('id_waiting_players').innerHTML = construct_username_str
            }

            document.getElementById('id_num_to_wait').value = game_towait.toString()
            document.getElementById('id_num_to_wait').innerHTML = game_towait.toString()


        },

        error: updateError
    });
}

function joinGame() {
    let token = $('#token').val()
    $.ajax({
        url: "bingo_plus/join-game",
        dataType: "json",
        type: "POST",
        data: `token=${token}&csrfmiddlewaretoken=${getCSRFToken()}`,
        success: function (items) {
            //console.log("wtf???"+items.cap)


            var new_url = "wait/?"
            //new_url += "&username="+items.username
            let counter = 0
            let is_init = true

            items.username.forEach(item => {
                if (is_init) {
                    new_url += "username=" + item
                    is_init = false

                } else {
                    new_url += "&username=" + item

                }
                counter += 1
            }
            )

            new_url += "&numplayer=" + (items.cap - counter)
            new_url += "&token=" + items.token
            //new_url.searchParams.append('player',items.username)
            //new_url.searchParams.append('cap',items.cap)

            window.location.href = new_url


        },

        error: updateError
    });
}
function retrieveGame() {

    $.ajax({
        url: "bingo_plus/retrieve-game",
        dataType: "json",
        type: "POST",
        data: `csrfmiddlewaretoken=${getCSRFToken()}`,
        success: updateGame,
        error: updateError
    });
}

function updateBuyStatus(items) {
    if (items.msg != "No Error") {
        document.getElementById('error_msg_for_buying').innerHTML = items.msg
    } else {
        if (items.item == "1") {
            document.getElementById('id_item_1_count').innerHTML = items.count

        } else {
            document.getElementById('id_item_2_count').innerHTML = items.count
        }
        document.getElementById('user_account_balance').innerHTML = "$ " + items.balance
    }
}

function buyItem1() {
    let item_val = "1"
    $.ajax({
        url: "bingo_plus/buy-item",
        dataType: "json",
        type: "POST",
        data: `item=${item_val}&csrfmiddlewaretoken=${getCSRFToken()}`,
        success: updateBuyStatus,
        error: updateError
    });
}

function buyItem2() {
    let item_val = "2"
    $.ajax({
        url: "bingo_plus/buy-item",
        dataType: "json",
        type: "POST",
        data: `item=${item_val}&csrfmiddlewaretoken=${getCSRFToken()}`,
        success: updateBuyStatus,
        error: updateError
    });
}

function loadPreGame() {
    //console.log("hi")  
    let dim_val = $('#dim').find(":selected").val()
    let mode_val = $('#mode').find(":selected").val()
    let player_cap = $('#player').find(":selected").val()
    //window.location.href = "game"
    //window.location = "game"
    $.ajax({
        url: "bingo_plus/set-game",
        dataType: "json",
        type: "POST",
        data: `dim=${dim_val}&mode=${mode_val}&cap=${player_cap}&csrfmiddlewaretoken=${getCSRFToken()}`,
        success: function (items) {
            //console.log("wtf???"+items.cap)
            var new_url = "wait/?"
            new_url += "username=" + items.username
            new_url += "&numplayer=" + (items.cap - 1)
            new_url += "&token=" + items.token
            //new_url.searchParams.append('player',items.username)
            //new_url.searchParams.append('cap',items.cap)

            window.location.href = new_url


        },

        error: updateError
    });
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown";
}

function getNum() {
    //$("#bingo_card td").off()

    $.ajax({
        url: "bingo_plus/get-num",
        dataType: "json",
        type: "POST",
        data: `csrfmiddlewaretoken=${getCSRFToken()}`,
        success: updateGame,
        error: updateError
    });
    // connectToServer()
}




/*if (xhr.status === 0) {
    displayError("Cannot connect to server")
    return
}

if (!xhr.getResponseHeader('content-type') === 'application/json') {
    displayError("Received status=" + xhr.status)
    return
}

let response = JSON.parse(xhr.responseText)
if (response.hasOwnProperty('error')) {
    displayError(response.error)
    return
}

displayError(response)*/


function displayError(message) {
    $("#error").html(message);
}
function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}


function roomFilled() {

    let reload_str = "game/?"

    $.ajax({
        url: "bingo_plus/all-arrived",
        dataType: "json",
        type: "POST",
        data: `csrfmiddlewaretoken=${getCSRFToken()}`,
        success: function (items) {
            reload_str += "mode=" + items.mode
            window.location.href = reload_str

        },
        error: updateError
    });



}

function updateUseItem1(items) {
    if (items.failed != "F") {
        document.getElementById("id_item_status").innerHTML = "You don't have enough item 1 left!"

    } else {
        //document.getElementById("closest_num").innerHTML = items.closest_num
        document.getElementById("id_item_status").innerHTML = "Successfully Used Item 1! The closest num is " + items.closest_num
        document.getElementById("id_item_status").backgroundColor = "#FF9234"
        document.getElementById("id_user_item1").innerHTML = items.new_count
    }
}

function updateUseItem2(items) {
    if (items.failed != "F") {
        document.getElementById("id_item_status").innerHTML = items.failed

    } else if (items.player_name != "Self") {
        document.getElementById("id_item_status").innerHTML = "Successfully Used Item 2! User " + items.player_name + " Bingo Card Displayed"
        let interested_card = items.most_filled_card.split(" ")
        let state = items.most_filled_card_state.split(" ")
        //console.log(items.generated)

        let total_string = ``
        for (let i = 0; i < items.dim; i++) {
            let row_string = `<tr> `
            for (let j = 0; j < items.dim; j++) {
                let k = i * items.dim + j;

                let generated_val = interested_card[k]

                let cell_string = ` <td id=other_cell_${k}> ${generated_val} </td> `
                row_string += cell_string
            }
            row_string += ` </tr> `
            total_string += row_string
        }


        $("#item_bingo_card").html(total_string)

        for (let i = 0; i < items.dim * items.dim; i++) {



            if (state[i] == "T") {
                //console.log("yes")
                document.getElementById(`other_cell_${i}`).style.backgroundColor = "green"
            }
        }
        document.getElementById("id_user_item2").innerHTML = items.new_count

    } else {
        document.getElementById("id_item_status").innerHTML = "Successfully Used Item 2! You are the person with most filled"

        document.getElementById("id_user_item2").innerHTML = items.new_count

    }


    //document.getElementById("closest_num").innerHTML = items.closest_num


}


function useItem1() {

    $.ajax({
        url: "bingo_plus/use-item-1",
        dataType: "json",
        type: "POST",
        data: `csrfmiddlewaretoken=${getCSRFToken()}`,
        success: updateUseItem1,
        error: updateError
    });
}

function useItem2() {

    $.ajax({
        url: "bingo_plus/use-item-2",
        dataType: "json",
        type: "POST",
        data: `csrfmiddlewaretoken=${getCSRFToken()}`,
        success: updateUseItem2,
        error: updateError
    });
}



function updateGame(items) {
    if (curr_mutation) {
        console.log("the previous mutation is already deleted. What?")
        curr_mutation.disconnect()

    }
    //handleWinInfo() // for other users, get notification that someone won

    card = items.card.split(" ")
    state = items.state.split(" ")
    console.log("what is the original state str " + items.state)
    console.log("what is the state " + state)
    let target_index = -1;

    let existence_missing = false
    for (let i = 0; i < items.dim * items.dim; i++) {
        let if_exist = document.getElementById(`cell_${i}`)
        //if some element is missing due to malicious user action, rebuild the grid with correct values
        if (if_exist == null) {
            existence_missing = true
            break
        }
        //fix the value if user maliciously changes value
        if (parseInt(if_exist.innerHTML) != parseInt(card[i])) {
            console.log("happened")
            document.getElementById(`cell_${i}`).innerHTML = card[i]
        }


    }
    if (existence_missing) {
        let total_string = ``
        for (let i = 0; i < items.dim; i++) {
            let row_string = `<tr> `
            for (let j = 0; j < items.dim; j++) {
                let k = i * items.dim + j;

                let generated_val = card[k]

                let cell_string = ` <td id=cell_${k}> ${generated_val} </td> `
                row_string += cell_string
            }
            row_string += ` </tr> `
            total_string += row_string
        }
        $("#bingo_card").html(total_string)


    }
    $("#bingo_card td").off()

    $("#bingo_card td").on("click", function () {
        console.log($(this))
        if ($(this).css('background-color') === $('#dummy1').css('background-color')) {

            $(this).css('background-color', "#F0E68C")
        } else if ($(this).css('background-color') === $('#dummy2').css('background-color')) {
            $(this).css('background-color', "green")
            // }else if ($(this).css('background-color') === $('#dummy3').css('background-color')){
            //     $(this).css('background-color',"#32CD32")
            // }else if ($(this).css('background-color') === $('#dummy4').css('background-color')){
            //     $(this).css('background-color',"green")
        } else {
            console.log("cant change green")

        }
    })

    for (let i = 0; i < items.dim * items.dim; i++) {
        let if_exist = document.getElementById(`cell_${i}`)
        if (parseInt(if_exist.innerHTML) === parseInt(items.rand)) {
            target_index = i
            console.log("got new target index" + target_index)
        }
    }
    //target_index = parseInt(items.randint)

    // no longer color the cell automatically
    // check if the card is colored correctly according to the previous state
    if (items.refresh == "false") {
        for (let i = 0; i < items.dim * items.dim; i++) {
            // if (oldstate[i] === "T"){
            //     //console.log("yes")
            //     document.getElementById(`cell_${i}`).style.backgroundColor = "green"
            // }
            if (state[i] === "F" || $(`#cell_${i}`).css('background-color') !== $('#dummy5').css('background-color')) {
                // clean wrong colors
                $(`#cell_${i}`).css('background-color', "transparent")
            }
        }
    } else {
        for (let i = 0; i < items.dim * items.dim; i++) {
            // if (oldstate[i] === "T"){
            //     //console.log("yes")
            //     document.getElementById(`cell_${i}`).style.backgroundColor = "green"
            // }
            if (state[i] === "T") {
                // clean wrong colors
                $(`#cell_${i}`).css('background-color', "green")
            } else {
                $(`#cell_${i}`).css('background-color', "transparent")
            }
            //document.getElementById(`cell_${i}`).innerHTML = items.generated[i]
        }
    }


    // let exist_match = false
    // for (let i = 0; i < items.dim; i++) {
    //     let all_matched = true
    //     let row_idx = i * items.dim;
    //     for (let j = 0; j < items.dim; j++) {
    //         let curridx = row_idx + j;
    //         if (state[curridx] != "T"){
    //             all_matched = false
    //
    //         }
    //     }
    //
    // }


    document.getElementById('id_user_item1').innerHTML = items.item_count_1
    document.getElementById('id_user_item2').innerHTML = items.item_count_2
    //console.log("finish 2nd loop")


    if ((items.exist_match == "T") && (items.others_won_before == "F")) {
        document.getElementById('bingo_num').innerHTML = "You Win!"
    } else if ((items.exist_match == "T") && (items.others_won_before == "T")) {
        document.getElementById('bingo_num').innerHTML = "You got a match, but  " + items.name_of_winner + " won already..."
    } else if ((items.exist_match == "F") && (items.others_won_before == "T")) {
        document.getElementById('bingo_num').innerHTML = items.name_of_winner + " won already..."
    }

    else {
        document.getElementById('bingo_num').innerHTML = "Currently Display: " + items.rand;
    }
    if (target_index === -1) {
        return
    }

    console.log("targIndex" + target_index)
    if (target_index === -1) {
        return
    }

    // Create a MutationObserver instance
    const cellToMonitor = document.getElementById(`cell_${target_index}`);
    console.log(cellToMonitor)

    observer = new MutationObserver(mutations => {

        mutations.forEach(mutation => {
            // Check if the background color of the cell changed to yellow
            if (mutation.target.style.backgroundColor === 'green') {


                $.ajax({
                    url: "bingo_plus/clicked-green",
                    dataType: "json",
                    type: "POST",
                    data: `csrfmiddlewaretoken=${getCSRFToken()}`,
                    success: updateGame,
                    error: updateError
                });
            }
        })
    })
    observer.observe(cellToMonitor, { attributes: true, attributeFilter: ['style'] });
    curr_mutation = observer

    //console.log("finished")
}

function myFunction() {
    alert('Cell color changed to yellow!');
}

function exchangeNum() {
    let id_val = $("#id_of_game").val()
    let id_userid = $("#id_userid").val()
    let dim = $("#dim").html()
    let mode = $("#mode").html()
    let pre_nums = $("#previous_seen_num").val()
    const nums_arr = pre_nums.split(" ")
    let requested_num = parseInt(nums_arr[0])


    // check if user has this number already or not
    // save the curridx
    // save the value to be replaced

    if (mode == "Dumb") {
        console.log("Not valid for Dumb mode")
        return
    }

    console.log("requested " + requested_num)

    dim = parseInt(dim)

    // only look for that column 
    let group = Math.trunc(requested_num / (dim * 3))

    console.log("group " + group)

    let pre_index = -1

    for (let i = 0; i < dim; i++) {
        let inx = i * dim + group
        let val = parseInt(document.getElementById(`cell_${inx}`).value)
        console.log("checking " + val)


        if (val == requested_num) {
            // there is such number already
            console.log('You got the number already.')
            return
        }
        if (val > requested_num) {
            break
        }

        if (document.getElementById(`cell_${inx}`).style.backgroundColor != "green") {
            pre_index = inx
        }

    }

    if (pre_index == -1) {
        console.log("This col is full")
        return
    }

    const index_for_exchange = pre_index
    const val_for_exchange = parseInt(document.getElementById(`cell_${index_for_exchange}`).value)


    console.log("index" + index_for_exchange)
    console.log("val" + val_for_exchange)

    $.ajax({
        url: "bingo_plus/exchange-card",
        dataType: "json",
        type: "POST",
        data: `num=${requested_num}&index=${index_for_exchange}&val=${val_for_exchange}&userid=${id_userid}&gameid=${id_val}&token=${token}&csrfmiddlewaretoken=${getCSRFToken()}`,
        success: function (items) {
            var ifSuccess = items.success  // other users may not have the card
            var exchanger = items.exchanger
            console.log('exchange ' + ifSuccess)

        },

        error: updateError
    });
}
function gameLoop() {
    //console.log("anything")
    if ((document.getElementById('bingo_num').innerHTML != "You Win!") &&
        !(document.getElementById('bingo_num').innerHTML.includes("won already..."))) {

        getNum()



        /*if (document.getElementById('bingo_num').innerHTML == "You Win!"){
            sendWinInfo()
        }
        receiveWinInfo()*/

    }
}
// let intervalId = window.setInterval(gameLoop, 5000);
function onloadAction() {

    var mode = document.getElementById("id_game_mode").innerHTML;
    var zone = document.getElementById("bidding_display_button");
    zone.style.display = "none";
    if (mode === "Fun") {
        zone.style.display = "block";
    }
    /*
    if (mode === "Dumb") {
        zone.style.display = block;
        //document.getElementById("bidding_display_button").innerHTML = "ssss"
        document.getElementById("bidding_display_button").style.display = "none";
        document.getElementById("bidding_display_button").style.display = "none";

    } else if (mode.innerHTML === "Fun") {
        zone.style.display = "none";
    }
    */

    console.log("onload")
    connectToServer()

    retrieveGame()
}
function connectToServer() {
    console.log("connecting to server", "ws://" + window.location.host + "/auction/data/" + window.location.search)
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
            case "control":
                handleControl(metaResp.body)
                break
            case "error":
                displayWSError(metaResp.body)
                break
            case "display_balance":
                displayBalance(metaResp.body)
                break
            default:
                displayMessage("Unknown response" + metaResp.type)
        }
    }
}

function clearError() {
    document.getElementById("error").innerHTML = ""
}

function displayBalance(response) {
    document.getElementById("balance").innerHTML = "Balance: " + response
}

function displayWSError(message) {
    let errorElement = document.getElementById("error")
    errorElement.innerHTML = sanitize(message)
}

function displayMessage(message) {
    let msgElement = document.getElementById("message")
    msgElement.innerHTML = sanitize(message)
}

function displayRecord(response) {
    console.log(response)
    document.getElementById("curr-price").innerHTML = "Current Price: " + response.bid_price
    document.getElementById("highest-bidder").innerHTML = "Highest Bidder: " + sanitize(response.buyer)
    document.getElementById("curr-item").innerHTML = "Current Item: " + response.item
    document.getElementById("curr-seller").innerHTML = "Current Seller: " + sanitize(response.seller)
}

function displayTimer(response) {
    document.getElementById("countdown").innerHTML = "Countdown: " + response + "s"
}

function newBid() {
    let bid = document.getElementById("open-price").value
    let data = {
        "bid_price": bid,
        "action": "new",
        "item": document.getElementById('bingo_num').innerHTML
    }
    clearError()
    socket.send(JSON.stringify(data))
    // window.clearInterval(intervalId)  // stop the game loop at earliest time
}

function handleControl(response) {
    if (response.action === "end") {
        document.getElementById("bid-button").disabled = true
        displayWSError(response.message)
        // @todo: notify game loop to continue
        intervalId = window.setInterval(gameLoop, 5000)
        setTimeout(function () {
            document.getElementById("bid-button").disabled = false
            document.getElementById("exchange_button").disabled = false
        }, 1000)
    }
    else if (response.action === "start") {
        document.getElementById("exchange_button").disabled = true
        window.clearInterval(intervalId)
    }
    else if (response.action === "accept") {
        document.getElementById("bid-button").disabled = true
    }
    else if (response.action === "reject") {
        intervalId = window.setInterval(gameLoop, 5000)
        displayWSError(response.message)
    }
    // @todo: turn back on at next iteration
}

function sendBid() {
    let bid = document.getElementById("bid-price").value
    let data = {
        "bid_price": bid,
        "action": "bid",
    }
    clearError()
    socket.send(JSON.stringify(data))
}

function sanitize(s) {
    if (s == null) {
        return ""
    }
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
}