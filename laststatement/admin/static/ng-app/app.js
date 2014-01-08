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
        templateUrl: 'static/ng-app/templates/dashboard.html',
        controller: 'DashCtrl'
      }).
      when('/offenders', {
        templateUrl: 'static/ng-app/templates/offenders.html',
        controller: 'OffenderCtrl'
      }).
      otherwise({
        redirectTo: '/dashboard'
      });
  }]);