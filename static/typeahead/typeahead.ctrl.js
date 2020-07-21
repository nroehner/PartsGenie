typeaheadApp.controller("typeaheadCtrl", ["TypeaheadService", function(TypeaheadService) {
	var self = this;
	self.url = null;
	self.parent_id = "2";

	self.getItem = function(terms) {
		terms["parent_id"] = self.parent_id;
		return TypeaheadService.getItem(self.url, terms);
	};
}]);