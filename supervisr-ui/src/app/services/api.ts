import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ClrDatagridFilterInterface } from '@clr/angular';

export enum Actions {
    Create = 'create',
    Read = 'read',
    Update = 'update',
    Delete = 'delete'
}

export class APIPath {

    app: string = '';
    component: string = '';
    action: Actions | string = '';

    static fromString(source: string): APIPath {
        var parts = source.split('::');
        var path = new APIPath();
        path.app = parts[0];
        path.component = parts[1];
        path.action = parts[2];
        return path;
    }

}

@Injectable()
export class API {

    version = 1;
    baseUrl = '/';

    constructor(private http: HttpClient) { }

    private _component: string;
    private _app: string;
    private _action: Actions | string;
    private _query: object = {};

    private buildUrl(app: string, component: string, action: string): string {
        return `${this.baseUrl}api/${app}/v${this.version}/${component}/${action}/`;
    }

    // Chainable functions

    public path(path: APIPath) {
        this._app = path.app;
        this._component = path.component;
        this._action = path.action;
        return this;
    }

    public component(component: string) {
        this._component = component;
        return this;
    }

    public app(app: string) {
        this._app = app;
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

    // Start request

    public request(method: string = 'GET') {
        var url = this.buildUrl(this._app, this._component, this._action);
        if (this._query) {
            url += '?';
            var query = Object.keys(this._query)
                .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(this._query[key]))
                .join('&');
            url += query;
        }
        var response = this.http.request(method, url);
        this._component = this._action = this._app = null;
        this._query = {};
        return response;
    }

    // Shortcut functions

    public reverse(viewName: string, kwargs?: object) {
        this.app('core')
            .component('utils')
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

}
