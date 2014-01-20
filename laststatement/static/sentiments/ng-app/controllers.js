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
        $scope.statement_count = data.statement_count;
        $scope.sentiments = data.sentiments;
        $scope.sentiments = [];
        $scope.selected = [];
        $scope.executionPool = [];
        $scope.executionPoolCount = 0;

        for(var i = 0; i < data.sentiments.length; i++){
          if(data.sentiments[i].active === true){
            $scope.sentiments.push(data.sentiments[i]);
          }
        }
      },
      function(data){
        console.log('Unable to query executions');
      });

    $scope.select = function(id){
      // Add sentiment id to list of sentiments
      // Update list of executions appearing in all selected sentiments
      var index = $scope.selected.indexOf(id),
          execs = [],
          counts = [],
          execution_arr = [];

      $scope.executionPool = [];

      if(index == -1){
        $scope.selected.push(id);
      }else{
        $scope.selected.splice(index, 1);
      }

      for(var i = 0; i < $scope.sentiments.length; i++){
        if($scope.selected.indexOf($scope.sentiments[i].id) > -1){
          execs = execs.concat($scope.sentiments[i].executions);
        }
      }

      for(var i = 0; i < execs.length; i++) {
        var num = execs[i];
        counts[num] = counts[num] ? counts[num]+1 : 1;
        if(counts[num] == $scope.selected.length){
          execution_arr.push(num);
        }
      }

      for(var i = 0; i < $scope.executions.length; i++){
        if(execution_arr.indexOf($scope.executions[i].id) > -1){
          $scope.executionPool.push($scope.executions[i]);
        }
      }

      $scope.executionPoolCount = execution_arr.length;
    }
  }]);