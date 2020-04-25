import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';


@Injectable({
  providedIn: 'root'
})

export class UtilService {

    private _filter_click;
    public FilterClick:Observable<any> = new Observable(d => this._filter_click = d);
    private _filter_values;
    public FilterValues:Observable<any> = new Observable(d => this._filter_values = d);

    private _filter_onchange;
	public FilterOnChange:Observable<any> = new Observable(d => this._filter_onchange = d);

    public notNullOrEmpty(term:any){
        let result;

        if(term !== null && term !== undefined && term !=='undefined' && term !== "" && term.length !== 0 && term !== "None"){
            result = true;
        }
        else{
            result = false;
        }
        return result;
    }

    public isNullOrEmpty(term:any){
        let result;

        if(term !== null && term !== undefined && term !== "undefined" && term !== "" && term.length !== 0 && term !== "None"){
            result = false;
        }
        else{
            result = true;
        }
        return result;
    }

    public guid() {
        function s4() {
            return Math.floor((1 + Math.random()) * 0x10000)
            .toString(16)
            .substring(1);
        }
        return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
    }

    public randomNum(){
        return Math.floor((Math.random() * 100) + 1);
    }

    public isEmptyObject(obj) {
        return Object.keys(obj).length === 0 && obj.constructor === Object;
    }

    public jsUcfirst(string) {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }

    public ucFirstAllWords(str){
        var pieces = str.split(" ");
        for ( var i = 0; i < pieces.length; i++ ){
            var j = pieces[i].charAt(0).toUpperCase();
            pieces[i] = j + pieces[i].substr(1).toLowerCase();
        }
        return pieces.join(" ");
    }

    public ucFirstAllChar(str){
        var matches = str.match(/\b(\w)/g); // ['J','S','O','N']
        var acronym = matches.join(''); // JSON
        return acronym.toUpperCase();
    }

    public onFilterClick(){
        this._filter_click.next(true);
    }

    public submitFilterValue(filters){
        this._filter_values.next(filters);
    }

    public submitFilterOnChange(filters){
        this._filter_onchange.next(filters);
    }

    public arrayRemove(arr, value) {
      return arr.filter(function(ele) {
          return ele !== value;
      });
   }
}
