'use strict';

/* Controllers */

var sentimentAppControllers = angular.module('sentimentAppControllers', []);

var GridCtrl = sentimentAppControllers.controller('GridCtrl', ['$scope', 'Execution', 'Sentiment', '$http',
  function($scope, Execution, Sentiment, $http) {
    Execution.query({},
      function(data){
        $scope.executions = data.executions
      },
      function(data){
        console.log('Unable to query executions');
      });
    $scope.orderProp = 'execution_num';

    Sentiment.query({},
      function(data){
        $scope.statement_count = data.statement_count; // data.count
        $scope.sentiments = data.sentiments
      },
      function(data){
        console.log('Unable to query executions');
      });
  }]);