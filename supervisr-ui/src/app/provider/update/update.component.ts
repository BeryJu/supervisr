import { Component } from '@angular/core';
import { API, Actions } from '../../services/api';

@Component({
    selector: 'provider-update',
    templateUrl: './update.component.html',
})
export class ProviderUpdateComponent {

    providers: Array<object> = [];
    result_data: object = null;

    provider: string = '';

    constructor(private api: API) {
        this.api.component('core').part('providers').action(Actions.Read).request().subscribe(
            data => { this.providers = data['data'] },
            err => console.error(err)
        );
    }

    public update() {
        this.api
            .component('core')
            .part('providers')
            .action('trigger_update')
            .queryString('uuid', this.provider)
            .request()
            .subscribe(
                data => { console.log(data) },
                err => console.error(err),
                () => console.log('we triggered')
            );
    }

}
