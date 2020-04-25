import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { OverviewComponent } from './overview/overview.component';

const routes: Routes = [];

@NgModule({
  imports: [RouterModule.forRoot(routes),
  RouterModule.forRoot([
      {
        path: '',
        component: OverviewComponent
      }
      
    ],{useHash:true})],
  exports: [RouterModule]
})
export class AppRoutingModule { }
