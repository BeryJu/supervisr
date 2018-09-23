import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

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

    public request(method: string = 'GET', q?: object) {
        var url = this.buildUrl(this._component, this._part, this._action);
        if (q) {
            url += '?';
            var query = Object.keys(q)
                .map(key => encodeURIComponent(key) + '=' + encodeURIComponent(q[key]))
                .join('&');
            url += query;
        }
        var response = this.http.request(method, url);
        this._component = this._action = this._part = null;
        return response;
    }

}
