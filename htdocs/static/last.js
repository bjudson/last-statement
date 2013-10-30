$(document).ready(function(){
    $('#info-btn').on('click', function(event){
        var btn = $('#info-btn');

        if(btn.hasClass('info-btn-selected')){
            btn.removeClass('info-btn-selected');
        }else{
            btn.addClass('info-btn-selected');
        }

        $('#more-info').slideToggle('fast');

        $('html, body').animate({
            scrollTop: btn.offset().top + 500
        }, 1000);

        return false;
    });

    if($('.term-chart')){
        var termView = location.hash.replace('#',''),
            url = "/terms/data/" + termView,
            termChart,
            yearChart = false,
            x,
            y,
            s;

        d3.json(url, function (data) {
            if(data['success'] == 'false'){
                $('.main-h1').text('The term does not exist');
            }else{
                var termCount = data['terms'].length,
                    termSvg = dimple.newSvg('.term-chart', '100%', termCount * 35);

                // Basic chart setup
                termChart = new dimple.chart(termSvg, data['terms']);
                if(termView != '') termChart.viewing = termView;
                termChart.noFormats = true;
                termChart.setMargins("100px", "20px", "40px", "70px");

                // Create axes
                x = termChart.addMeasureAxis("x", "count");
                y = termChart.addCategoryAxis("y", "term");
                y.addOrderRule("count");

                // Add series & setup events
                s = termChart.addSeries(["count", "term"], dimple.plot.bar);
                s.addEventHandler("mouseover", onBarHover);
                s.addEventHandler("mouseleave", onBarLeave);
                s.addEventHandler("click", onBarClick);

                if(data['statements']){
                    printStatements(data['statements']);
                }else{
                    $('.statements').hide();
                }

                if(data['years']){
                    drawYearChart();
                }

                drawTermChart();
            }

            function drawYearChart() {
                if(!yearChart){
                    console.log(yearChart);
                    var yearSvg = dimple.newSvg('.year-chart', '100%', 300);
                    yearChart = new dimple.chart(yearSvg, data['years']);
                    yearChart.setMargins("30px", "20px", "20px", "70px");
                    yearChart.addCategoryAxis('x', 'year');
                    yearChart.addMeasureAxis('y', 'percent');
                    yearChart.addSeries(null, dimple.plot.line);
                }

                $('.years').fadeIn(500);
                $('.years h1').text('Percent of statements referencing “' + termChart.viewing + '” by year');
                yearChart.draw();
            }

            function drawTermChart(noData) {
                var noData = noData || false

                $('.term-chart').fadeIn(500);
                termChart.draw(0, noData);
                y.titleShape.remove();
                y.shapes.selectAll('text')
                    .on('click', onLabelClick);
                y.shapes.selectAll('g').classed('yAxis', true);
                x.titleShape.text("Occurences");
                if(termChart.viewing){
                    $('#alongside-term').text(' alongside “' + termChart.viewing + '”');
                }
            }

            function printStatements(statements) {
                var out = '';
                $.each(statements, function(){
                    out += '<h2>' + $(this)[0]['date'] + ': ' + $(this)[0]['name'] + '</h2>';
                    out += $(this)[0]['statement'];
                });
                $('.statement-list').html(out);
                $('.statements h1').text(statements.length + ' statements referencing “' + termChart.viewing + '”');
                $('.statements').fadeIn(500);
            }

            function getNewData(term) {
                var url = "/terms/data/" + term;
                d3.json(url, function (data) {
                    termChart.data = data['terms'];
                    termChart.viewing = term;
                    printStatements(data['statements']);
                    drawTermChart();
                    if (typeof popup != 'undefined') {
                        popup.remove();
                    }
                    if(data['years']){
                        yearChart.data = data['years'];
                        drawYearChart();
                    }
                });
            }

            function onLabelClick(e) {
                document.location.href = '/terms#' + e;
                getNewData(e);
            }

            function onBarClick(e) {
                document.location.href = '/terms#' + e.yValue;
                getNewData(e.yValue);
            }

            // Event to handle mouse enter
            function onBarHover(e) {
                // Get the properties of the selected shape
                var cWidth = parseFloat(e.selectedShape.attr("width")),
                    cHeight = parseFloat(e.selectedShape.attr("height")),
                    cx = parseFloat(e.selectedShape.attr("x")),
                    cy = parseFloat(e.selectedShape.attr("y"));

                // Set the size and position of the popup
                var x = cx + cWidth + 5,
                    y = cy + Math.round(cHeight / 2) + 5;
                // Create a group for the popup objects
                popup = termSvg.append("g");

                // Add multiple lines of text
                popup.append('text')
                    .style("color", "#fff")
                    .attr('x', x)
                    .attr('y', y)
                    .append('tspan')
                    .attr('x', x)
                    .attr('y', y)
                    .text(e.seriesValue[0])
                    .style("font-size", ".8em");
            }

            // Event to handle mouse exit
            function onBarLeave(e) {
                // Remove the popup
                if (popup !== null) {
                    popup.remove();
                }
            };

            // Add a method to draw the chart on resize of the window
            window.onresize = function () {
                // As of 1.1.0 the second parameter here allows you to draw
                // without reprocessing data.  This saves a lot on performance
                // when you know the data won't have changed.
                drawTermChart(true);
            };
        });
    }
});