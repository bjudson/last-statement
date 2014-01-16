'use strict';

/* Services */

var lastAdminServices = angular.module('lastAdminServices', ['ngResource']);

lastAdminServices.factory('Execution', ['$resource',
  function($resource){
    return $resource('/api/1/executions/:executionId', {}, {
      query: {method:'GET', params: {executionId: 'all'}},
      save: {method:'POST'},
      update: {method:'PUT'}
    });
  }]);

lastAdminServices.factory('Term', ['$resource',
  function($resource){
    return $resource('/api/1/terms/:termId', {}, {
      query: {method:'GET', params: {termId: 'all'}},
      save: {method:'POST'},
      update: {method:'PUT'}
    });
  }]);

lastAdminServices.factory('Sentiment', ['$resource',
  function($resource){
    return $resource('/api/1/sentiments/:sentimentId', {}, {
      query: {method:'GET', params: {sentimentId: 'all'}},
      save: {method:'POST'},
      update: {method:'PUT'}
    });
  }]);