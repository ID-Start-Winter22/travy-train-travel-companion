
var chatWindow = document.getElementsByClassName("css-qpwdbp")[0];


// add header bar to chat widget
var headerContainer = document.createElement("div")
headerContainer.classList.add("header-container")
chatWindow.appendChild(headerContainer)


// create overlay for mobile
var mobileOverlay = document.createElement("div");
mobileOverlay.classList.add("mobile-overlay");

var body = document.body;

// hide header bar when chat widget is closed via button
var chatButton = document.getElementsByClassName("css-1c58232")[0];

chatButton.onclick = function() {
    if (chatWindow.offsetHeight > 0) {
        headerContainer.style.display = "none";
        body.style.overflowY = "scroll";
        body.removeChild(mobileOverlay);
    }
    else {
        headerContainer.style.display = "inline";
        body.appendChild(mobileOverlay);
        body.style.overflowY = "hidden";
    }
};


// hide header bar when chat widget is closed via click outside
document.addEventListener("mousedown", function(event) {
    var clickedOutside = !document.getElementsByClassName("css-1kgb40s")[0].contains(event.target);
    if (clickedOutside) {
        headerContainer.style.display = "none";
        body.style.overflowY = "scroll";
        body.removeChild(mobileOverlay);
    }
});

// add logo to header bar
var logoImage = document.createElement("img");
logoImage.src = "./images/logo.svg";
logoImage.classList.add("logo-image")
headerContainer.appendChild(logoImage)

// add title to header bar
var chatbotTitle = document.createElement("h1");
chatbotTitle.innerText = "Train Travel Companion";
chatbotTitle.classList.add("chatbot-title");
headerContainer.appendChild(chatbotTitle);

// add server status text to header bar
var statusText = document.createElement("p");
statusText.innerText = "offline";
statusText.classList.add("status-text");
headerContainer.appendChild(statusText);

// add server status indicator to header bar
var statusInidcator = document.createElement("div");
statusInidcator.classList.add("status-indicator");
headerContainer.appendChild(statusInidcator);

// add sleepy logo image indicating offline
var emptyChatWindow = document.getElementsByClassName("css-1c77470")[0];
var sleepyLogoImage = document.createElement("img");
sleepyLogoImage.src = "./images/sleepy_logo.svg";
sleepyLogoImage.classList.add("sleepy-logo-image");
emptyChatWindow.appendChild(sleepyLogoImage);


// checks if rasa server and rasa action server are running and updates UI if so
function checkStatus() {

    // stop this interval function if both servers are online
    if (document.getElementsByClassName("status-text")[0].innerText === "online" && 
    document.getElementById("s2-text").innerText === "online") {
        clearInterval(checkStatusInterval);
    }

    // handle rasa server status
    fetch("http://localhost:5005", { mode: "no-cors" })
    .then(response => {
        // set rasa server status text in header bar to online and update color of indicator
        var statusText = document.getElementsByClassName("status-text")[0];
        var statusInidcator = document.getElementsByClassName("status-indicator")[0];
        statusText.innerText = "online";
        statusInidcator.style.backgroundColor = "#10de7d";

        // set rasa server status in status-box to online and update color of indicator
        statusText = document.getElementById("s1-text");
        statusInidcator = document.getElementById("s1-indicator");
        statusText.innerText = "online";
        statusInidcator.style.backgroundColor = "#10de7d";
        
        // remove sleepy logo image
        emptyChatWindow.removeChild(sleepyLogoImage);

        console.log("rasa server online");
    })
    .catch(error => {
        console.log("rasa server offline");
    });

    // handle rasa action server status
    fetch("http://localhost:5055/actions", { mode: "no-cors" })
    .then(response => {
        // set rasa action server status in status-box to online and update color of indicator
        var statusText = document.getElementById("s2-text");
        var statusInidcator = document.getElementById("s2-indicator");
        statusText.innerText = "online";
        statusInidcator.style.backgroundColor = "#10de7d";

        console.log("rasa action server online");
    })
    .catch(error => {
        console.log("rasa action server offline");
    });
}

// run status check function first time
checkStatus();

// run status check function in intervall
var checkStatusInterval = setInterval(checkStatus, 5000);

// add shadow to chat widget (it has no css class therefore handled in js)
var chatWidgetChildren = document.getElementsByClassName("css-1kgb40s")[0].childNodes;
chatWidgetChildren[0].style.boxShadow = "0 10px 25px -15px rgb(148 148 148)";