import { TempGauge } from "./temp_gauge.js";
import { TempPlot } from "./temp_plot.js";

let temp_gauge_1 = new TempGauge("Temp_1", "Ofentemperatur");
temp_gauge_1.value = 0.0;

let temp_gauge_2 = new TempGauge("Temp_2", "Kerntemperatur");
temp_gauge_2.value = 0.0;

let temp_plot = new TempPlot("Plot");
temp_plot.start_time = document.getElementById("StartTime").value;

// Start here
let socket = io.connect();
let start_time = new Date().valueOf() * 1e6;
let end_time = new Date().valueOf() * 1e6;

socket.emit("getTimeSeries", "end", receiveDataSeries);
socket.emit("getStartTime", "now", setStartTime);
socket.emit("getCoreRefTemp", "now", setCoreRefTemp);
socket.emit("getOvenRefTemp", "now", setOvenRefTemp);

socket.on("new_temp_data", (temp_data) => {
  temp_gauge_1.value = temp_data[0][1];
  temp_gauge_2.value = temp_data[1][1];
  temp_plot.add_data(temp_data);
  renderAll();
});
window.setInterval(function () {
  //socket.emit("timer");
  updateElapsedTime();
}, 1000);

let ofen_ref = document.getElementById("OvenRef");
ofen_ref.addEventListener("change", ovenRefChange);

let core_ref = document.getElementById("CoreRef");
core_ref.addEventListener("change", coreRefChange);

document
  .getElementById("StartTime")
  .addEventListener("change", startTimeChanged);

let start_time_button = document.getElementById("StartTimeButton");
start_time_button.addEventListener("click", setStartTimeNow);

let fullscreen_button = document.getElementById("FullscreenButton");
fullscreen_button.addEventListener("click", fullscreen_toggler);

let show_fit_checkbox = document.getElementById("CheckboxFit");
show_fit_checkbox.addEventListener("change", () => {
  if (show_fit_checkbox.checked) {
    temp_plot.show_fit = true;
  } else {
    temp_plot.show_fit = false;
  }
  renderAll();
});

let show_pred_checkbox = document.getElementById("CheckboxPred");
show_pred_checkbox.addEventListener("change", () => {
  if (show_pred_checkbox.checked) {
    temp_plot.show_pred = true;
  } else {
    temp_plot.show_pred = false;
  }
  renderAll();
});

let show_full_state_checkbox = document.getElementById("CheckboxFullState");
show_full_state_checkbox.addEventListener("change", () => {
  if (show_full_state_checkbox.checked) {
    temp_plot.show_full_state = true;
  } else {
    temp_plot.show_full_state = false;
  }
  renderAll();
});

socket.on("new_prediction", (pred_data) => {
  end_time = pred_data[0][6];
  let end_time_date = new Date(end_time * 1e-6);
  document.getElementById("EndTime").innerHTML = end_time_date.toLocaleString();
  temp_plot.add_prediction(pred_data);
  renderAll();
});

function fullscreen_toggler(event) {
  if (
    window.matchMedia("(display-mode: fullscreen)").matches ||
    document.fullscreenElement
  ) {
    exitFullscreen();
  } else {
    enterFullscreen(document.documentElement);
  }
}

function enterFullscreen(element) {
  if (element.requestFullscreen) {
    element.requestFullscreen();
  } else if (element.webkitRequestFullscreen) {
    // iOS Safari
    element.webkitRequestFullscreen();
  }
}

function exitFullscreen() {
  if (document.exitFullscreen) {
    document.exitFullscreen();
  } else if (document.webkitExitFullscreen) {
    document.webkitExitFullscreen();
  }
}

function receiveDataSeries(server_response) {
  let data = JSON.parse(server_response);
  temp_gauge_1.value = data[0].slice(-1)[0][1];
  temp_gauge_2.value = data[1].slice(-1)[0][1];
  temp_plot.add_data_series(data);
  renderAll();
}

function setOvenRefTemp(new_data) {
  let ofen_ref = document.getElementById("OvenRef");
  ofen_ref.value = parseFloat(new_data);
  temp_plot.reference_1 = new_data;
  temp_gauge_1.margin = [
    new_data - 10.0,
    new_data - 5.0,
    new_data + 5.0,
    new_data + 10.0,
  ];
  temp_gauge_1.reference = new_data;
  temp_gauge_1.max = new_data + 30.0;
  temp_gauge_2.max = new_data + 30.0;
  renderAll();
}

function ovenRefChange(event) {
  let ofen_ref = document.getElementById("OvenRef");
  const new_ref_value = parseFloat(ofen_ref.value);
  temp_plot.reference_1 = new_ref_value;
  temp_gauge_1.margin = [
    new_ref_value - 10.0,
    new_ref_value - 5.0,
    new_ref_value + 5.0,
    new_ref_value + 10.0,
  ];
  temp_gauge_1.reference = new_ref_value;
  temp_gauge_1.max = new_ref_value + 30.0;
  temp_gauge_2.max = new_ref_value + 30.0;
  socket.emit("newOvenRef", new_ref_value);
  renderAll();
}

function setCoreRefTemp(new_data) {
  let core_ref = document.getElementById("CoreRef");
  core_ref.value = parseFloat(new_data);
  temp_plot.reference_2 = new_data;
  temp_gauge_2.reference = new_data;
  temp_gauge_2.margin = [0.0, 0.0, new_data - 3.0, new_data + 1.0];
  socket.emit("newCoreRef", new_data);
  renderAll();
}

function coreRefChange(event) {
  let core_ref = document.getElementById("CoreRef");
  const new_ref_value = parseFloat(core_ref.value);
  temp_plot.reference_2 = new_ref_value;
  temp_gauge_2.reference = new_ref_value;
  temp_gauge_2.margin = [0.0, 0.0, new_ref_value - 3.0, new_ref_value + 1.0];
  socket.emit("newCoreRef", new_ref_value);
  renderAll();
}

function renderAll() {
  temp_gauge_1.render();
  temp_gauge_2.render();
  temp_plot.render();
}

function startTimeChanged(event) {
  let new_start_time = new Date(document.getElementById("StartTime").value);
  start_time = new_start_time.valueOf() * 1e6;
  temp_plot.start_time = new Date(start_time * 1e-6);
  socket.emit("newStartTime", start_time);
  updateElapsedTime();
  renderAll();
}

function setStartTime(start_time_server) {
  start_time = start_time_server;
  let now = new Date(start_time * 1e-6);
  temp_plot.start_time = now;
  let new_start_time = new Date(start_time * 1e-6);
  new_start_time.setMinutes(
    now.getMinutes() - new_start_time.getTimezoneOffset(),
  );

  new_start_time.setMilliseconds(null);
  new_start_time.setSeconds(null);

  document.getElementById("StartTime").value = new_start_time
    .toISOString()
    .slice(0, -1);
  updateElapsedTime();
  renderAll();
}

function setStartTimeNow(event) {
  let now = new Date();
  start_time = now.valueOf() * 1e6;
  temp_plot.start_time = now;
  let now_local = new Date(now);
  now_local.setMinutes(now.getMinutes() - now_local.getTimezoneOffset());

  now_local.setMilliseconds(null);
  now_local.setSeconds(null);

  document.getElementById("StartTime").value = now_local
    .toISOString()
    .slice(0, -1);
  updateElapsedTime();
  socket.emit("newStartTime", now.valueOf() * 1e6);
  renderAll();
}

function updateElapsedTime() {
  let now = new Date();
  let time_diff = new Date(now.getTime() - new Date(start_time * 1e-6));
  document.getElementById("ElapsedTime").innerHTML = time_diff
    .toISOString()
    .slice(11, -5);
  let remaining_time = new Date(new Date(end_time * 1e-6) - now.getTime());
  document.getElementById("RemainingTime").innerHTML = remaining_time
    .toISOString()
    .slice(11, -5);
}
