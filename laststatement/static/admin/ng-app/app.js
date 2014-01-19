'use strict';

/* App Module */

var lastAdmin = angular.module('lastAdmin', [
  'ngRoute',
  'ngSanitize',
  'lastAdminControllers',
  'lastAdminServices',
  'lastAdminDirectives',
  'lastAdminFilters'
]);

lastAdmin.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/dashboard', {
        templateUrl: '../static/admin/ng-app/templates/dashboard.html',
        controller: 'DashCtrl'
      }).
      when('/executions', {
        templateUrl: '../static/admin/ng-app/templates/executions.html',
        controller: 'ExecutionCtrl'
      }).
      otherwise({
        redirectTo: '/dashboard'
      });
  }]);