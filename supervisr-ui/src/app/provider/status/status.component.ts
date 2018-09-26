import { Component, ElementRef } from '@angular/core';
import { API } from '../../services/api';

@Component({
    selector: 'provider-status',
    templateUrl: './status.component.html',
})
export class ProviderStatusComponent {

    providerUUID: string = '';

    status: boolean | string = null;
    loading: boolean = true;

    constructor(private api: API, private element: ElementRef) {
        this.providerUUID = element.nativeElement.dataset['uuid'];
        this.api
            .component('core')
            .part('providers')
            .action('status')
            .queryString('provider_uuid', this.providerUUID)
            .request().subscribe(
            data => {
                this.status = data['data'];
                this.loading = false;
            },
            err => console.error(err)
        );
    }

}
