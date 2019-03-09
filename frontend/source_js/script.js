// Write any custom javascript functions here
var navOffset = $("nav").offset().top;
$(window).scroll(function () {
    var myarray = [];
    $('.starter_option a').each(function () {
        myarray.push($(this).prop('hash'));
    });
    var scrollPos = $(window).scrollTop();
    if(scrollPos > navOffset+50) {
        $("#nav_bar").addClass("navbar-fixed");
    } else {
        $("#nav_bar").removeClass("navbar-fixed");
    }
});