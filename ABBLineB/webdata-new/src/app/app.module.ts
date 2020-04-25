import { BrowserModule } from '@angular/platform-browser';
import { NgModule, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { HttpModule } from '@angular/http';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { ApiService } from './shared/service/api.service';
import { UtilService } from './shared/service/utils.service';
import { ChartsService } from './shared/service/charts.service';

import { SidebarModule } from 'primeng/sidebar';
import { ButtonModule } from 'primeng/button';
import { AccordionModule } from 'primeng/accordion';
import { CalendarModule } from 'primeng/calendar';
import { PanelMenuModule } from 'primeng/panelmenu';
import { TableModule } from 'primeng/table';
import { MenuModule } from 'primeng/menu';
import { MenuItem } from 'primeng/api';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { InputTextModule } from 'primeng/inputtext';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule, MatInputModule, MatDatepickerModule, MatNativeDateModule,MatSelectModule,
    MatCheckboxModule,
    MatButtonModule } from '@angular/material';



import { OverviewComponent } from './overview/overview.component';
import { LoadmaskComponent } from './loadmask/loadmask.component';

@NgModule({
  declarations: [
    AppComponent,
    OverviewComponent,
    LoadmaskComponent
  ],
  schemas: [ CUSTOM_ELEMENTS_SCHEMA ],
  imports: [
    BrowserModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    HttpModule,
    SidebarModule,
    ButtonModule,
    AccordionModule,
    CalendarModule,
    PanelMenuModule,
    MenuModule,
    TableModule,
    MatDatepickerModule, MatFormFieldModule, MatInputModule,MatNativeDateModule,
    ProgressSpinnerModule,
    MatSelectModule,
    MatCheckboxModule,
    InputTextModule,
    FormsModule,
    MatButtonModule
  ],
  exports:[MatNativeDateModule],
  providers: [
    ApiService,
    UtilService,
    ChartsService,

  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
