export class TempGauge {
    constructor(id = "", title = "Kerntemperatur", min = 20.0, max = 130.0) {
        this.id = id;
        this.layout = {
            margin: { t: 0, r: 30, l: 30, b: 0 },
            paper_bgcolor: "black",
            font: { color: "white", family: "Arial" }
        };

        this.data = [
            {
                type: "indicator",
                mode: "gauge+number+delta",
                value: 28.1,
                title: { text: title, font: { size: 24 } },
                number: { suffix: "°C" },
                delta: { reference: 25.0, font: { color: "white" } },
                gauge: {
                    bgcolor: "black",
                    borderwidth: 2,
                    bordercolor: "white",
                    axis: { range: [min, max], tickwidth: 1, tickcolor: "white" },
                    bar: { color: "blue", line: { width: 1, color: "white" } },
                    steps: [
                        { range: [min, 10.0], color: "red" },
                        { range: [10.0, 20.0], color: "yellow" },
                        { range: [20.0, 30.0], color: "green" },
                        { range: [30.0, 40.0], color: "yellow" },
                        { range: [40.0, max], color: "red" },
                    ],
                    threshold: {
                        line: { color: "gray", width: 4 },
                        thickness: 0.75,
                        value: 25.0
                    }
                }
            }
        ];
    }

    render() {
        Plotly.newPlot(this.id, this.data, this.layout);
    };

    /**
     * @param {float} val
     */
    set value(val) {
        this.data[0]["value"] = val;
    };

    set reference(ref) {
        this.data[0]["delta"]["reference"] = ref;
        this.data[0]["gauge"]["threshold"]["value"] = ref;
    };

    set margin(margin) {
        const [min, min_warn, max_warn, max] = margin;
        this.data[0]["gauge"]["steps"][0]["range"][1] = min;
        this.data[0]["gauge"]["steps"][1]["range"][0] = min;
        this.data[0]["gauge"]["steps"][1]["range"][1] = min_warn;
        this.data[0]["gauge"]["steps"][2]["range"][0] = min_warn;
        this.data[0]["gauge"]["steps"][2]["range"][1] = max_warn;
        this.data[0]["gauge"]["steps"][3]["range"][0] = max_warn;
        this.data[0]["gauge"]["steps"][3]["range"][1] = max;
        this.data[0]["gauge"]["steps"][4]["range"][0] = max;
    };

    set max(max) {
        this.data[0]["gauge"]["axis"]["range"][1] = max;
        this.data[0]["gauge"]["steps"][4]["range"][1] = max;
    };
}
