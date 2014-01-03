'use strict';

/* Services */

var lastAdminServices = angular.module('lastAdminServices', ['ngResource']);

lastAdminServices.factory('Term', ['$resource',
  function($resource){
    return $resource('/api/1/terms/:termId', {}, {
      query: {method:'GET', params: {termId: 'all'}},
      save: {method:'POST'},
      update: {method:'PUT'}
    });
  }]);
