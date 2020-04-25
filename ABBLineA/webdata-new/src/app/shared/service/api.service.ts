import { Injectable } from '@angular/core';
import { Headers, Http, Response, URLSearchParams } from '@angular/http';
import { environment } from '../../../environments/environment';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/catch';
import { Observable } from 'rxjs';
import * as $ from "jquery";

@Injectable()
export class ApiService {

  private apiUrl = "/apis/";
  private apiGetUrl = "/apisget/";
  private apiUrlPost = "/apipost/";
  private apiGetDownload = "/downloadfile";

  constructor(private http: Http) { }

  private _handle_error(error:any) {
		if(error.status == 401 || error.status == 302 || error.status == 10 || error.status == 403 ){
			window.localStorage.clear();
			window.sessionStorage.clear();
			if('_body' in error){
				var link = error._body;
				if(link.indexOf('http') !== -1){
					location.href = link;
				}
			}
			else{
				location.reload();
			}
		};
		let message:string = (error.message) ? error.message :  error.status ? `${error.status} - ${error.statusText}` : 'Server error';
		return Observable.throw(message);
	}
    private _read_response(res:Response): object {
		let response = res.json();
		if('Result' in response){
			return response.Result;
		}
		return response;
	}

	public make_api_call(url: string, params:object={}): Observable<any>{
		let headers = new Headers();
    	this.createAuthorizationHeader(headers);

    	return this.http.post(this.apiUrlPost+url, params, {headers: headers})
         .map(this._read_response)
         .catch(this._handle_error);
	  };
	
		public downloadFile(urlStr:string, name:string){
			if(name === 'not-available'){
						 alert("Something went wrong please try again");
						 return;
				 }
				 var params = $.param({
								 name : name
				 });

			 const url = urlStr + '/sendfresponse' + '?' + params;
						 if($('#download-frame')){
				 $('#download-frame').attr('src', ' ');
				 $('#download-frame').remove('iframe');
						 }
						 $('body').append('<iframe id="download-frame" style="width:0;height:0;" src="' + url + '"></iframe');
			 setTimeout(function(){
				 $('#download-frame').attr('src', ' ');
				 $('#download-frame').remove('iframe');
			 },10000);
		 }

  	public download(name:string){
     if(name === 'not-available'){
            alert("Something went wrong please try again");
            return;
        }
        var params = $.param({
                name : name
        }),
			url = environment.origin + environment.api  + 'sendfresponse' + '?' + params;
            if($('#download-frame')){
			  $('#download-frame').attr('src', ' ');
        $('#download-frame').remove('iframe');
            }
            $('body').append('<iframe id="download-frame" style="width:0;height:0;" src="' + url + '"></iframe');
      setTimeout(function(){
        $('#download-frame').attr('src', ' ');
        $('#download-frame').remove('iframe');
      },10000);
  	}

	////////////////////////////////////

	createAuthorizationHeader(headers: Headers) {
		var token = this.getToken();
		if(token){
			headers.append('token', token);
		}
		else{
			headers.append('token', 'VydNVBMgLUbnyK3V3VvCPgafmjXPicXklCQpSqXAd3z2g9u3hrGuacHHuonoNHhGmsP6Y76sPF1/1M9UpStJtHRKhOnZj2Kn0KiNwJ1qdN688cToeattfqove0oU/Uxoa4qZpST1EPFP+JrD0hphYWWqzpHGEdtsCyEh2uQe6wvRz2nfAE+leylAb8b4AAV5XQ+ZZFf13yrUU665I6bM+UHol8/wk3xzkkNKJ66qEeBlB4OCewCXO9csmv0C0P1UOitawKsnwJPHeKZ0wi6g/DPAb46WqajlteLh8Oen8OAjILrqsMFwPDR2m5RnpGrPgQVLtyNkimQIC2y09FdwcAn6RnTb30drhzUN9T76cDAq+0Kqr39aKWTGzyLuFo76Tkryg1qFhqBFGq4CEGdTttNROPVz9OlspWL6+4FCJ8YPJwSJy9h45u30+H363hHR6Xu6p3PwrwpUIiI+B5E5bkSEWTPaja67UpYxgGiLCsCLnInI2rr/NUPH+KxVl1ydt7TORqI9wRV1ljJgL+qZEBYqt9ovhQAQlEZIJIc/K6lICzdIlr/qht/g79enqE9s4AqSTIA4sIZTmIMTkAMI+ZQGoqxI72fQrzY1vOnJLI+/yV/+JtdaeBpmTDJCT1NDeu6SgRuUkqPOiY/hFB5Oj0Ip28yGce8csClEMReJLm/4/Kdnug523sWywR+j+ePTcTjT6YVy3Nywtf7l7wRHkDGjP1gXUCFkD0EPVd1h4Qq2BXcGdb+R/+wnvvSH5qrNwuO6FKIQ3vX35KTgNz/nc2nc9e2xMjVh+I+PV1EAYlTUrB/PnAg5gx0Nr5ZdZr091TnBCpe4VvD7qMeQKlppgeA3/WtQD+LnimaYyEZRASxrRGHzNbAV9mJygfbdUI76clwBkaMoKBQuU3PkgkLCH3NI5LGuKgQjxMs+viqhfOI3etC1aRjq1WtOPaaAT8oFkoJbOCkp2+2gjkvf+7Zg+qKhIxXU9IHWaElicSvlVBo8xNv7knqHH5jR0vacgxkOVgQdBsuwA5RNCFMTtjJ8fSOPzVQ11p75ef28KwscnoJV4Ia5CcDGgq1ZS+NnwlXHYGlrUzK5X+9su2KRDiHS2geuvFCLiLp2Rg0jwsKkb8zra/C6MQ+qoBrwHc0ffBbZhamoBukSdQgLPE5bCAAFCsHGThBzt2+btfIuYwP05tazRRqJrezr1D5gD6s/JTlsAX8qCjwFwwzUx7KCPJ6RxoIfWSGNxwLm+QnLqTraiNxkwM3yRW8Oo9ujehTZvSHhPorWTpXhjZjjrENB5i0NLq9Rm/pAE8+cOrVxehudIWbqfxYE5HhiWSwc6l72Ish8HiPXHdZEt2D6keRcRM6q1lKGz1ZnDOoDo4b99ePUKS1Y8Ve7PSnDykd4AlX93ame2zDFl3KBg89lwVNpKaMdXscCSlsVhh64P4QvVNRIYcYr6kzOJmQtC4WVNetLsBT2rlntfp36trLvmOdaJIHlQG9Y5C1YJ59C7Wopt0bxXZ/G0Z0/S6/iHN3/195PcNAPBU7WCsoyBXjGbHjjRGqSJLmQYW60YbMgDh+C8rmF2ujpQJnpdS0mVMnCSR6se2TbcAgXwbBkHPQ7WmNu1h9rifZi99lr5QSCWqpeELRnUiau6UL9rZcL539FkueuxNUQVvOKwYSP1+rVUj8deAWlRgeNvRGz3cb7eSeyjS953RS/X9T0dWyVhgh4VZsmmt7PsQjLOxK4ryG9++60cZ7k8KgKLSKVo/jg4e4zJvTumeZAsUKeq6V8gDzQFIb6udIfj2ZvTnLRVj/JonKmZQwYlQ==');
		}
  }

  getemptyapi(val,context) {
    return this.http.get(this.apiGetUrl,{params:{'input':val,context:context}})
    .map((res: Response) => res.json());
  }

  getapi(url) {
	let headers = new Headers();
    this.createAuthorizationHeader(headers);
    return this.http.get(this.apiUrl+url,{headers: headers})
    .map((res: Response) => res.json());
  }

  postapi(url,params){
	let headers = new Headers();
    this.createAuthorizationHeader(headers);
    return this.http.post(this.apiUrlPost+url,params,{headers: headers})
    .map((res: Response) => res.json());
	}
 
	applyDownload(apiKey,uuid){
		var url = environment.origin + environment.api + apiKey + '?uuid='+uuid+'&fname=Export';
		if($("#download-frame").length == 0) {
			$('body').append('<iframe id="download-frame" style="width:0;height:0;visibility:hidden;display:none;" src="' + url + '"></iframe');
		}else{
				$('#download-frame').attr('src', ' ');
				$('#download-frame').remove('iframe');
				$('body').append('<iframe id="download-frame" style="width:0;height:0;visibility:hidden;display:none;" src="' + url + '"></iframe');
		}
		return true;
	}
	
	getToken(){
    return sessionStorage.getItem('ct_token');
  }
}
