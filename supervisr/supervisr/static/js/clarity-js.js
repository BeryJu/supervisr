$('[clrDropdown]').on('click', function (e) {
    $(e.target).parent().toggleClass('open');
});

$('[clrAlert]').on('click', function (e) {
    $(e.target).closest('.alert.alert-app-level').remove();
});