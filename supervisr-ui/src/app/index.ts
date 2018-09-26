import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { BrowserModule } from '@angular/platform-browser';
import { NgModule, ApplicationRef, Injector, ComponentFactoryResolver } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { ClarityModule, ClrFormsNextModule } from '@clr/angular';
import { ProviderUpdateComponent } from './provider/update/update.component';
import { ProviderStatusComponent } from './provider/status/status.component';
import { DatagridComponent } from './datagrid/datagrid.component';
import { API } from './services/api';
import './legacy/clarity-js';
import './legacy/supervisr.js';
import * as $ from 'jquery';

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

    constructor(
        private injector: Injector,
        private componentFactoryResolver: ComponentFactoryResolver) { }

    ngDoBootstrap(app: ApplicationRef) {
        COMPONENTS.forEach((component) => {
            const widgetCompFactory = this.componentFactoryResolver.resolveComponentFactory(<any>component);
            var selector = "angular[data-component=" + widgetCompFactory.selector;
            $(selector).each((_, el) => {
                var compRef = widgetCompFactory.create(this.injector, [], el);
                app.attachView(compRef.hostView);
            });
        })
    }

 }
