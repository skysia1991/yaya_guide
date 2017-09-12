/**
 * Created by gliao on 8/22/17.
 */

var app = angular.module('userGuide',[]);
app.controller('homeCtrl',['$scope', '$http', function($scope, $http) {
    $scope.problem_select = function($event) {
        var id = $event.target.id;
        switch(id) {
            case 'classification':
                $scope.problem_type = 1;
                break;
            case 'regression':
                $scope.problem_type = 2;
                break;
            case 'sort':
                $scope.problem_type =3;
                break;
            default:
                break
        }
    }
}]);

app.controller('targetCtrl', ['$scope', '$http', function($scope, $http) {
    var tableHeader = [],
        idIndex,
        targetIndex,
        preIdIndex,
        preTargetIndex;
    $('#data_preview_table thead th').each(function() {
        tableHeader.push($.trim($(this).text()));
    });
    tableHeader.shift();
    $scope.id = tableHeader[0];
    $scope.target = tableHeader[0];
    $scope.selectId = function() {
        idIndex = $.inArray($scope.id, tableHeader) + 1 ;
        if(preIdIndex) {
            $('#data_preview_table thead th:eq('+preIdIndex+')').removeClass('id_chosen');
            $('#data_preview_table tr td:nth-child('+(preIdIndex+1)+')').removeClass('id_chosen');
        }
        if (idIndex) {
            $('#data_preview_table thead th:eq('+idIndex+')').addClass('id_chosen');
            $('#data_preview_table tr td:nth-child('+(idIndex+1)+')').addClass('id_chosen');
        }
        preIdIndex = idIndex;
    };
    $scope.selectTarget = function() {
        targetIndex = $.inArray($scope.target, tableHeader) + 1;
        if(preTargetIndex) {
            $('#data_preview_table thead th:eq('+preTargetIndex+')').removeClass('target_chosen');
            $('#data_preview_table tr td:nth-child('+(preTargetIndex+1)+')').removeClass('target_chosen');
        }
        if (targetIndex) {
            $('#data_preview_table thead th:eq('+targetIndex+')').addClass('target_chosen');
            $('#data_preview_table tr td:nth-child('+(targetIndex+1)+')').addClass('target_chosen');
        }
        preTargetIndex = targetIndex;
    };
}]);