'use strict';

/* Directives */

var sentimentAppDirectives = angular.module('sentimentAppDirectives', []);

sentimentAppDirectives.directive('lsPieChart', ['$compile', 'd3', function($compile, d3){
    return {
        scope: {
            title: '=lsPieChart',
            values: '=lsPieValues',
            total: '=lsPieTotal',
            select: '&lsPieSelect'
        },
        link: function($scope, elem, attr, ctrl) {
            var tau = 2 * Math.PI, // http://tauday.com/tau-manifesto
                percent = $scope.values / $scope.total,
                svg = d3.select(elem[0])
                    .append('svg')
                    .attr('viewBox', "0 0 200 200")
                    .append("g")
                    .attr("transform", "translate(" + 100 + "," + 90 + ")");

            var arc = d3.svg.arc()
                .innerRadius(40)
                .outerRadius(70)
                .startAngle(0);

            var background = svg.append("path")
                .datum({endAngle: tau})
                .style("fill", "#ddd")
                .attr("d", arc);

            var foreground = svg.append("path")
                .datum({endAngle: percent * tau})
                .attr("d", arc)
                .classed('percent-path', true);

            svg.selectAll('.sentiment-title')
                .data([$scope])
                .enter()
                .append('text')
                .attr('class', 'sentiment-title')
                .attr('y', 95)
                .attr('x', 0)
                .attr('text-anchor', 'middle')
                .text(function(d){ return d.title; });

            svg.selectAll('.count-text')
                .data([$scope])
                .enter()
                .append('text')
                .attr('class', 'count-text')
                .attr('y', 8)
                .attr('text-anchor', 'middle')
                .text(function(d){ return d.values; });
        }
    }
}]);

sentimentAppDirectives.directive('lsBarCounter', ['$compile', 'd3', function($compile, d3){
    return {
        scope: {
            value: '=lsBarValue',
            total: '=lsBarTotal',
            select: '&lsBarSelect'
        },
        link: function($scope, elem, attr, ctrl) {
            var percent = $scope.value / $scope.total,
                height = 30,
                width = $(elem[0]).width(),
                svg = d3.select(elem[0])
                    .append('svg')
                    .append('g');

                svg.append('rect')
                    .attr('height', height)
                    .attr('width', width)
                    .attr('fill', '#efefde');

                svg.selectAll('.bar')
                    .data([$scope])
                    .enter()
                    .append('rect')
                    .classed('bar', true)
                    .attr('y', 0)
                    .attr('x', 0)
                    .attr('height', height)
                    .attr('width', function(d){ return 1 + (parseInt(d.value) / parseInt(d.total) * width); });

                svg.selectAll('.count')
                    .data([$scope])
                    .enter()
                    .append('text')
                    .classed('count', true)
                    .attr('y', 20)
                    .attr('x', function(d){ return (parseInt(d.value) / parseInt(d.total) * width) + 5; })
                    .attr('fill', '#666')
                    .attr('font-size', '12pt')
                    .text(function(d){ return d.value; });

                svg.selectAll('.empty-text')
                    .data([$scope])
                    .enter()
                    .append('text')
                    .classed('empty-text', true)
                    .attr('y', 20)
                    .attr('x', 170)
                    .attr('fill', '#aaa')
                    .attr('font-size', '12pt')
                    .text('Please select sentiments');

            $scope.$watch('value', function (newVal, oldVal) {
                var bar,
                    count;

                if(newVal > 0){
                    svg.selectAll('.empty-text')
                        .data([])
                        .exit()
                        .remove();
                }

                svg.selectAll('.bar')
                    .data([$scope])
                    .transition()
                    .duration(500)
                    .attr('width', function(d){ return 1 + (parseInt(d.value) / parseInt(d.total) * width); });

                svg.selectAll('.count')
                    .data([$scope])
                    .transition()
                    .duration(500)
                    .attr('x', function(d){ return (parseInt(d.value) / parseInt(d.total) * width) + 5; })
                    .text(function(d){ return d.value; });

            });
        }
    }
}]);
