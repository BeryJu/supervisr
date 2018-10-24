import { Component, ElementRef, AfterViewInit } from '@angular/core';
import { ClrDatagridStateInterface } from '@clr/angular';
import { API } from '../services/api';
import { APIPath } from '../services/path';
import { HTMLChildrenComponent } from '../base';
import { Model } from '../services/model';
import * as $ from 'jquery';

function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

@Component({
    selector: 'datagrid',
    templateUrl: './datagrid.component.html'
})
export class DatagridComponent extends HTMLChildrenComponent implements AfterViewInit {

    loading = true;

    selected: Array<object> = [];
    dataset: Array<object> = [];
    headerColumns: Array<string> = [];
    bodyColumns: Array<string> = [];

    addView: string = null;
    editView: string = null;
    deleteView: string = null;
    actionBarItems: Array<HTMLElement> = [];

    private apiPath: APIPath = null;
    private lastState: ClrDatagridStateInterface = null;

    constructor(private api: API, private element: ElementRef) {
        super();
        this.apiPath = APIPath.fromString(this.element.nativeElement.attributes.getNamedItem('api-path').value);
    }

    ngAfterViewInit() {
        const actionBar = $(this.element.nativeElement).find('clr-dg-action-bar');
        this.actionBarItems.forEach(item => {
            actionBar.find('.btn-group').first().append(item);
        });
    }

    getValue(obj: object, path: string) {
        // Optionally support modifiers like value|keys
        let modifier = '';
        if (path.indexOf('|') !== -1) {
            // Split modifier off of path
            const parts = path.split('|');
            path = parts[0];
            modifier = parts[1];
        }
        const value = path.split('.').reduce((o, i) => o[i], obj);
        // Handle empty value early
        if (value === undefined) {
            return value;
        }
        if (modifier === 'keys') {
            // Return all keys of object
            return Object.keys(value).join(', ');
        } else if (modifier === 'join') {
            // Join array by comma
            return value.join(', ');
        } else if (modifier === 'length') {
            // Get length of string or length of keys
            if (typeof value === 'string') {
                return value.length;
            } else {
                return Object.keys(value).length;
            }
        } else if (modifier === 'bool') {
            // Beautify bool
            if (value === true) {
                return 'Yes';
            } else if (value === false) {
                return 'No';
            }
        } else {
            return value.toString();
        }
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
            } else {
                this.actionBarItems.push(element);
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
        } else if (action === 'refresh') {
            // refresh from API
            this.refresh(this.lastState);
        }
    }

    refresh(state: ClrDatagridStateInterface) {
        this.loading = true;
        this.lastState = state;
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
