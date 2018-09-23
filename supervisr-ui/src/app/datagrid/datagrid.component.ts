import { Component, ElementRef } from '@angular/core';
import { API, Actions } from '../services/api';
import { ClrDatagridStateInterface } from "@clr/angular";

function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

@Component({
    selector: 'datagrid',
    templateUrl: './datagrid.component.html'
})
export class DatagridComponent {

    loading: boolean = true;

    selected = [];
    dataset: Array<any> = [];
    headerColumns: Array<string> = [];
    bodyColumns: Array<string> = [];

    addView: string = '';
    editView: string = '';
    deleteView: string = '';

    attributes: object = {};

    constructor(private api: API, private element: ElementRef) {
        this.attributes = element.nativeElement.dataset;
        this.headerColumns = JSON.parse(this.attributes['headerColumns']);
        this.bodyColumns = JSON.parse(this.attributes['bodyColumns']);
        this.addView = this.attributes['addView'];
        this.editView = this.attributes['editView'];
        this.deleteView = this.attributes['deleteView'];
    }

    action(action: string) {
        if (action === 'edit' || action === 'delete') {
            // edit and delete can only be triggered when 1 item is selected
            var item = this.selected[0];
            var view = '';
            if (action === 'edit') {
                view = this.editView;
            } else if (action === 'delete') {
                view = this.deleteView;
            }
            this.api.reverse(view, { 'uuid': item['uuid'] }).subscribe(
                data => window.location.href = data['data'] + '?back=' + window.location.href,
                err => console.error(err)
            );
        } else if (action === 'add') {
            // add things
            this.api.reverse(this.addView).subscribe(
                data => window.location.href = data['data'] + '?back=' + window.location.href,
                err => console.error(err)
            );
        }
    }

    refresh(state: ClrDatagridStateInterface) {
        this.loading = true;
        this.api
            .component(this.attributes['apiComponent'])
            .part(this.attributes['apiPart'])
            .action(this.attributes['apiAction'])
            .filter(state.filters)
            .sort(<{ by: string, reverse: boolean }>state.sort)
            .paginate(state.page.from, state.page.size)
            .request()
            .subscribe(
                data => {
                    sleep(500).then(() => {
                        this.dataset = data['data'];
                        this.loading = false;
                    });
                },
                err => console.error(err)
            );
    }

}
