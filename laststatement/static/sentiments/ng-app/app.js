'use strict';

/* App Module */

var sentimentApp = angular.module('sentimentApp', [
  'ngRoute',
  'ngSanitize',
  'sentimentAppServices',
  'sentimentAppDirectives',
  'sentimentAppControllers'
]);

sentimentApp.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider.
      when('/', {
        templateUrl: '../static/sentiments/ng-app/templates/grid.html',
        controller: 'GridCtrl'
      }).
      otherwise({
        redirectTo: '/'
      });
  }]);