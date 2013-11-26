$(document).ready(function(){
    $('#info-btn').on('click', function(event){
        var btn = $('#info-btn');

        if(btn.hasClass('info-btn-selected')){
            btn.removeClass('info-btn-selected');
        }else{
            btn.addClass('info-btn-selected');
        }

        $('#more-info').slideToggle('fast');

        return false;
    });

    if($('.term-chart')){
        var termView = location.hash.replace('#',''),
            url = "/terms/data/" + termView,
            termChart,
            x,
            y,
            s;

        d3.json(url, function (data) {
            this.yearChart = false;
            this.monthChart = false;

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
                    drawTimeChart(data['years'], 'year');
                }

                if(data['months']){
                    drawTimeChart(data['months'], 'month');
                }

                drawTermChart();

                $('.term-chart-info').text('Click a term to drill down');
            }

            function drawTimeChart(timeData, type) {
                var chart = this[type + 'Chart'],
                    contClass = '.' + type + 's';

                if(!chart){
                    this[type + 'Svg'] = dimple.newSvg(contClass + ' .chart', '100%', 300);
                    chart = new dimple.chart(this[type + 'Svg'], timeData);
                    chart.setMargins("65px", "20px", "20px", "50px");
                    chart.timeX = chart.addCategoryAxis('x', type);
                    chart.timeY = chart.addMeasureAxis('y', 'percent');
                    chart.addSeries(null, dimple.plot.line);

                    if(type == 'month'){
                        chart.timeX.addOrderRule(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]);
                    }
                }else{
                    chart.data = timeData;
                }

                $(contClass).fadeIn(500);
                $(contClass + ' h1').text('Percent of statements referencing “' + termChart.viewing + '” by ' + type);
                chart.draw();
                chart.timeX.titleShape.remove();
                chart.timeY.titleShape.remove();
                this[type + 'Chart'] = chart;
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
                        drawTimeChart(data['years'], 'year');
                    }
                    if(data['months']){
                        drawTimeChart(data['months'], 'month');
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
                drawTermChart(true);
            };
        });
    }
});