import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { BrowserModule } from '@angular/platform-browser';
import { NgModule, ApplicationRef } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { ClarityModule, ClrFormsNextModule } from '@clr/angular';
import { ProviderUpdateComponent } from './provider/update/update.component';
import { ProviderStatusComponent } from './provider/status/status.component';
import { DatagridComponent } from './datagrid/datagrid.component';
import { API } from './services/api';
import './legacy/clarity-js';
import './legacy/supervisr.js';

const COMPONENTS = [
    DatagridComponent,
    ProviderUpdateComponent,
    ProviderStatusComponent,
];

@NgModule({
    declarations: COMPONENTS,
    imports: [
        BrowserAnimationsModule,
        BrowserModule,
        FormsModule,
        HttpClientModule,
        ClarityModule,
        ClrFormsNextModule
    ],
    providers: [
        API
    ],
    entryComponents: COMPONENTS,
})
export class AppModule {

    ngDoBootstrap(app: ApplicationRef) {
        COMPONENTS.forEach((component) => {
            try {
                app.bootstrap(<any>component);
            } catch (error) {
                // Empty catch since we anticipate selectors not existing
            }
        });
    }

 }
