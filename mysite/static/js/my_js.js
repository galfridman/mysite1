//$(document).ready(function() {
//    var s = $("#sticker");
//    var pos = s.offset().top+s.height(); //offset that you need is actually the div's top offset + it's height
//    $(window).scroll(function() {
//        var windowpos = $(window).scrollTop(); //current scroll position of the window
//        var windowheight = $(window).height(); //window height
//        if (windowpos+windowheight>pos) s.addClass('stick'); //Currently visible part of the window > greater than div offset + div height, add class
//        else s.removeClass('stick');
//    });
//});
//$(.'scroll-down').each(function(){
//var elem = document.getElementsByClassName('scroll-down');
//elem[0].scrollTop = elem[0].scrollHeight;
//});

$('.scroll-down').each(function(){
    this.scrollTop = this.scrollHeight;
});


$(window).load(function() {
		// Animate loader off screen
		$(".se-pre-con").fadeOut("slow");;
});



//Table
  $(".search").keyup(function () {
    var searchTerm = $(".search").val();
    var listItem = $('.results tbody').children('tr');
    var searchSplit = searchTerm.replace(/ /g, "'):containsi('")

  $.extend($.expr[':'], {'containsi': function(elem, i, match, array){
        return (elem.textContent || elem.innerText || '').toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
    }
  });

  $(".results tbody tr").not(":containsi('" + searchSplit + "')").each(function(e){
    $(this).attr('visible','false');
  });

  $(".results tbody tr:containsi('" + searchSplit + "')").each(function(e){
    $(this).attr('visible','true');
  });

  var jobCount = $('.results tbody tr[visible="true"]').length;
    $('.counter').text(jobCount + ' item');

  if(jobCount == '0') {$('.no-result').show();}
    else {$('.no-result').hide();}
		  });
//End Table


$('tr[data-href]').on("click", function() {
    document.location = $(this).data('href');
});



//search
$('#search-input').keyup(function(){
    $('.searchable').hide();
    var txt = $('#search-input').val();
    $('.searchable').each(function(){
       if($(this).text().toUpperCase().indexOf(txt.toUpperCase()) != -1){
           $(this).show();
       }
    });
});
