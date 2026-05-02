(function () {
    const canvas = document.getElementById('myChart1');
    const labelsElement = document.getElementById('chart-labels');
    const valuesElement = document.getElementById('chart-values');
    if (!canvas || !labelsElement || !valuesElement || typeof Chart === 'undefined') {
        return;
    }

    const labels = JSON.parse(labelsElement.textContent);
    const values = JSON.parse(valuesElement.textContent);

    new Chart(canvas, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                fill: true,
                label: 'Weight',
                borderColor: 'rgb(102, 205, 0)',
                backgroundColor: 'rgba(102, 205, 0, 0.12)',
                data: values
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: 'My weight during all the time'
                },
                legend: {
                    display: false
                }
            }
        }
    });
})();
