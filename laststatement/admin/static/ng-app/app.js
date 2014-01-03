'use strict';

/* App Module */

var lastAdmin = angular.module('lastAdmin', [
  'ngRoute',
  'lastAdminControllers',
  'lastAdminServices',
  'lastAdminDirectives',
  'lastAdminFilters'
]);

lastAdmin.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/dashboard', {
        templateUrl: 'static/ng-app/templates/dashboard.html',
        controller: 'DashCtrl'
      }).
      when('/terms', {
        templateUrl: 'static/ng-app/templates/terms.html',
        controller: 'TermCtrl'
      }).
      otherwise({
        redirectTo: '/dashboard'
      });
  }]);