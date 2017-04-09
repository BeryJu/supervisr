$('[clrDropdown]').on('click', function (e) {
    $(e.target).parent().toggleClass('open');
});

$('[clrAlert]').on('click', function (e) {
    $(e.target).closest('.alert.alert-app-level').remove();
});

var clrWizard = function (containerId, initialPage) {
    var containerId = '#' + containerId;
    var currentPage = 0;
    var maxStepForward = 1;
    var maxStepBackward = 99999;
    var totalPages = $(containerId + ' .clr-nav-content').length - 1; // - 1 because we're 0 based

    var updateCurrent = function (page, lastPage) {
        // Update main container
        $(containerId + ' div.clr-nav-content:eq('+lastPage+')').attr('data-hidden', true);
        $(containerId + ' div.clr-nav-content:eq('+page+')').attr('data-hidden', false);

        for (var i = lastPage; i > page; i--) {
            $(containerId + ' li.clr-nav-link:eq('+i+')').removeClass('complete active');
        }

        $(containerId + ' li.clr-nav-link:eq('+lastPage+')').removeClass('complete active');
        $(containerId + ' li.clr-nav-link:eq('+page+')').removeClass('complete');
        // Update sidebar
        $(containerId + ' li.clr-nav-link:eq('+page+')').addClass('active');
        // Update sidebar complete class
        if (page > lastPage) {
          // only add complete class when we go forward
          $(containerId + ' li.clr-nav-link:eq('+lastPage+')').addClass('complete');
        }


        // Disable/enable buttons

        // Check if we're done
        if (page == totalPages) {
            $(containerId + ' [clrWizNext]').hide();
            $(containerId + ' [clrWizFinish]').show();
        } else {
            $(containerId + ' [clrWizNext]').show();
            $(containerId + ' [clrWizFinish]').hide();
        }

        // Disable Back on start
        if (page === 0) {
            $(containerId + ' [clrWizBack]').addClass('disabled');
        } else {
            $(containerId + ' [clrWizBack]').removeClass('disabled');
        }
    };

    var reset = function () {
        currentPage = 0;
        // Remove all active's and complete's
        $(containerId + ' li.clr-nav-link').removeClass('active complete');

        updateCurrent(0, 0);
    };

    // Do cancel (x and Cancel button)
    $(containerId + ' [clrWizCancel]').on('click', function (e) {
        $(e.target).parents(containerId).addClass('hidden');
    });

    $(containerId + ' [clrWizBack]').on('click', function (e) {
        if (currentPage === 0) { return; }
        currentPage -= 1;
        updateCurrent(currentPage, currentPage + 1);
    });

    $(containerId + ' [clrWizNext]').on('click', function (e) {
        updateCurrent(currentPage + 1, currentPage);
        currentPage += 1;
    })

    $(containerId + ' li.clr-nav-link button.btn').on('click', function (e) {
        var parent = $(e.target).parents('li.clr-nav-link');
        var listChildren = $(e.target).parents('ol.navList').children();
        var idx = listChildren.index(parent);
        if ((idx > currentPage + maxStepForward) || (idx < currentPage - maxStepBackward)) return;
        updateCurrent(idx, currentPage);
        currentPage = idx;
    });

    // Show by button click
    $('[clrWizLauncher][data-id="'+containerId+'"]').on('click', function (e) {
        reset();
        $(containerId).removeClass('hidden');
    });

    reset();

    $(containerId).addClass('hidden');

    return {
        'reset': reset,
        'launch': function () {
            $(containerId).removeClass('hidden');
        }
    };
};


console.log(ClarityIcons.get('edit'));
