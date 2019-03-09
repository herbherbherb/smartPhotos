var AppServices=angular.module("AppServices",[]);AppServices.factory("Data",function($http){var base="http://0.0.0.0:5000";return{getLabel:function(data){return $http.get(base+"/api/label",{params:{name:data}})},putLabel:function(old_name,new_name,username){return $http.get(base+"/api/label_change",{params:{old_name:old_name,new_name:new_name,username:username}})},getImage:function(data){return $http.get(base+"/api/image",{params:{name:data}})},postImage:function(data){return $http.post(base+"/api/upload",data,{headers:{"Content-Type":void 0},transformRequest:angular.identity})},init_image:function(username){return $http.get(base+"/api/init_image",{params:{username:username}})},register:function(username,password){return $http.get(base+"/api/register",{params:{username:username,password:password}})},login:function(username,password){return $http.get(base+"/api/login",{params:{username:username,password:password}})},share_image:function(login_name,share_name,image_name){return $http.get(base+"/api/share_image",{params:{login_name:login_name,share_name:share_name,image_name:image_name}})},get_shared_image:function(login_name){return $http.get(base+"/api/get_shared_image",{params:{login_name:login_name}})},get_summary:function(login_name){return $http.get(base+"/api/get_summary",{params:{login_name:login_name}})},delete_image:function(login_name,image_name){return $http.get(base+"/api/delete_image",{params:{login_name:login_name,image_name:image_name}})}}});