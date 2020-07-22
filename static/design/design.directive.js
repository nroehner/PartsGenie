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
    		pagination: "="
    	},
        templateUrl: "/static/design/design.html",
        link: function(scope, element) {
        	scope.$watch(function() {
        		return scope.query().designs;
        	},               
        	function(designs) {
        		$timeout(setValidity(scope, designs));
        	}, true);
        	
        	setValidity = function(scope, designs) {
        		var valid = checkValidity(designs);
        		scope.$parent.form.$setValidity("valid", valid);
        	}
        	
        	checkValidity = function(designs) {
        		var valid = true;
        		
        		for(var i = 0; i < designs.length; i++) {
        			design = designs[i];
        			
        			for(var j = 0; j < design.features.length; j++) {
        				feature = design.features[j];
        				
        				// If RBS not followed by CDS:
        				if(feature.typ == "http://identifiers.org/so/SO:0000139") {
        					var is_cds_next = j != design.features.length - 1
    							&& design.features[j + 1].typ == "http://identifiers.org/so/SO:0000316";
        					
        					feature.temp_params.valid = is_cds_next;
        				}
        				
        				if(!feature.temp_params.valid) {
        					valid = false;
        				}
        			}
        		}
        		
        		return valid;
        	}
        }
    };
});