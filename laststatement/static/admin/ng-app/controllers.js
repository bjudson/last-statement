'use strict';

/* Controllers */

var lastAdminControllers = angular.module('lastAdminControllers', []);

lastAdminControllers.controller('DashCtrl', ['$scope', 'Term', 'Sentiment', '$http',
    function($scope, Term, Sentiment, $http) {
        Term.query({},
            function(data){
                $scope.terms = data.terms
            },
            function(data){
                console.log('Unable to query terms');
            });

        Sentiment.query({},
            function(data){
                $scope.sentiments = data.sentiments
            },
            function(data){
                console.log('Unable to query sentiments');
            });

        $scope.orderProp = 'title';

        function getModel(name, id){
            var models = {
                'Term': {
                    'service': Term,
                    'scope': $scope.terms,
                    'pk': {termId: id}
                },
                'Sentiment': {
                    'service': Sentiment,
                    'scope': $scope.sentiments,
                    'pk': {sentimentId: id}
                }
            };

            return models[name];
        }

        $scope.createTerm = function(){
            if($scope.newTermTitle != ''){
                Term.save({
                    title: $scope.newTermTitle,
                    words: $scope.newTermTitle,
                    chart: false
                },
                function(data){
                    $scope.terms.push(data.term);
                },
                function(data){
                    console.log('Unable to create term');
                });
            }
        };

        $scope.createSentiment = function(){
            if($scope.newSentimentTitle != ''){
                Sentiment.save({
                    title: $scope.newSentimentTitle
                },
                function(data){
                    $scope.sentiments.push(data.sentiment);
                },
                function(data){
                    console.log('Unable to create sentiment');
                });
            }
        };

        $scope.delete = function(model, id){
            var m = getModel(model, id);

            if(confirm('Are you sure you want to delete this forever?')){
                m.service.delete(m.pk,
                    function(data){
                        for(var i = 0; i < m.scope.length; i++){
                            if(m.scope[i].id == data.id){
                                m.scope.splice(i, 1);
                                break;
                            }
                        }
                    },
                    function(data){ console.log('failure') });
            }
        };

        $scope.update = function(model, id, fld, val){
            var newValue = {},
                m = getModel(model, id);

            newValue[fld] = val;

            if(fld === 'chart'){
                if(val == true){
                    newValue[fld] = 'false';
                }else{
                    newValue[fld] = 'true';
                }
            }

            m.service.update(m.pk, newValue,
                function(data){
                    for(var i = 0; i < m.scope.length; i++){
                        if(m.scope[i].id == data.id){
                            m.scope[i][fld] = data[fld];
                            break;
                        }
                    }
                },
                function(data){ console.log('failure') });
        };
    }]);

lastAdminControllers.controller('ExecutionCtrl', ['$scope', 'Execution', 'Sentiment', '$http',
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
                $scope.sentiments = data.sentiments
            },
            function(data){
                console.log('Unable to query executions');
            });

        $scope.update = function(id, fld, val, add){
            var newValue = {};

            newValue[fld] = val;

            // add is used for sentiments. if true add to execution, if false remove
            if(typeof add !== 'undefined'){
               newValue['add'] = add;
            }

            Execution.update({executionId: id}, newValue,
                function(data){
                    for(var i = 0; i < $scope.executions.length; i++){
                        if($scope.executions[i].id == data.id){
                            $scope.executions[i][fld] = data[fld];
                            break;
                        }
                    }
                },
                function(data){ console.log('failure') });

        };
    }]);