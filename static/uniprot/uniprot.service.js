uniprotApp.factory("UniprotService", ["$uibModal", function($uibModal) {
	var obj = {};
	
	obj.updateFeature = function(feature, selected) {
		feature.name = selected["Entry name"];
		feature.temp_params.aa_seq = selected.Sequence;
		feature.temp_params.orig_seq = selected.Sequence;
		feature.temp_params.valid = true;
		
		if(selected.hasOwnProperty("Protein names") && selected.hasOwnProperty("Organism")) {
			feature.desc = selected["Protein names"].join(", ") + " (" + selected["Organism"] + ")";
		}
		
		if(selected.hasOwnProperty("Entry")) {
			feature.links = [
		        "http://identifiers.org/uniprot/" + selected["Entry"]
		    ]
		}

		if(selected.hasOwnProperty("EC number")) {
	    	ecNumbers = selected["EC number"].split("; ");
	    	
	    	for(var i = 0; i < ecNumbers.length; i++) {
	    		feature.links.push("http://identifiers.org/ec-code/" + ecNumbers[i]);
	    	}
	    }
	}
	
	obj.open = function(options, feature) {
		var modalInstance = $uibModal.open({
			animation: true,
			ariaLabelledBy: "modal-title",
			ariaDescribedBy: "modal-body",
			templateUrl: "/static/uniprot/uniprot.html",
			controller: "uniprotCtrl",
			controllerAs: "uniprotCtrl",
			backdrop: "static",
			keyboard: false,
			size: "lg",
			resolve: {
				options: function() {
					return options;
				},
				feature: function() {
					return feature;
				}
			}
		});

		modalInstance.result.then(function(selected) {
			obj.updateFeature(feature, selected);
		});
	};
	
	return obj;
}]);