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
            var τ = 2 * Math.PI, // http://tauday.com/tau-manifesto
                percent = $scope.values / $scope.total,
                svg = d3.select(elem[0])
                    .append('svg')
                    .style('width', 200)
                    .style('height', 200)
                    .append("g")
                    .attr("transform", "translate(" + 100 + "," + 90 + ")");

            var arc = d3.svg.arc()
                .innerRadius(40)
                .outerRadius(70)
                .startAngle(0);

            var background = svg.append("path")
                .datum({endAngle: τ})
                .style("fill", "#ddd")
                .attr("d", arc);

            var foreground = svg.append("path")
                .datum({endAngle: percent * τ})
                .style("fill", "orange")
                .attr("d", arc);

            svg.selectAll('.sentiment-title')
                .data([$scope])
                .enter()
                .append('text')
                .attr('class', 'sentiment-title')
                .attr('y', 95)
                .attr('x', 0)
                .attr('text-anchor', 'middle')
                .attr('font-size', '10pt')
                .attr('fill', '#666')
                .text(function(d){ return d.title; });

            svg.selectAll('.percent-text')
                .data([$scope])
                .enter()
                .append('text')
                .attr('class', 'sentiment-title')
                .attr('y', 8)
                .attr('text-anchor', 'middle')
                .attr('font-size', '16pt')
                .attr('fill', '#ccc')
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
                height = 23,
                width = $(elem[0]).width(),
                svg = d3.select(elem[0])
                    .append('svg')
                    .style('width', '100%')
                    .style('height', height)
                    .append("g");

            $scope.$watch('value', function (newVal, oldVal) {
                if(svg.selectAll('.bar')){
                    svg.selectAll('rect').data([]).exit().remove();
                    svg.selectAll('text').data([]).exit().remove();
                }

                svg.selectAll('.bar')
                    .data([$scope])
                    .enter()
                    .append('rect')
                    .attr('y', 0)
                    .attr('x', 0)
                    .attr('fill', '#666')
                    .attr('height', height)
                    .attr('width', function(d){ return 1 + (d.value / d.total * width); });

                svg.selectAll('.count')
                    .data([$scope])
                    .enter()
                    .append('text')
                    .attr('y', 17)
                    .attr('x', function(d){ return (d.value / d.total * width) + 5; })
                    .attr('fill', '#666')
                    .attr('font-size', '12pt')
                    .text(function(d){ return d.value; });
            });
        }
    }
}]);
