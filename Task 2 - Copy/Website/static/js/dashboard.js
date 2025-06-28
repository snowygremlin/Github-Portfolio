// Prepare data for the line graph
const traceGenerated = {
    x: labels, // Time-based labels (hourly or daily)
    y: generatedEnergy, // Energy generated data
    name: 'Generated Energy',
    type: 'scatter', // Line chart
    mode: 'lines+markers', // Lines with markers
    line: {
        color: 'rgba(75, 192, 192, 1)', // Solid blue for generated energy
        width: 3,
    },
    marker: {
        size: 8,
        color: 'rgba(75, 192, 192, 0.8)',
    },
};

const traceUsed = {
    x: labels, // Time-based labels (hourly or daily)
    y: usedEnergy, // Energy used data
    name: 'Used Energy',
    type: 'scatter', // Line chart
    mode: 'lines+markers', // Lines with markers
    line: {
        color: 'rgba(255, 99, 132, 1)', // Solid red for used energy
        width: 3,
    },
    marker: {
        size: 8,
        color: 'rgba(255, 99, 132, 0.8)',
    },
};

// Combine traces into a single dataset
const data = [traceGenerated, traceUsed];

// Configure graph layout for responsiveness
const layout = {
    title: {
        text: 'Energy Usage and Generation Over Time',
        font: {
            family: 'Arial, sans-serif',
            size: 24,
        },
    },
    xaxis: {
        title: {
            text: labels.length === 24 ? 'Hour' : 'Date', // Adjust title based on timeframe
            font: {
                family: 'Arial, sans-serif',
                size: 18,
            },
        },
        tickangle: -45, // Rotate labels for better readability
    },
    yaxis: {
        title: {
            text: 'Energy (kWh)',
            font: {
                family: 'Arial, sans-serif',
                size: 18,
            },
        },
    },
    legend: {
        orientation: 'h', // Horizontal legend
        x: 0.5,
        xanchor: 'center',
    },
    margin: {
        t: 50, // Top margin
        l: 50, // Left margin
        r: 50, // Right margin
        b: 100, // Bottom margin
    },
    autosize: true,
    responsive: true,
};

// Render the graph in the `energyChart` div
Plotly.newPlot('energyChart', data, layout, { responsive: true });
