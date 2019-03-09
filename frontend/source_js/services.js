var AppServices = angular.module('AppServices', []);
// http://localhost:5000/api/upload
/**
 * This is the service functions that controls all the $http calls to the backend.
 * For week 2, the application supports 4 http calls.
 */
AppServices.factory('Data', function($http) {
    // var base = "http://localhost:5000";
    var base = "http://35.225.82.230:5000";

    return {
        // For detail page, get image label
        getLabel : function (data) {
            return $http.get(base + '/api/label', {params: { name: data }});
        },
        // Update image label
        putLabel : function (old_name, new_name, username) {
            return $http.get(base + '/api/label_change', {params: { old_name: old_name,
                new_name: new_name, username: username}});
        },
        // For detail page, get a specific image
        getImage : function (data) {
            return $http.get(base + '/api/image', {params: { name: data }});
        },
        // Upload new image to server
        postImage: function(data){
            return $http.post(base + '/api/upload', data, {
                headers: {'Content-Type': undefined},
                transformRequest: angular.identity
            });
        },
        // For list page, retrieve stored images
        init_image : function (username) {
            return $http.get(base + '/api/init_image', {params: { username: username}});
        },
        // Register a new user account
        register : function (username, password) {
            return $http.get(base + '/api/register', {params: { username: username, password: password }});
        },
        // Validate user account info to login
        login : function (username, password) {
            return $http.get(base + '/api/login', {params: { username: username, password: password }});
        },
        share_image : function (login_name, share_name, image_name) {
            return $http.get(base + '/api/share_image',
                {params: {login_name: login_name, share_name: share_name, image_name: image_name}});
        },
        get_shared_image : function (login_name) {
            return $http.get(base + '/api/get_shared_image',
                {params: {login_name: login_name}});
        },
        get_summary : function (login_name) {
            return $http.get(base + '/api/get_summary',
                {params: {login_name: login_name}});
        },
        delete_image : function (login_name, image_name) {
            return $http.get(base + '/api/delete_image',
                {params: {login_name: login_name, image_name: image_name}});
        }
    }
});