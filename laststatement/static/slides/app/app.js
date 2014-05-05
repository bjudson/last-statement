$(document).ready(function(){
  var colorScale = d3.scale.linear()
    .domain([1,365])
    .interpolate(d3.interpolateRgb)
    .range(["#222222", "#ffffff", "#222222"])

  var months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

  var newSlide = function(cont, text, date) {
    cont.fadeOut({
      duration: 500,
      complete: function(){
        $('.excerpt').html(text);
        $('.date').html(date);
        cont.fadeIn(500);
      }
    });
  }

  var textDate = function(date){
    var months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
        date_parts = date.split('-');

    return months[parseInt(date_parts[1]) - 1] + ' ' + parseInt(date_parts[2]) + ', ' + date_parts[0];
  }

  $('#page').load('../static/slides/app/templates/slides.html');

  $.get( "/api/1/executions/all?order=day_of_year", function( data ) {
    var i = 1,
        cont = $('.slides'),
        timer,
        data = data,
        date;

    $('.excerpt').html(data.executions[0].teaser);
    $('.date').html(textDate(data.executions[i].execution_date));
    cont.fadeIn(500);

    timer = setInterval(function(){
      if(i < data.executions.length){
        newSlide(cont, data.executions[i].teaser, textDate(data.executions[i].execution_date));
        $('body').css({'background': colorScale(data.executions[i].execution_day)})
        i++;
      }else{
        clearInterval(timer);
      }

    }, 10000);
  });
});