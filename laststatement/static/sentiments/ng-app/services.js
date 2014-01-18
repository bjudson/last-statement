'use strict';

/* Services */

var sentimentAppServices = angular.module('sentimentAppServices', ['ngResource'])

  .factory('Execution', ['$resource',
    function($resource){
      return $resource('/api/1/executions/:executionId', {}, {
        query: {method:'GET', params: {executionId: 'all'}}
      });
    }])

  .factory('Sentiment', ['$resource',
    function($resource){
      return $resource('/api/1/sentiments/:sentimentId', {}, {
        query: {method:'GET', params: {sentimentId: 'all'}}
      });
    }]);