console.log("Fraud Detection System Loaded");

/* Simple Welcome Alert */

function welcomeMessage(){
    alert("Welcome to Fraud Detection System");
}

/* Fraud Amount Warning */

function checkAmount(){

    let amount = document.getElementById("amount").value;

    if(amount > 50000){
        alert("Warning: High Amount Transaction!");
    }
}