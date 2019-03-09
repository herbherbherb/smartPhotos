var app = angular.module('mp3',['ngRoute', 'AppServices', 'chart.js']).run(function($rootScope) {
    $rootScope.stepsModel = [];
    $rootScope.login_name = "";
});

/**
 * Route logic that controls between pages and controllers
 */
app.config(function ($routeProvider) {
    $routeProvider
        .when('/gallery/', {
            templateUrl: 'partials/gallery.html',
            controller: 'gal_ctr'
        })
        .when('/list/', {
            templateUrl: 'partials/list.html',
            controller: 'list_ctr'
        })
        .when('/detail/:username', {
            templateUrl: 'partials/details.html',
            controller: 'detail_ctr'
        })
        .when('/login/', {
            templateUrl: 'partials/login.html',
            controller: 'login_ctr'
        })
        .when('/register/', {
            templateUrl: 'partials/register.html',
            controller: 'register_ctr'
        })
        .when('/share/', {
            templateUrl: 'partials/share.html',
            controller: 'share_ctr'
        })
        .when('/summary/', {
            templateUrl: 'partials/summary.html',
            controller: 'summary_ctr'
        })
        .otherwise({
            redirectTo: '/login/'
        });
});

app.filter('listfilter',[ function () {
    return function(items, searchText) {
        var filtered = [];
        if (searchText === ""){return items}
        angular.forEach(items, function(item) {
            if( item.title.indexOf(searchText) >= 0 ) filtered.push(item);
        });
        return filtered;
    };
}]);
