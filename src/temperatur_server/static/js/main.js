import { TempGauge } from "./temp_gauge.js";
import { TempPlot } from "./temp_plot.js";

let temp_gauge_1 = new TempGauge("Temp_1", "Ofentemperatur");
temp_gauge_1.value = 0.0;

let temp_gauge_2 = new TempGauge("Temp_2", "Kerntemperatur");
temp_gauge_2.value = 0.0;

let temp_plot = new TempPlot("Plot");

ovenRefChange();
coreRefChange();

// Start here
let socket = io.connect();

socket.on('new_temp_data', (temp_data) => {
    temp_gauge_1.value = temp_data[0][1];
    temp_gauge_2.value = temp_data[1][1];
    temp_plot.add_data(temp_data);
    renderAll();
});
window.setInterval(function () { socket.emit("timer"); updateElapsedTime(); }, 1000);

let ofen_ref = document.getElementById("OvenRef");
ofen_ref.addEventListener("change", ovenRefChange);

let core_ref = document.getElementById("CoreRef");
core_ref.addEventListener("change", coreRefChange);

window.addEventListener("load", setStartTimeNow);

let start_time_button = document.getElementById("StartTimeButton");
start_time_button.addEventListener("click", setStartTimeNow);
let start_time = new Date();


function ovenRefChange(event) {
    let ofen_ref = document.getElementById("OvenRef");
    const new_ref_value = parseFloat(ofen_ref.value);
    temp_plot.reference_1 = new_ref_value;
    temp_gauge_1.margin = [new_ref_value - 10.0, new_ref_value - 5.0, new_ref_value + 5.0, new_ref_value + 10.0];
    temp_gauge_1.reference = new_ref_value;
    renderAll();
}

function coreRefChange(event) {
    let core_ref = document.getElementById("CoreRef");
    const new_ref_value = parseFloat(core_ref.value);
    temp_plot.reference_2 = new_ref_value;
    temp_gauge_2.reference = new_ref_value;
    temp_gauge_2.margin = [0.0, 0.0, new_ref_value - 3.0, new_ref_value + 1.0];
    renderAll();
}

function renderAll(){
    temp_gauge_1.render();
    temp_gauge_2.render();
    temp_plot.render();
}

function setStartTimeNow(event){
    let now = new Date();
    start_time = now;
    temp_plot.start_time = now;
    let now_local = new Date(now);
    now_local.setMinutes(now.getMinutes() - now_local.getTimezoneOffset());
  
    now_local.setMilliseconds(null)
    now_local.setSeconds(null)
  
    document.getElementById('StartTime').value = now_local.toISOString().slice(0, -1);
    updateElapsedTime();
    renderAll();
    
  };

function updateElapsedTime(){
    let now = new Date();
    let time_diff = new Date(now.getTime() - start_time.getTime())
    document.getElementById("ElapsedTime").innerHTML = time_diff.toISOString().slice(11, -5);
}
