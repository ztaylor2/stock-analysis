$(document).ready(function() {
  $('icon-menu').on('click', function() {
    $('toggle-menu').removeClass('inactive').addClass('active');
  });

  $('icon-menu').on('click', function() {
    $('toggle-menu').removeClass('active').addClass('inactive');
  });
});
