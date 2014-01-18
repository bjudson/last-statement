'use strict';

/* Directives */

var lastAdminDirectives = angular.module('lastAdminDirectives', []);

lastAdminDirectives.directive('lsInput', function($compile){
    return {
        scope: {
            item: '=lsInput',
            field: '=lsFld',
            update: '&lsEnter'
        },
        template: '<input ng-model="item" class="term-text-fld">',
        link: function($scope, elem, attr, ctrl) {
            $scope.oldVal = $scope.item;

            elem.bind("keydown keypress", function (event) {
                if(event.which === 13) { // enter key
                    $scope.oldVal = $scope.item;
                    $scope.$apply($scope.update());

                    event.target.blur();
                    event.preventDefault();
                }
                if(event.which === 27) { // escape key
                    $scope.item = $scope.oldVal;
                    $scope.$apply();
                    event.target.blur();
                    event.preventDefault();
                }
            });
        }
    }
});
