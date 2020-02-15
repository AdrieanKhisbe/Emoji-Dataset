$(document).ready(function () {
  console.log("ready!");

  var url = "https://raw.githubusercontent.com/AtomicSpider/Emoji-Dataset/master/dataset/highchart_data.json";

  $.getJSON(url, function (data) {
    console.log(data[0]);
    data1 = data.slice(0, 1000);
    data2 = data.slice(1000, 1600);
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
        name: '0-1000',
        data: data1
      },
      {
        name: '1000:1600',
        data: data2
      }]
    });
  });
});