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
        throw new Error('Unable to query executions');
      });
    $scope.orderProp = 'execution_num';

    Sentiment.query({},
      function(data){
        $scope.statementCount = data.statement_count;
        $scope.sentiments = [];
        $scope.selectedSentiments = [];
        $scope.sentimentTitles = [];
        $scope.executionPool = [];
        $scope.executionPoolCount = 0;

        for(var i = 0; i < data.sentiments.length; i++){
          if(data.sentiments[i].active === true){
            data.sentiments[i].overlap = data.sentiments[i].executions.length;
            $scope.sentiments.push(data.sentiments[i]);
          }
        }
      },
      function(data){
        throw new Error('Unable to query sentiments');
      });

    $scope.showStatements = false;

    $scope.toggleStatements = function(){
      if($scope.showStatements){
        $('html, body').scrollTop(0);
        $scope.showStatements = false;
      }else{
        $('html, body').scrollTop(0);
        $scope.showStatements = true;
      }
    }

    $scope.select = function(id){
      // Add sentiment id to list of sentiments
      // Update list of executions appearing in all selected sentiments
      var index = $scope.selectedSentiments.indexOf(id),
          execs = [], // array of execution ids (includes duplicates)
          counts = [], // number of times execution id appears in execs
          execution_arr = []; // execution ids within all selected sentiments

      $scope.executionPool = [];
      $scope.sentimentTitles = [];

      if(index == -1){
        $scope.selectedSentiments.push(id);
      }else{
        $scope.selectedSentiments.splice(index, 1);
      }

      // Put all execution ids from selected sentiments into execs & put titles into sentimentTitles
      for(var i = 0; i < $scope.sentiments.length; i++){
        if($scope.selectedSentiments.indexOf($scope.sentiments[i].id) > -1){
          execs = execs.concat($scope.sentiments[i].executions);
          $scope.sentimentTitles.push($scope.sentiments[i].title)
        }
      }

      for(var i = 0; i < execs.length; i++) {
        var exec_id = execs[i];
        counts[exec_id] = counts[exec_id] ? counts[exec_id]+1 : 1;
        // Is this execution id in all selected sentiments?
        if(counts[exec_id] == $scope.selectedSentiments.length){
          execution_arr.push(exec_id);
        }
      }

      // Find overlap between selected & unselected sentiments
      for(var i = 0; i < $scope.sentiments.length; i++){
        var s = $scope.sentiments[i],
            overlap = s.executions.length;

        if($scope.selectedSentiments.length > 0){
          if($scope.selectedSentiments.indexOf(s.id) < 0){
            overlap = 0;

            for(var n = 0; n < s.executions.length; n++){
              if(execution_arr.indexOf(s.executions[n]) > -1){
                overlap++;
              }
            }
          }else{
            overlap = execution_arr.length;
          }          
        }

        $scope.sentiments[i].overlap = overlap;
      }

      for(var i = 0; i < $scope.executions.length; i++){
        if(execution_arr.indexOf($scope.executions[i].id) > -1){
          $scope.executionPool.push($scope.executions[i]);
        }
      }

      $scope.executionPoolCount = execution_arr.length;
    }
  }]);