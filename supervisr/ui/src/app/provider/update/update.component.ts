import { Component } from '@angular/core';
import { API } from '../../services/api';
import { Actions } from '../../services/actions';

@Component({
    selector: 'provider-update',
    templateUrl: './update.component.html',
})
export class ProviderUpdateComponent {

    providers: Array<object> = [];
    result_data: object = null;

    provider = '';

    constructor(private api: API) {
        this.api.app('core').component('providers').action(Actions.Read).request().subscribe(
            data => { this.providers = data['data']; },
            err => console.error(err)
        );
    }

    public update() {
        this.api
            .app('core')
            .component('providers')
            .action('trigger_update')
            .queryString('uuid', this.provider)
            .request()
            .subscribe(
                data => { console.log(data); },
                err => console.error(err),
                () => console.log('we triggered')
            );
    }

}
