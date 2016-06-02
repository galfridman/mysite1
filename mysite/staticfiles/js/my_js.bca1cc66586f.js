$(document).ready(function() {
    var s = $("#sticker");
    var pos = s.offset().top+s.height(); //offset that you need is actually the div's top offset + it's height
    $(window).scroll(function() {
        var windowpos = $(window).scrollTop(); //current scroll position of the window
        var windowheight = $(window).height(); //window height
        if (windowpos+windowheight>pos) s.addClass('stick'); //Currently visible part of the window > greater than div offset + div height, add class
        else s.removeClass('stick');
    });
});
//$(.'scroll-down').each(function(){
//var elem = document.getElementsByClassName('scroll-down');
//elem[0].scrollTop = elem[0].scrollHeight;
//});

$('.scroll-down').each(function(){
    this.scrollTop = this.scrollHeight;
});