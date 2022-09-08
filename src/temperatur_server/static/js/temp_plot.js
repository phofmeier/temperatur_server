export class TempPlot {
    constructor(id = "Plot") {
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

        this.layout = {
            // width: 1500,
            // height: 400,
            //margin: { t: 25, r: 25, l: 25, b: 25 },
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
                y: 0
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
        Plotly.newPlot(this.id, [this.trace1, this.trace2], this.layout);
    }
    add_data_series(data_series){
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