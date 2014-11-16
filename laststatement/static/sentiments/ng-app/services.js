'use strict';

/* Services */

var sentimentAppServices = angular.module('sentimentAppServices', ['ngResource'])

  .factory('Execution', ['$resource',
    function($resource){
      return $resource('/api/1/executions/:executionId', {}, {
        query: {method:'GET', params: {executionId: 'all'}}
      });
    }])

  .factory('Sentiment', ['$resource',
    function($resource){
      return $resource('/api/1/sentiments/:sentimentId', {}, {
        query: {method:'GET', params: {sentimentId: 'all'}}
      });
    }])

  .factory('d3Service', ['$document', '$q', '$rootScope',
    function($document, $q, $rootScope) {
      var d = $q.defer();
      
      function onScriptLoad() {
        $rootScope.$apply(function() { d.resolve(window.d3); });
      }

      var scriptTag = $document[0].createElement('script');
      scriptTag.type = 'text/javascript'; 
      scriptTag.async = true;
      scriptTag.src = '//cdnjs.cloudflare.com/ajax/libs/d3/3.4.13/d3.min.js';
      scriptTag.onreadystatechange = function () {
        if (this.readyState == 'complete') onScriptLoad();
      }
      scriptTag.onload = onScriptLoad;

      var s = $document[0].getElementsByTagName('body')[0];
      s.appendChild(scriptTag);

      return {
        d3: function() { return d.promise; }
      };
  }]);