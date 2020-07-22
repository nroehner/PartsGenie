designApp.directive("designPanel", function($timeout) {
    return {
    	scope: {
    		templates: "=",
    		query: "&",
    		selected: "&",
    		toggleSelected: "&",
    		addDesign: "&",
    		copyDesign: "&",
    		removeDesign: "&",
    		addFeature: "&",
    		copyFeature: "&",
    		bulkUniprot: "&",
    		valid: "&",
    		pagination: "="
    	},
        templateUrl: "/static/design/design.html",
        link: function(scope, element) {
        	scope.$watch(function() {
        		return scope.valid();
        	},               
        	function(valid) {
        		$timeout(scope.$parent.form.$setValidity("valid", valid));
        	}, true);
        }
    };
});