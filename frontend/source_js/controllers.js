/**
 * Controller for login page
 */
app.controller('login_ctr', function($scope, $window, $rootScope, Data) {
    $scope.username = "";
    $scope.password = "";
    $scope.change = {"noshow": false, "yesshow": false, "yes": false};
    $scope.login = function(){
        $scope.change.noshow = false;
        $scope.change.yesshow = false;
        $scope.change.yes = false;
        Data.login($scope.username, $scope.password).success(function(data){
            if(data.message === "username"){
                $scope.change.noshow = true;
            }
            if(data.message === "password"){
                $scope.change.yesshow = true;
            }
            if(data.message === "yes"){
                $scope.change.yes = true;
                $rootScope.login_name = $scope.username;
                data = data.result;
                for (var i = 0; i < data.length; i++) {
                    var cur_image = 'data:image/png;base64,' + data[i]['image']['py/b64'];
                    var cur_title = data[i].title;
                    var cur_label = data[i].label.split(',');
                    $rootScope.stepsModel.push({image:cur_image, title:cur_title, rank: i + $rootScope.stepsModel.length, labels: cur_label});
                }
                $window.location.href = '#/list/';
                
            }
        }).error(function(data){
        });
    };
    $scope.register = function(){
        $window.location.href = '#/register/';
    };
});

/**
 * Controller for register page
 */
app.controller('register_ctr', function($scope, $window, $rootScope, Data) {
    $scope.username = "";
    $scope.password = "";
    $scope.change = {"noshow": false, "yesshow": false};
    $scope.register = function(){
        $scope.change.noshow = false;
        $scope.change.noshow = false;
        Data.register($scope.username, $scope.password).success(function(data){
            if(data.message === "no"){
                $scope.change.noshow = true;
            }
            if(data.message === "yes"){
                $scope.change.yesshow = true;
                setTimeout(function(){$window.location.href = '#/login/';}, 1500);
            }
        }).error(function(data){});
    };
});

/**
 * Controller for gallery page
 */
app.controller('gal_ctr', function($scope, $rootScope, Data) {
    $scope.search = "null";
    $scope.query = "";
    $scope.showMovie = function(item){
        var result = false;
        if($scope.search === "all")
        {return true;}
        if($scope.search === "null")
        {return true;}
        for(i=0; i < $rootScope.stepsModel.length; i++) {
            if ($rootScope.stepsModel[i].title === item.title){
                for(j=0; j < $rootScope.stepsModel[i].labels.length; j++) {
                    if ($scope.search === $rootScope.stepsModel[i].labels[j]) {result = true; break;}
                }
                break;
            }
        }
        return result;
    };

    function check(labels, queryString){
        for(c=0; c < labels.length; c++) {

            if (queryString.includes(labels[c])
                || labels[c].includes(queryString)) {return true;}
        }
        return false;
    }

    $scope.queryMovie = function(item){
        if($scope.query === "")
        {return true;}
        var queryinput = $scope.query.toLowerCase()
            .replace("airplane", "aeroplane").replace("airplanes", "aeroplane").replace("plane", "aeroplane")
            .replace("bike", "bicycle").replace("bikes", "bicycle").replace("bicycles", "bicycle").replace("birds", "bird")
            .replace("boats", "boat").replace("ships", "boat").replace("bottles", "bottle").replace("buses", "bus")
            .replace("cars", "car").replace("cats", "cat").replace("chairs", "chair").replace("cows", "cow")
            .replace("dogs", "dog").replace("horses", "horse").replace("motorbikes", "motorbike").replace("motorcycles", "motorbike")
            .replace("people", "person").replace("tv", "tvmonitor");

        if (queryinput.includes("and")){
            for(i=0; i < $rootScope.stepsModel.length; i++) {
                if ($rootScope.stepsModel[i].title === item.title){
                    var result = true;
                    querySplit = queryinput.split("and");
                    for(j=0; j < querySplit.length; j++) {
                        result = result && check($rootScope.stepsModel[i].labels, querySplit[j].replace(/\s/g, ''));
                    }
                    return result;
                }
            }
        }
        else if (queryinput.includes("or")){
            for(i=0; i < $rootScope.stepsModel.length; i++) {
                if ($rootScope.stepsModel[i].title === item.title){
                    var result = false;
                    querySplit = queryinput.split("or");
                    for(j=0; j < querySplit.length; j++) {
                        result = result || check($rootScope.stepsModel[i].labels,querySplit[j]);
                    }
                    return result;
                }
            }
        }
        else{
            for(i=0; i < $rootScope.stepsModel.length; i++) {
                if ($rootScope.stepsModel[i].title === item.title){
                    for(j=0; j < $rootScope.stepsModel[i].labels.length; j++) {
                        if (queryinput.includes($rootScope.stepsModel[i].labels[j])) {return true;}
                    }
                    break;
                }
            }
        }
    };
    $scope.username = "";
    $scope.myFunc = function(item) {
        $scope.username = item.title;
    };
});

/**
 * Controller for summary page
 */
app.controller('summary_ctr', function($scope, $routeParams, $rootScope, Data) {
    var login_name = $rootScope.login_name;
    $scope.share = {'show1': false};
    if(login_name === ""){
        $scope.share.show1 = true;
    }
    $scope.labels = [];
    $scope.data = [];
    Data.get_summary(login_name).success(function(data){
        $scope.share.show1 = false;
        for (var key in data.result) {
            if (data.result.hasOwnProperty(key)) {
                $scope.labels.push(key);
                $scope.data.push(data.result[key]);
            }
        }
    }).error(function(data){

    });
});

/**
 * Controller for list page
 */
app.controller('list_ctr', function($scope, $rootScope, Data) {
    $scope.search = { by:"title", in:false, stri:""};
    $scope.username = "";
    $scope.myFunc = function(item) {
        $scope.username = item.title;
    };
    // $rootScope.stepsModel = [];
    $scope.imageUpload = function(event){
        var files = event.target.files; //FileList object

        for (var i = 0; i < files.length; i++) {
            var file = files[i];
            var reader = new FileReader();
            reader.onload = $scope.imageIsLoaded(file, i);
            reader.readAsDataURL(file);
        }
    };
    $scope.imageIsLoaded = function(f, i){
        return function(e) {
            var base64result = e.target.result.substr(e.target.result.indexOf(',') + 1);
            $rootScope.stepsModel.push({image:e.target.result, title:f.name, rank: i, labels: []});
            Data.postImage(JSON.stringify({image: base64result, name: f.name, user: $rootScope.login_name}))
                .success(function(data){
                    for(i=0; i < $rootScope.stepsModel.length; i++) {
                        if(data.name === $rootScope.stepsModel[i].title){
                            $rootScope.stepsModel[i].labels = data.labels;
                            break;
                        }
                    }
                }).error(function(data){});
        };
    };
});

/**
 * Controller for image details page
 */
app.controller('share_ctr', function($scope, $routeParams, $rootScope, Data) {
    $scope.shared_images  = [];
    $scope.share = {'show1': false};
    // $scope.myFunc = function(item) {
    //     $scope.username = item.title;
    // };

    var login_name = $rootScope.login_name;
    Data.get_shared_image(login_name).success(function(data){
        if(data.message === "no"){
            $scope.share.show1 = true;
        }
        if(data.message === "yes"){
            data = data.result;
            for (var i = 0; i < data.length; i++) {
                var cur_image = 'data:image/png;base64,' + data[i]['image']['py/b64'];
                var cur_title = data[i].title;
                var share_person = data[i].share_person;
                $scope.shared_images.push({image:cur_image, title:cur_title, share_person: share_person});
            }
        }
    }).error(function(data){

    });

});

/**
 * Controller for image details page
 */
app.controller('detail_ctr', function($scope, $routeParams, $rootScope, $window, Data) {
    $scope.username = $routeParams.username;
    $scope.change = {'name': $scope.username, 'show': false};
    $scope.share = {'name': "", 'show1': false, 'show2': false};

    $scope.share_image = function () {
        $scope.share.show1 = false;
        $scope.share.show2 = false;
        var image_name = $scope.username;
        var username = $scope.share.name;
        var login_name = $rootScope.login_name;
        Data.share_image(login_name, username, image_name).success(function(data){
            if(data.message === "no"){
                $scope.share.show1 = true;
            }
            if(data.message === "yes"){
                $scope.share.show2 = true;
            }
        }).error(function(data){

        });
    };
    var login_name = $rootScope.login_name;
    $scope.delete = function(){
        for(i=0; i < $rootScope.stepsModel.length; i++) {
            var current = $rootScope.stepsModel[i];
            if($scope.username === current.title){
                if(i === $rootScope.stepsModel.length-1){
                    $scope.nextRight = $rootScope.stepsModel[0].title;
                }
                else {
                    $scope.nextRight = $rootScope.stepsModel[i+1].title;
                }
                break;
            }
        }
        for(var i =  0; i < $rootScope.stepsModel.length; i++) {
            if($scope.username === $rootScope.stepsModel[i].title){
                break;
            }
        }
        $rootScope.stepsModel.splice(i, 1);
        Data.delete_image(login_name, $scope.username);
    };

    $scope.reset = function () {
        $scope.change.show = false;
        if ($scope.change.name === $scope.username){
            $scope.change.show = true;
            return;
        }
        for(i=0; i < $rootScope.stepsModel.length; i++) {
            if($scope.change.name === $rootScope.stepsModel[i].title){
                $scope.change.show = true;
                return;
            }
        }
        for(i=0; i < $rootScope.stepsModel.length; i++) {
            var current = $rootScope.stepsModel[i];
            if($scope.username === current.title){
                $rootScope.stepsModel[i]['title'] = $scope.change.name;
                Data.putLabel($scope.username, $scope.change.name, $rootScope.login_name);
                $scope.username = $scope.change.name;
                break;
            }
        }
    };
    $scope.showMovie = function(movie){
        var current_id = movie.title;
        return (current_id === $scope.username);
    };
    $scope.label = "None";
    $scope.processed = "";

    Data.getImage($scope.username).success(function(data){
        $scope.processed = 'data:image/png;base64,' + data.image['py/b64'];
    }).error(function(data){
        $scope.processed = "";
    });

    Data.getLabel($scope.username).success(function(data){
        $scope.label = data.label;
    }).error(function(data){
        $scope.label = "None";
    });

    $scope.nextRight = "";
    $scope.nextLeft = "";
    $scope.rightFunc = function(){
        for(i=0; i < $rootScope.stepsModel.length; i++) {
            var current = $rootScope.stepsModel[i];
            if($scope.username === current.title){
                if(i === $rootScope.stepsModel.length-1){
                    $scope.nextRight = $rootScope.stepsModel[0].title;
                }
                else {
                    $scope.nextRight = $rootScope.stepsModel[i+1].title;
                }
                break;
            }
        }

    };
    $scope.leftFunc = function(){
        for(i=0; i < $rootScope.stepsModel.length; i++) {
            var current = $rootScope.stepsModel[i];
            if($scope.username === current.title){
                if(i === 0){
                    $scope.nextLeft = $rootScope.stepsModel[$rootScope.stepsModel.length-1].title;
                }
                else {
                    $scope.nextLeft = $rootScope.stepsModel[i-1].title;
                }
                break;
            }
        }
    }
});
