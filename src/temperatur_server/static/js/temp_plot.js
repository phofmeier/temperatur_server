export class TempPlot {
    constructor(id = "Plot") {
        this.show_fit = false;
        this.show_pred = false;
        this.show_full_state = false;
        this.id = id;

        this.trace1 = {
            x: [],
            y: [],
            type: 'scatter',
            name: "Ofentemperatur",
        };


        this.trace2 = {
            x: [],
            y: [],
            type: 'scatter',
            name: "Kerntemperatur",
        };

        this.trace3 = {
            x: [],
            y: [],
            type: 'scatter',
            name: "Fit",
        };
        this.trace4 = {
            x: [],
            y: [],
            type: 'scatter',
            name: "Pred_Oven",
        };
        this.trace5 = {
            x: [],
            y: [],
            type: 'scatter',
            name: "Pred_meat",
        };
        this.full_state_traces_fit = [];
        this.full_state_traces_pred = [];

        this.fit_oven = {
            x: [],
            y: [],
            type: 'scatter',
            name: "fit_oven",
        };

        this.layout = {
            // width: 1500,
            // height: 400,
            //margin: { t: 25, r: 25, l: 25, b: 25 },
            margin: { t: 40, r: 25, l: 40, b: 40 },
            paper_bgcolor: "black",
            plot_bgcolor: "black",
            font: { color: "white", family: "Arial" },
            xaxis: {
                title: "Time",
                showgrid: true,
                gridcolor: 'darkgray',
                linecolor: 'white',
                tickcolor: 'white',
                tickfont: {
                    color: 'white'
                }
            },
            yaxis: {
                title: "Temperature [°C]",
                showgrid: true,
                gridcolor: 'darkgray',
                linecolor: 'white',
                tickcolor: 'white',
                tickfont: {
                    color: 'white'
                }
            },
            legend: {
                font: { size: 16 },
                x: 1,
                xanchor: 'right',
                y: 1,
                yanchor: 'bottom'
            },
            shapes: [{
                type: 'line',
                line: {
                    color: "lightblue",
                    width: 2,
                    dash: 'dash',
                },
                xref: 'paper',
                yref: 'y',
                x0: 0,
                x1: 1,
                y0: 52.0,
                y1: 52.0,
            },
            {
                type: 'line',
                line: {
                    color: "lightgreen",
                    width: 2,
                    dash: 'dash',
                },
                xref: 'paper',
                yref: 'y',
                x0: 0,
                x1: 1,
                y0: 62.0,
                y1: 62.0,
            },
            {
                type: 'line',
                line: {
                    color: "red",
                    width: 4,
                    // dash: 'dash',
                },
                xref: 'x',
                yref: 'paper',
                x0: 0,
                x1: 1,
                y0: 0,
                y1: 1,
            },],
            annotations: [
                {
                    x: 0,
                    y: 1,
                    yshift: 25,
                    xref: 'x',
                    yref: 'paper',
                    text: 'Start',
                    anchor: "bottom",
                    showarrow: false,
                    bgcolor: "red",
                    font: {
                        size: 16,
                        color: '#ffffff'
                    }
                },],
        };

    }

    render() {
        let traces = [this.trace1, this.trace2]
        if (this.show_fit) {
            traces.push(this.fit_oven);
            traces.push(this.trace3);
        }

        if (this.show_pred) {
            traces.push(this.trace4);
            traces.push(this.trace5);
        }

        if (this.show_full_state && this.show_fit) {
            traces = traces.concat(this.full_state_traces_fit);
        }

        if (this.show_full_state && this.show_pred) {
            traces = traces.concat(this.full_state_traces_pred);
        }


        Plotly.newPlot(this.id, traces, this.layout);
    }
    add_prediction(prediction_data) {
        this.trace3["x"] = [];
        this.trace3["y"] = [];
        this.trace4["x"] = [];
        this.trace4["y"] = [];
        this.trace5["x"] = [];
        this.trace5["y"] = [];
        this.fit_oven["x"] = [];
        this.fit_oven["y"] = [];


        let t_fit = prediction_data[0][0]
        let oven_fit = prediction_data[0][1]
        let meat_fit = prediction_data[0][2]
        let inner_index = prediction_data[0][2][0].length - 1


        for (let index = 0; index < t_fit.length; index++) {
            this.fit_oven["x"].push(new Date(t_fit[index] * 1e-6));
            this.fit_oven["y"].push(oven_fit[index]);
            this.trace3["x"].push(new Date(t_fit[index] * 1e-6));
            this.trace3["y"].push(meat_fit[index][inner_index]);
        }

        let t_pred = prediction_data[0][3];
        let oven_pred = prediction_data[0][4];
        let meat_pred = prediction_data[0][5];

        for (let index = 0; index < t_pred.length; index++) {
            this.trace4["x"].push(new Date(t_pred[index] * 1e-6));
            this.trace4["y"].push(oven_pred[index]);
            this.trace5["x"].push(new Date(t_pred[index] * 1e-6));
            this.trace5["y"].push(meat_pred[index][inner_index]);
        }

        if (this.show_full_state) {



            this.full_state_traces_pred = [];
            this.full_state_traces_fit = [];

            for (let state_index = 0; state_index < meat_fit[0].length; state_index++) {
                this.full_state_traces_fit.push({
                    x: [],
                    y: [],
                    type: 'scatter',
                    name: "Fit_full_" + state_index,
                    showlegend: false,
                })

            }
            for (let index = 0; index < t_fit.length; index++) {
                for (let state_index = 0; state_index < this.full_state_traces_fit.length; state_index++) {
                    this.full_state_traces_fit[state_index]["x"].push(new Date(t_fit[index] * 1e-6));
                    this.full_state_traces_fit[state_index]["y"].push(meat_fit[index][state_index]);
                }

            }

            for (let state_index = 0; state_index < meat_pred[0].length; state_index++) {
                this.full_state_traces_pred.push({
                    x: [],
                    y: [],
                    type: 'scatter',
                    name: "pred_full_" + state_index,
                    showlegend: false,
                })

            }

            for (let index = 0; index < t_pred.length; index++) {
                for (let state_index = 0; state_index < this.full_state_traces_pred.length; state_index++) {
                    this.full_state_traces_pred[state_index]["x"].push(new Date(t_pred[index] * 1e-6));
                    this.full_state_traces_pred[state_index]["y"].push(meat_pred[index][state_index]);
                }

            }
        }



    };
    add_data_series(data_series) {
        this.trace1["x"] = [];
        this.trace1["y"] = [];
        this.trace2["x"] = [];
        this.trace2["y"] = [];
        for (let index = 0; index < data_series[0].length; index++) {
            this.trace1["x"].push(new Date(data_series[0][index][0] * 1e-6));
            this.trace1["y"].push(data_series[0][index][1]);
            this.trace2["x"].push(new Date(data_series[1][index][0] * 1e-6));
            this.trace2["y"].push(data_series[1][index][1]);

        }
    }
    add_data(new_data) {
        this.trace1["x"].push(new Date(new_data[0][0] * 1e-6))
        this.trace1["y"].push(new_data[0][1])
        this.trace2["x"].push(new Date(new_data[1][0] * 1e-6))
        this.trace2["y"].push(new_data[1][1])
    }
    set reference_1(reference) {
        this.layout["shapes"][0]["y0"] = reference;
        this.layout["shapes"][0]["y1"] = reference;
    }

    set reference_2(reference) {
        this.layout["shapes"][1]["y0"] = reference;
        this.layout["shapes"][1]["y1"] = reference;
    }

    set start_time(start_time) {
        this.layout["shapes"][2]["x0"] = start_time;
        this.layout["shapes"][2]["x1"] = start_time;
        this.layout["annotations"][0]["x"] = start_time;
    }
}
