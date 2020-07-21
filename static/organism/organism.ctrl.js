organismApp.controller("organismCtrl", ["OrganismService", function(OrganismService) {
	var self = this;
	self.url = null;
	self.parent_id = "2";

	self.getItem = function(terms) {
		terms["parent_id"] = self.parent_id;
		return OrganismService.getItem(self.url, terms);
	};
}]);