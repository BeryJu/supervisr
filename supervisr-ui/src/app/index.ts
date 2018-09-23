import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { ClarityModule, ClrFormsNextModule } from '@clr/angular';
import { ProviderUpdateComponent } from './provider/update/update.component';
import { API } from './services/api';

@NgModule({
    declarations: [
        ProviderUpdateComponent
    ],
    imports: [
        BrowserAnimationsModule,
        BrowserModule,
        FormsModule,
        HttpClientModule,
        ClarityModule,
        ClrFormsNextModule
        // ROUTING
    ],
    providers: [
        API
    ],
    bootstrap: [
        ProviderUpdateComponent
    ]
})
export class AppModule { }
