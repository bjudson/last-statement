$(document).ready(function(){
    $('#info-btn').on('click', function(event){
        var btn = $('#info-btn');

        if(btn.hasClass('info-btn-selected')){
            btn.removeClass('info-btn-selected');
        }else{
            btn.addClass('info-btn-selected');
        }

        $('#more-info').slideToggle('fast');

        $('html, body').animate({
            scrollTop: btn.offset().top + 500
        }, 1000);

        return false;
    })
});