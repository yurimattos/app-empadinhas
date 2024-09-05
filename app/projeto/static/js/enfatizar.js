$(function () {
    $(".enfatizar").click(function ( event ) {
        event.preventDefault();
        $('.enfatizar').removeClass('active');
        $(this).addClass('active');
    });
});