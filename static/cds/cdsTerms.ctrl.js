cdsTermsApp.controller("cdsTermsCtrl", ["$uibModalInstance", function($uibModalInstance) {
	var self = this;
	
	self.cdsTerms = null;
	
	self.ok = function() {
		cdsTerms = self.cdsTerms.split(/,?\s+/);
		$uibModalInstance.close(cdsTerms);  
		$uibModalInstance.close();
	};
	
	self.cancel = function() {
		$uibModalInstance.close([]);
	};
}]);