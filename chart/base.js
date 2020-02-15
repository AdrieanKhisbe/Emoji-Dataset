$(document).ready(function () {
  console.log("ready!");

  var url = "https://raw.githubusercontent.com/AtomicSpider/Emoji-Dataset/master/dataset/highchart_data.json";

  $.getJSON(url, function (data) {
    console.log(data[0]);
    data = data.slice(0, 1000);
    Highcharts.chart('container', {
      title: {
        text: 'Contextual grouping of Emojis'
      },
      yAxis: {
        title: {
          text: ''
        }
      },
      xAxis: {
        title: {
          text: ''
        }
      },
      chart: {
        type: 'scatter',
        zoomType: 'xy',
        panning: true,
        panKey: 'shift'
      },
      plotOptions: {
        series: {
          marker: {
            enabled: true
          }
        }
      },
      series: [{
        data: data
      }]
    });
  });
});