import * as $ from 'jquery';

$('document').ready(function() {
    $(document).click(function () {
        $('[clrDropdown]').closest('div.dropdown').removeClass('open');
    });

    $('[clrDropdown]').on('click', e => {
        e.stopPropagation();
        $(e.target).closest('div.dropdown').toggleClass('open');
    });

    $('[clrAlert]').on('click', e => {
        $(e.target).closest('.alert').remove();
    });

    $('.clr-root-container button.header-overflow-trigger').on('click', e => {
        $('.clr-root-container').toggleClass('open-overflow-menu');
    });

    $('.clr-root-container button.header-hamburger-trigger').on('click', e => {
        $('.clr-root-container').toggleClass('open-hamburger-menu');
    });

    $('.clr-root-container .header-backdrop').on('click', e => {
        $('.clr-root-container').removeClass('open-overflow-menu');
        $('.clr-root-container').removeClass('open-hamburger-menu');
    });

    $('.modal [data-action=close]').on('click', e => {
        $(e.target).closest('.modal').hide();
    });

    $('[data-action=show-modal]').on('click', e => {
        const modalId = $(e.target).data('modal');
        $('#' + modalId).show();
    });
});

export function clrWizard (container: string, initialPage) {
    const containerId = '#' + container;
    const maxStepForward = 1;
    const maxStepBackward = 99999;
    const totalPages = $(`${containerId} .clr-nav-content`).length - 1; // - 1 because we're 0 based
    let currentPage = 0;

    const updateCurrent = function (page, lastPage) {
        // Update main container
        $(`${containerId} div.clr-nav-content:eq(${lastPage})`).attr('data-hidden', true);
        $(`${containerId} div.clr-nav-content:eq(${page})`).attr('data-hidden', false);

        for (let i = lastPage; i > page; i--) {
            $(`${containerId} li.clr-nav-link:eq(${i})`).removeClass('complete active');
        }

        $(`${containerId} li.clr-nav-link:eq(${lastPage})`).removeClass('complete active');
        $(`${containerId} li.clr-nav-link:eq(${page})`).removeClass('complete');
        // Update sidebar
        $(`${containerId} li.clr-nav-link:eq(${page})`).addClass('active');
        // Update sidebar complete class
        if (page > lastPage) {
            // only add complete class when we go forward
            $(`${containerId} li.clr-nav-link:eq(${lastPage})`).addClass('complete');
        }


        // Disable/enable buttons

        // Check if we're done
        if (page === totalPages) {
            $(`${containerId} [clrWizNext]`).hide();
            $(`${containerId} [clrWizFinish]`).show();
        } else {
            $(`${containerId} [clrWizNext]`).show();
            $(`${containerId} [clrWizFinish]`).hide();
        }

        // Disable Back on start
        if (page === 0) {
            $(`${containerId} [clrWizBack]`).addClass('disabled');
        } else {
            $(`${containerId} [clrWizBack]`).removeClass('disabled');
        }
    };

    const reset = function () {
        currentPage = 0;
        // Remove all active's and completed
        $(`${containerId} li.clr-nav-link`).removeClass('active complete');

        updateCurrent(0, 0);
    };

    // Do cancel (x and Cancel button)
    $(`${containerId} [clrWizCancel]`).on('click', e => {
        $(e.target).parents(containerId).addClass('hidden');
    });

    $(`${containerId} [clrWizBack]`).on('click', e => {
        if (currentPage === 0) { return; }
        currentPage -= 1;
        updateCurrent(currentPage, currentPage + 1);
    });

    $(`${containerId} [clrWizNext]`).on('click', e => {
        updateCurrent(currentPage + 1, currentPage);
        currentPage += 1;
    });

    $(`${containerId} li.clr-nav-link button.btn`).on('click', e => {
        const parent = $(e.target).parents('li.clr-nav-link');
        const listChildren = $(e.target).parents('ol.navList').children();
        const idx = listChildren.index(parent);
        if ((idx > currentPage + maxStepForward) || (idx < currentPage - maxStepBackward)) {
            return;
        }
        updateCurrent(idx, currentPage);
        currentPage = idx;
    });

    // Show by button click
    $(`[clrWizLauncher][data-id="${containerId}"]`).on('click', e => {
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
}

export function clrTabs() {
    let currentTab = '';

    const unseletTab = function (id) {
        if (id === '') {
            return;
        }
        $(`section#${id}`).attr('aria-hidden', true);
        const btn = $(`ul[role="tablist"] button[aria-controls="${id}"]`);
        btn.removeClass('active');
        btn.attr('aria-selected', false);
    };
    const selectTab = function (id) {
        if (id === '' || id === undefined) {
            return;
        }
        $(`section#${id}`).attr('aria-hidden', false);
        const btn = $(`ul[role="tablist"] button[aria-controls="${id}"]`);
        btn.addClass('active');
        btn.attr('aria-selected', true);
        currentTab = id;
        window.location.hash = `clr_tab=${id}`;
    };

    const hash = window.location.hash.substr(1);
    if (hash.startsWith('clr_tab')) {
        selectTab(hash.replace('clr_tab=', ''));
    } else {
        const first = $('ul[role="tablist"] li button').first().attr('aria-controls');
        selectTab(first);
    }

    $('ul[role="tablist"] li button').on('click', e => {
        unseletTab(currentTab);
        selectTab($(e.target).attr('aria-controls'));
    });

    return {
        'unseletTab': unseletTab,
        'selectTab': selectTab,
    };
}

export function clrTableSelect(container) {
    $(`${container} [data-ctx-name]`).addClass('disabled');
    $(`${container} tr[data-selectable]`).on('click', e => {
        const tr = $(e.target).parent('tr');
        tr.addClass('selected');
        tr.siblings().removeClass('selected');
        for (const k in tr.data()) {
            if (k.startsWith('ctx')) {
                const key = k.replace('ctx', '').toLowerCase();
                const url = tr.data(k);
                $(`${container} [data-ctx-name="${key}"]`).attr('href', url);
                $(`${container} [data-ctx-name]`).removeClass('disabled');
            }
        }
    });
}

export function clrSidenav(containerSelector) {
    const container = $(containerSelector);
    const navTrigger = container.children('.nav-trigger');
    const navTriggerIcon = navTrigger.children('.nav-trigger-icon');

    let isCollapsed = container.hasClass('is-collapsed');

    // Collapse trigger
    const updateCollapse = function () {
        if (isCollapsed === false) {
            container.addClass('is-collapsed');
            navTriggerIcon.attr('dir', 'right');
        } else if (isCollapsed === true) {
            container.removeClass('is-collapsed');
            navTriggerIcon.attr('dir', 'left');
        }
        isCollapsed = !isCollapsed;
    };

    navTrigger.on('click', function () {
        updateCollapse();
    });

    container.find('.nav-group-trigger').on('click', function () {
        const subContainer = $(this).parents('clr-vertical-nav-group');
        const icon = subContainer.find('.nav-group-trigger-icon');
        const isGroupExpanded = subContainer.hasClass('is-expanded');
        const toggleChildren = function () {
            subContainer.find('.nav-group-children').each(function () {
                $(this).toggleClass('nav-group-children-hidden');
            });
        };
        if (isGroupExpanded === false) {
            if (isCollapsed === true) {
                updateCollapse();
            }
            toggleChildren();
            icon.attr('dir', 'down');
        } else if (isGroupExpanded === true) {
            toggleChildren();
            icon.attr('dir', 'right');
        }
        subContainer.toggleClass('is-expanded');
    });
}

window['clrTabs'] = clrTabs;
window['clrTableSelect'] = clrTableSelect;
window['clrWizard'] = clrWizard;
window['clrSidenav'] = clrSidenav;
