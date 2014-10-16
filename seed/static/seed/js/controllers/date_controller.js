angular.module('BE.seed.controller.date', [])
.controller('date_controller', ['$scope', function($scope){
    $scope.open = function($event) {
        console.log({key: $event});
        $event.preventDefault();
        $event.stopPropagation();

        $scope.opened = true;
        $scope.dateOptions = {
            formatYear: 'yy',
            startingDay: 1
        };
      };
}]);