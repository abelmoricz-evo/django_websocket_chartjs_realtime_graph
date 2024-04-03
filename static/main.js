const ctx = document.getElementById('myChart');

let graphData = {
    type: 'line',
    data: { labels: [],
            datasets: [{
                label: 'liters of base added per hour', data: [], fill: true,
                backgroundColor: ['rgba(73, 198, 230, 0.5)',], borderWidth: 2
            }]
    },
    options:{}
};

var myChart = new Chart(ctx, graphData);




var socket = new WebSocket('ws://localhost:8000/ws/graph/')

socket.onmessage = function (e) {

    var djangoData = JSON.parse(e.data);


    var newGraphData = graphData.data.datasets[0].data;    
    newGraphData.push(djangoData.value);
    graphData.data.datasets[0].data = newGraphData;

    var newLabels = graphData.data.labels;    
    newLabels.push(djangoData.index);
    graphData.data.labels = newLabels;



    myChart.update();
}