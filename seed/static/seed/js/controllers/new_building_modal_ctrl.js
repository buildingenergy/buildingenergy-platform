/**
 * :copyright: (c) 2014 Building Energy Inc
 * :license: see LICENSE for more details.
 */
angular.module('BE.seed.controller.new_building_modal', [])
.controller('new_building_modal_ctrl', [
  '$scope',
  '$modalInstance',
  'building_services',
  '$location',
  '$timeout',
  function (
    $scope,
    $modalInstance,
    building_services,
    $location,
    $timeout
    ) {
    $scope.building = {};


    /**
     * creates a building then changes the browser location to the new building
     * page
     */
    $scope.submit_form = function () {
        building_services.create_building($scope.building).then(function (data) { 
            $modalInstance.close();
            $location.path('/buildings/' + data.building.canonical_building);
        });
    };
    /**
     * cancel: dismissed the modal, routes to the dismiss function of the parent
     *  scope
     */
    $scope.cancel = function () {
        $modalInstance.dismiss('cancel');
    };

    /**
     * set the focus on the first input box
     */
    $timeout(function() {
        angular.element('#building_name').focus();
    }, 50);
}]);
