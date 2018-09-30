import { Component, ElementRef } from '@angular/core';
import { ClrDatagridStateInterface } from '@clr/angular';
import { API } from '../services/api';
import { APIPath } from '../services/path';
import { HTMLChildrenComponent } from '../base';
import { Model } from '../services/model';

function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

@Component({
    selector: 'datagrid',
    templateUrl: './datagrid.component.html'
})
export class DatagridComponent extends HTMLChildrenComponent {

    loading = true;

    selected: Array<object> = [];
    dataset: Array<object> = [];
    headerColumns: Array<string> = [];
    bodyColumns: Array<string> = [];

    addView: string = null;
    editView: string = null;
    deleteView: string = null;

    private apiPath: APIPath = null;

    constructor(private api: API, element: ElementRef) {
        super();
        this.apiPath = APIPath.fromString(element.nativeElement.attributes.getNamedItem('api-path').value);
    }

    getValue(obj: object, path: string) {
        return path.split('.').reduce((o, i) => o[i], obj);
    }

    onChildren() {
        this.children.forEach(element => {
            const tagName = element.tagName.toLowerCase();
            if (tagName === 'clr-header-column') {
                // Column Declaration, append to headerColumns and bodyColumns
                this.headerColumns.push(element.innerText);
                this.bodyColumns.push(element.attributes.getNamedItem('field').value);
            } else if (tagName === 'clr-action') {
                // Action bar declaration
                this.addView = element.attributes.getNamedItem('add-view').value;
                this.editView = element.attributes.getNamedItem('edit-view').value;
                this.deleteView = element.attributes.getNamedItem('delete-view').value;
            }
        });
    }

    action(action: string) {
        if (action === 'edit' || action === 'delete') {
            // edit and delete can only be triggered when 1 item is selected
            const item = this.selected[0];
            let view = '';
            if (action === 'edit') {
                view = this.editView;
            } else if (action === 'delete') {
                view = this.deleteView;
            }
            this.api.reverse(view, { 'uuid': item['uuid'] }).subscribe(
                data => window.location.href = data['data'] + '?back=' + window.location.pathname,
                err => console.error(err)
            );
        } else if (action === 'add') {
            // add things
            this.api.reverse(this.addView).subscribe(
                data => window.location.href = data['data'] + '?back=' + window.location.pathname,
                err => console.error(err)
            );
        }
    }

    refresh(state: ClrDatagridStateInterface) {
        this.loading = true;
        this.api
            .path(this.apiPath)
            .filter(state.filters)
            .sort(<{ by: string, reverse: boolean }>state.sort)
            .paginate(state.page.from, state.page.size)
            .request()
            .subscribe(
                data => {
                    sleep(500).then(() => {
                        this.dataset = [];
                        data['data'].forEach(element => {
                            this.dataset.push(new Model().fromObject(element));
                        });
                        this.loading = false;
                    });
                },
                err => console.error(err)
            );
    }

}
