organismApp.controller("organismCtrl", ["OrganismService", function(OrganismService) {
	var self = this;
	self.url = null;
	
	self.parentId = OrganismService.parentId;
	
	self.getItem = function(terms) {
		terms["parent_id"] = OrganismService.getParentId();
		return OrganismService.getItem(self.url, terms);
	};
}]);