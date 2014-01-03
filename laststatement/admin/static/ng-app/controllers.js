'use strict';

/* Controllers */

var lastAdminControllers = angular.module('lastAdminControllers', []);

lastAdminControllers.controller('DashCtrl', ['$scope', 'Term', '$http',
    function($scope, Term, $http) {
        Term.query({},
            function(data){
                $scope.terms = data.terms
            },
            function(data){
                console.log('Unable to query terms');
            });
        $scope.orderProp = 'title';

        $scope.update = function(id, fld, val){
            var newValue = {};
                newValue[fld] = val;

            if(fld === 'chart'){
                if(val == true){
                    newValue[fld] = 'false';
                }else{
                    newValue[fld] = 'true';
                }
            }

            Term.update({termId: id}, newValue,
                function(data){
                    for(var i = 0; i < $scope.terms.length; i++){
                        if($scope.terms[i].id == data.id){
                            $scope.terms[i][fld] = data[fld];
                            break;
                        }
                    }
                },
                function(data){ console.log('failure') });
        };
    }]);

lastAdminControllers.controller('TermCtrl', function($scope) {
    $scope.msg = 'Terms for everyone';
});