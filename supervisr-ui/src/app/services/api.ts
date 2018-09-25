import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ClrDatagridFilterInterface } from '@clr/angular';

export enum Actions {
    Create = 'create',
    Read = 'read',
    Update = 'update',
    Delete = 'delete'
}

@Injectable()
export class API {

    version = 1;
    baseUrl = '/';

    constructor(private http: HttpClient) { }

    private _component: string;
    private _part: string;
    private _action: Actions | string;
    private _query: object = {};

    private buildUrl(component: string, part: string, action: string): string {
        return `${this.baseUrl}api/${component}/v${this.version}/${part}/${action}/`;
    }

    public component(component: string) {
        this._component = component;
        return this;
    }

    public part(part: string) {
        this._part = part;
        return this;
    }

    public action(action: Actions | string) {
        this._action = action;
        return this;
    }

    public filter(filters: ({ property: string; value: string; } | ClrDatagridFilterInterface<any>)[]) {
        if (!filters) return this;
        filters.forEach((filter) => {
            if (filter.hasOwnProperty('property')) {
                this._query[`__filter__${filter['property']}`] = filter['value'];
            }
        });
        return this;
    }

    public sort(sort: { by: string, reverse: boolean }) {
        if (sort !== undefined) {
            this._query['__order_by'] = sort.by;
            this._query['__reverse'] = sort.reverse;
        }
        return this;
    }

    public paginate(from: number, to: number) {
        this._query['__from'] = from;
        this._query['__to'] = to;
        return this;
    }

    public queryString(key: string, value: string) {
        this._query[key] = value;
        return this;
    }

    public reverse(viewName: string, kwargs?: object) {
        this.component('core')
            .part('utils')
            .action('reverse')
            .queryString('__view_name', viewName);
        if (kwargs !== undefined) {
            for (const key in kwargs) {
                if (kwargs.hasOwnProperty(key)) {
                    const element = kwargs[key];
                    this.queryString(key, element);
                }
            }
        }
        return this.request();
    }

    public translate(message: string, kwargs?: object) {
        this.component('core')
            .part('utils')
            .action('gettext')
            .queryString('__message', message);
        if (kwargs !== undefined) {
            for (const key in kwargs) {
                if (kwargs.hasOwnProperty(key)) {
                    const element = kwargs[key];
                    this.queryString(key, element);
                }
            }
        }
        return this.request();
    }

    public request(method: string = 'GET') {
        var url = this.buildUrl(this._component, this._part, this._action);
        if (this._query) {
            url += '?';
            var query = Object.keys(this._query)
                .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(this._query[key]))
                .join('&');
            url += query;
        }
        var response = this.http.request(method, url);
        this._component = this._action = this._part = null;
        this._query = {};
        return response;
    }

}
