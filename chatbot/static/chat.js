let chatContainer = document.getElementById("chat-container");
let userInput = document.getElementById("user-input");
let loaderContainer = document.getElementById("loader-container");
let quickReplies = [];
let generatingResponseFlag = false;
let db_ids = [];

function updateButtonVisibility() {
    let stopBtn = document.getElementById("stopBtn");
    let positiveBtn = document.getElementById("positiveBtn");
    let negativeBtn = document.getElementById("negativeBtn");

    if (generatingResponseFlag) {
        // stopBtn.classList.remove("hidden");
        positiveBtn.classList.add("hidden");
        negativeBtn.classList.add("hidden");
    } else {
        // stopBtn.classList.add("hidden");
        positiveBtn.classList.remove("hidden");
        negativeBtn.classList.remove("hidden");
    }
}
function toggleResponseGeneration() {
    generatingResponseFlag = !generatingResponseFlag;
    updateButtonVisibility();
}
function renderQuickReplies() {
    let quickRepliesContainer = document.createElement(
        "div"
    );
    quickRepliesContainer.className = "quick-replies";
    for (const element of quickReplies) {
        let quickReplyButton = document.createElement("button");
        quickReplyButton.innerText = element;
        quickReplyButton.addEventListener("click", function () {
            // Handle quick reply click event
            sendMessage(this.innerText);
        });

        quickRepliesContainer.appendChild(quickReplyButton);
    }
    return quickRepliesContainer;
}

async function getBotResponse(message) {
    // Bot response logic here
    let formdata = new FormData();
    formdata.append("msg", message);

    let requestOptions = {
        method: 'POST',
        body: formdata,
        redirect: 'follow'
    };

    let response = await fetch("./get", requestOptions);
    try {
        const res = JSON.parse(await response.text());
        console.log(/* In the code snippet provided, `res` is a variable that stores the response
        received from the server after making a POST request to the "/get" endpoint. It
        is expected to contain the bot's response to the user's message. */
        res)
        db_ids = res["db_ids"]
        return res["res"];
    } catch (error) {
        console.log(error);
        return [""];
      }
}

function sendMessage(userMessage) {
    if (!userMessage) {
        return;
    }
    toggleResponseGeneration();
    let userBubble = document.createElement("div");
    userBubble.className = "user-bubble";
    userBubble.innerHTML = "<strong>You:</strong> " + userMessage;
    chatContainer.appendChild(userBubble);

    userInput.disabled = true;
    loaderContainer.style.display = "flex";

    // Simulating bot response delay with setTimeout
    setTimeout(function () {
        if (!generatingResponseFlag) {
            userInput.disabled = false;
            loaderContainer.style.display = "none";
            return;
        }
        getBotResponse(userMessage).then(function (response) {
            console.log(response);
            let botBubble = document.createElement("div");
            botBubble.className = "bot-bubble";
            let botMessage;
            let quickRepliesContainer;
            if (response.length > 1) {
                quickReplies = response;
                botMessage = "<p>Bitte wählen Sie eine Frage aus:</p>";
                quickRepliesContainer = renderQuickReplies();
                console.log(quickRepliesContainer);
            } else {
                botMessage = response[0];
            }
            botBubble.innerHTML = "<strong>Bot:</strong> " + botMessage;
            if (quickRepliesContainer) {
                botBubble.appendChild(quickRepliesContainer);
            }
            chatContainer.appendChild(botBubble);

            userInput.disabled = false;
            loaderContainer.style.display = "none";
            userInput.value = "";
            chatContainer.scrollTop = chatContainer.scrollHeight;
            toggleResponseGeneration();

        });

    }, 2000); // Simulating 2 seconds delay for bot response
}

userInput.addEventListener("keydown", function (event) {
    if (event.keyCode === 13 && userInput.value) {
        let userMessage = userInput.value;
        sendMessage(userMessage);
    }
});

function giveFeedback(feedback) {
    // Logic to handle feedback
    if (feedback === "positive") {
        // Handle positive feedback
        alert("Vielen Dank für Ihr positives Feedback!");
    } else if (feedback === "negative") {
        // Handle negative feedback
        alert("Es tut mir leid, das zu hören. Ich werde daran arbeiten, Ihre Erfahrung zu verbessern.");
    }
    // Bot response logic here
    let formdata = new FormData();
    formdata.append("feedback", feedback);
    formdata.append("db_id", db_ids);

    let requestOptions = {
        method: 'POST',
        body: formdata,
        redirect: 'follow'
    };
    let response = fetch("./giveFeedBack", requestOptions)
    console.log(response)
}