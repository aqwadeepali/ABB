import { Injectable } from '@angular/core';

import {Observable} from 'rxjs/Observable';

import * as $ from 'jquery';
declare let Highcharts: any;
window['Highcharts'] = Highcharts;

import * as _moment from 'moment';
import { Moment } from 'moment';

const moment =  _moment;

@Injectable({
  providedIn: 'root'
})

export class ChartsService {

	public draw_line_chart(options): object{
        var container = $('#' + options.id),
            _w = container.width(),
            _h = container.height();
        var seriesOption = [];

        for(let i=0;i<options.series.length; i++){
        	let obj = options.series[i];
        	obj["turboThreshold"] = 3000;
        	seriesOption.push(obj);
        }

		return new Highcharts.Chart({
			chart: {
				backgroundColor: null,
				renderTo: options.id,
				type: "line",
	            spacingTop: 5,
	            spacingBottom: 5,
	            spacingLeft: 5,
	            spacingRight: 5
			},
			legend:{
				enabled : true,
				align : 'right',
				layout: 'horizontal',
				verticalAlign: 'top',
				borderWidth : 0,
				itemStyle: {
		            color: '#000000',
		            padding:'0.5rem',
		            fontWeight: 'normal',
		            fontSize : '1.25rem',
					fontFamily : 'Roboto,Helvetica Neue,Helvetica'
		        }
			},
			credits : { 'enabled': false },
			exporting : { 'enabled': false },
			title : {
                text : ''
			},
			xAxis: {
				// startOfWeek:0,
				categories:options.categories,
				alignTicks:false,
				tickLength: 0,
				lineWidth: 0.05,
				labels: {
	                overflow: 'justify',
	                style: {
	                    color: '#000000'
	                }
		        },
				title: {
					text: ''
				}
			},
			yAxis: [{
				lineWidth: 0.5,
	            gridLineWidth: 0.5,
	            gridLineDashStyle:"Dot",
	            min:0,
	            gridLineColor:'#808080',
	            reversedStacks: false,
	            opposite:false,
	            labels: {
	                enabled: true,
	                overflow: 'justify',
	                style: {
	                    color: '#000000'
	                }
	            },
	            title: {
	                text: ''
	            },
	            startOnTick: true
			},{
				lineWidth: 0.5,
	            gridLineWidth: 0.5,
	            gridLineDashStyle:"Dot",
	            min:0,
	            opposite:true,
	            gridLineColor:'#808080',
	            reversedStacks: false,
	            labels: {
	                enabled: true,
	                overflow: 'justify',
	                style: {
	                    color: '#000000'
	                }
	            },
	            title: {
	                text: ''
	            },
	            startOnTick: true
			}],
			plotOptions : {
				line : {
					allowPointSelect: false,
					// minSize:100,
                    dataLabels : {
                        enabled : false
                    },
                    marker:{
                    	enabled:false
                    }
				},
				series:{
					turboThreshold: 3000
				}
			},
			tooltip : {
				enabled:true,
				// useHTML : true,
				// style: {
		  //           fontSize : '10px',
				// 	fontFamily : 'Roboto'
		  //       },
    //             shadow : false,
    //             borderRadius : 5,
    //             formatter : function() {
    //             	console.log(this);
    //                 var s = '<span style="color:' + this.point.color + '">\u25CF</span><span class="word-wrap: break-word;">' + this.point.series.name +'</span>';
    //                 s += 'Batch:' +this.point.x + '</span><br/><span class="word-wrap: break-word;"> Cost:'+this.point.options.cost +'</span>'; 
    //                 return s;
    //             }
			},
			series : seriesOption
		});

	}

	public draw_line_chart_2(options): object{
        var container = $('#' + options.id),
            _w = container.width(),
            _h = container.height();
		return new Highcharts.Chart({
			chart: {
				backgroundColor: null,
				renderTo: options.id,
				type: "line",
	            spacingTop: 5,
	            spacingBottom: 5,
	            spacingLeft: 5,
	            spacingRight: 5
			},
			legend:{
				enabled : true,
				align : 'right',
				layout: 'horizontal',
				verticalAlign: 'top',
				borderWidth : 0,
				itemStyle: {
		            color: '#000000',
		            padding:'0.5rem',
		            fontWeight: 'normal',
		            fontSize : '1.25rem',
					fontFamily : 'Roboto,Helvetica Neue,Helvetica'
		        }
			},
			credits : { 'enabled': false },
			exporting : { 'enabled': false },
			title : {
                text : ''
			},
			xAxis: {
				// startOfWeek:0,
				categories:options.categories,
				alignTicks:false,
				tickLength: 0,
				lineWidth: 0.05,
		        type: 'datetime',
		        labels: {
		        	formatter: function(){
		        		var s = this.value.substring(11);
		        		return s;
		        	},
		            rotation: 45,
		            align: 'left',
		            overflow: 'justify',
	                style: {
	                    color: '#000000'
	                }
		        },
				title: {
					text: ''
				}
			},
			yAxis: [{
				lineWidth: 0.5,
	            gridLineWidth: 0.5,
	            gridLineDashStyle:"Dot",
	            // min:0,
	            gridLineColor:'#808080',
	            reversedStacks: false,
	            opposite:false,
	            labels: {
	                enabled: true,
	                overflow: 'justify',
	                style: {
	                    color: '#000000'
	                }
	            },
	            title: {
	                text: ''
	            },
	            startOnTick: true
			},{
				lineWidth: 0.5,
	            gridLineWidth: 0.5,
	            gridLineDashStyle:"Dot",
	            // min:0,
	            opposite:true,
	            gridLineColor:'#808080',
	            reversedStacks: false,
	            labels: {
	                enabled: true,
	                overflow: 'justify',
	                style: {
	                    color: '#000000'
	                }
	            },
	            title: {
	                text: ''
	            },
	            startOnTick: true
			}],
			plotOptions : {
				line : {
					allowPointSelect: false,
					// minSize:100,
                    dataLabels : {
                        enabled : false
                    },
                    marker:{
                    	enabled:false
                    }
				},
				series:{
					turboThreshold: 3000
				}
			},
			tooltip : {
				enabled:true,
				// useHTML : true,
				// style: {
		  //           fontSize : '10px',
				// 	fontFamily : 'Roboto'
		  //       },
    //             shadow : false,
    //             borderRadius : 5,
    //             formatter : function() {
    //             	console.log(this);
    //                 var s = '<span style="color:' + this.point.color + '">\u25CF</span><span class="word-wrap: break-word;">' + this.point.series.name +'</span>';
    //                 s += 'Batch:' +this.point.x + '</span><br/><span class="word-wrap: break-word;"> Cost:'+this.point.options.cost +'</span>'; 
    //                 return s;
    //             }
			},
			series : options.series
		});

	}

	public draw_column_chart(options): object{
        var container = $('#' + options.id),
            _w = container.width(),
            _h = container.height();
		return new Highcharts.Chart({
			chart: {
				backgroundColor: null,
				renderTo: options.id,
				type: "column",
	            spacingTop: 5,
	            spacingBottom: 5,
	            spacingLeft: 5,
	            spacingRight: 5
			},
			legend:{
				enabled : true,
				align : 'right',
				layout: 'horizontal',
				verticalAlign: 'top',
				borderWidth : 0,
				itemStyle: {
		            color: '#000000',
		            padding:'0.5rem',
		            fontWeight: 'normal',
		            fontSize : '1.25rem',
					fontFamily : 'Roboto,Helvetica Neue,Helvetica'
		        }
			},
			credits : { 'enabled': false },
			exporting : { 'enabled': false },
			title : {
                text : ''
			},
			xAxis: {
				// startOfWeek:0,
				categories:options.categories,
				alignTicks:false,
				tickLength: 0,
				lineWidth: 0.05,
		        // type: 'datetime',
		        // labels: {
		        // 	formatter: function(){
		        // 		var s = this.value.substring(11);
		        // 		return s;
		        // 	},
		        //     rotation: 45,
		        //     align: 'left',
		        //     overflow: 'justify',
	         //        style: {
	         //            color: '#000000'
	         //        }
		        // },
				title: {
					text: ''
				}
			},
			yAxis: [{
				lineWidth: 0.5,
	            gridLineWidth: 0.5,
	            gridLineDashStyle:"Dot",
	            min:0,
	            gridLineColor:'#808080',
	            reversedStacks: false,
	            opposite:false,
	            labels: {
	                enabled: true,
	                overflow: 'justify',
	                style: {
	                    color: '#000000'
	                }
	            },
	            title: {
	                text: ''
	            },
	            startOnTick: true
			},{
				lineWidth: 0.5,
	            gridLineWidth: 0.5,
	            gridLineDashStyle:"Dot",
	            min:0,
	            opposite:true,
	            gridLineColor:'#808080',
	            reversedStacks: false,
	            labels: {
	                enabled: true,
	                overflow: 'justify',
	                style: {
	                    color: '#000000'
	                }
	            },
	            title: {
	                text: ''
	            },
	            startOnTick: true
			}],
			plotOptions : {
				column : {
					allowPointSelect: false,
					// minSize:100,
                    dataLabels : {
                        enabled : false
                    },
                    marker:{
                    	enabled:false
                    }
				},
				series:{
					turboThreshold: 3000
				}
			},
			tooltip : {
				enabled:true
			},
			series : options.series
		});

	}

	public draw_pie_with_single_title(options): object{
        var container = $('#' + options.id),
            _w = container.width(),
            _h = container.height();
		return new Highcharts.Chart({
			chart: {
				backgroundColor: null,
				renderTo: options.id,
				type: "pie",
				margin: [0, 0, 0, 0],
	            spacingTop: 0,
	            spacingBottom: 0,
	            spacingLeft: 0,
	            spacingRight: 0,
                events: {
                    load: function () {
                        if (_h < 50)
                            return
                        var chart = this,
                            rend = chart.renderer;
                        rend.text(options.title, chart.chartWidth / 2, chart.chartHeight / 2 - 8)
                            .attr({ 'fill': '#000000', 'text-anchor': 'middle', 'font-size': '9px' })
                            .add();
                        rend.text(options.subtitle, chart.chartWidth / 2, chart.chartHeight / 2 + 8)
                            .attr({ 'fill': '#000000', 'text-anchor': 'middle', 'font-size': '13px' })
                            .add();
                    }
                }
			},
			noData: {},
			legend:{
				enabled : false,
                // itemMarginBottom:8,
				margin:45,
				// padding:8,
				align: 'right',
        		verticalAlign: 'middle',
        		layout: 'vertical',
        		itemDistance: 8,
				symbolHeight: 8,
				symbolWidth: 8,
				// symbolHeight: 15,
		        // symbolWidth: 15,
				symbolRadius: 2,
				itemStyle: {
		            color: '#444',
		            fontWeight: 'normal',
		            fontSize : '10px',
					fontFamily : 'Roboto'
		        }
			},
			credits : { 'enabled': false },
			exporting : { 'enabled': false },
			title : {
                text : ''
				// useHTML: true,
		  //       text : '<div class="text-reading text-center" style="font-weight:normal">Alerts <div class="text-center" style="font-weight:bold;color:#7f7f7f;">' + options.title + '</div></div>',
		  //       align : 'center',
		  //       verticalAlign : 'middle',
		  //       y : -18
			},
			plotOptions : {
				pie : {
					allowPointSelect: false,
					// minSize:100,
                    dataLabels : {
                        enabled : false,
                        connectorPadding:2,
                        distance: 3,
                        formatter: function(){
                        	return this.y;
                        }
                    },
                    size : '100%',
                    innerSize : '90%',
                    // borderWidth : 0,
					showInLegend : true,
				},
				series : {
                    states : {
                        hover : {
                            halo : {
                                size : 2,
                            },
                            lineWidth : 1
                        }
                    }
                }
			},
			tooltip : {
				enabled:true,
				useHTML : true,
				style: {
		            fontSize : '10px',
					fontFamily : 'Roboto'
		        },
                shadow : false,
                borderRadius : 5,
                formatter : function() {
                    var s = '<span style="color:' + this.point.color + '">\u25CF</span><span class="word-wrap: break-word;">' + this.point.name +'</span>';
                    // s += 'Qty:' +this.point.options.qty + '</span><br/><span class="word-wrap: break-word;"> Cost:'+this.point.options.cost +'</span>'; 
                    return s;
                }
			},
			series : options.series
		});

	}

	public draw_pie_with_title(options): object{
        var container = $('#' + options.id),
            _w = container.width(),
            _h = container.height();
		return new Highcharts.Chart({
			chart: {
				backgroundColor: null,
				renderTo: options.id,
				type: "pie",
				margin: [0, 0, 0, 0],
	            spacingTop: 0,
	            spacingBottom: 0,
	            spacingLeft: 0,
	            spacingRight: 0,
                events: {
                    load: function () {
                        if (_h < 50)
                            return
                        var chart = this,
                            rend = chart.renderer;
                        rend.text('Action', chart.chartWidth / 2, chart.chartHeight / 2 - 8)
                            .attr({ 'fill': '#000000', 'text-anchor': 'middle', 'font-size': '10px' })
                            .add();
                        rend.text(options.title, chart.chartWidth / 2, chart.chartHeight / 2 + 8)
                            .attr({ 'fill': '#000000', 'text-anchor': 'middle', 'font-size': '13px' })
                            .add();
                    }
                }
			},
			noData: {},
			legend:{
				enabled : false,
                // itemMarginBottom:8,
				margin:45,
				// padding:8,
				align: 'right',
        		verticalAlign: 'middle',
        		layout: 'vertical',
        		itemDistance: 8,
				symbolHeight: 8,
				symbolWidth: 8,
				// symbolHeight: 15,
		        // symbolWidth: 15,
				symbolRadius: 2,
				itemStyle: {
		            color: '#444',
		            fontWeight: 'normal',
		            fontSize : '10px',
					fontFamily : 'Roboto'
		        }
			},
			credits : { 'enabled': false },
			exporting : { 'enabled': false },
			title : {
                text : ''
				// useHTML: true,
		  //       text : '<div class="text-reading text-center" style="font-weight:normal">Alerts <div class="text-center" style="font-weight:bold;color:#7f7f7f;">' + options.title + '</div></div>',
		  //       align : 'center',
		  //       verticalAlign : 'middle',
		  //       y : -18
			},
			plotOptions : {
				pie : {
					allowPointSelect: false,
					// minSize:100,
                    dataLabels : {
                        enabled : false,
                        connectorPadding:2,
                        distance: 3,
                        formatter: function(){
                   //      	console.log(this);
                   //      	if(this.point.name === "Not Available"){
		                	// 	var s = '<span style="color:' + this.point.color + '">\u25CF</span><span class="word-wrap: break-word;">' + this.point.name + '</span>';	
		                	// }
		                	// else{
		                	// 	var s = '<span style="color:' + this.point.color + '">\u25CF</span><span class="word-wrap: break-word;">' + this.point.name + ':' + this.point.y + '</span>';	
		                	// }
		                    
		                 //    s += '<br>Qty:' +this.point.options.qty + '</span><br/><span class="word-wrap: break-word;"> Cost:'+this.point.options.cost +'</span>'; 
		                 //    return s;
                        	return this.y;
                        }
                    },
                    size : '100%',
                    innerSize : '85%',
                    // borderWidth : 0,
					showInLegend : true,
				},
				series : {
                    states : {
                        hover : {
                            halo : {
                                size : 2,
                            },
                            lineWidth : 1
                        }
                    }
                }
			},
			tooltip : {
				enabled:true,
				useHTML : true,
				style: {
		            fontSize : '10px',
					fontFamily : 'Roboto'
		        },
                shadow : false,
                borderRadius : 5,
                formatter : function() {
                	if(this.point.name === "Not Available"){
                		var s = '<span style="color:' + this.point.color + '">\u25CF</span><span class="word-wrap: break-word;">' + this.point.name + '</span>';	
                	}
                	else{
                		var s = '<span style="color:' + this.point.color + '">\u25CF</span><span class="word-wrap: break-word;">' + this.point.name + ':' + this.point.y + '</span>';	
                	}
                    
                    // s += '<br>Qty:' +this.point.options.qty + '</span><br/><span class="word-wrap: break-word;"> Cost:'+this.point.options.cost +'</span>'; 
                    return s;
                }
			},
			series : options.series
		});

	}

	public draw_stock_chart(options):object{

		return	new Highcharts.StockChart({
			chart: {
				alignTicks: false,
				spacing: [5,0,0,0],
				reflow: true,
				backgroundColor : null,
				renderTo : options.id
			},
			credits : options.credits,
			exporting : options.exporting,
			//title : options.title,
			legend : {
				enabled : true,
				align : 'right',
				layout: 'vertical',
				margin: 50,
				symbolRadius: 6,
				symbolHeight: 10,
    			symbolWidth: 10,
				verticalAlign: 'top',
				borderWidth : 0,
				itemStyle: {
		            color: '#000000',
		            padding:'0.5rem',
		            fontWeight: 'normal',
		            fontSize : '1rem',
					fontFamily : 'Roboto,Helvetica Neue,Helvetica'
		        }
			},

			rangeSelector : {
				enabled:false,
			},

			scrollbar:{
				minWidth:2,
				height:1,
				liveRedraw:true,
				enabled:true
			},
			navigator: {
				baseSeries: 0,
				height: 15,
				// margin: 10,
				maskInside: true,
				maskFill: 'rgba(100, 100, 100, 0.12)',
				outlineWidth: 0,
				xAxis: {
					lineWidth: 0,
					gridLineWidth: 0,
					opposite: true,
					labels: {
						enabled:false,
					}
				},
				series: {
					type: 'areaspline',
					color: null,
					lineColor: null,
					fillOpacity: 0,
					labels:{
						style: {
						color: '#666'
					}
				},
				dataGrouping: {
					enabled: false,
				},
				lineWidth: 0,
					marker: {
						enabled: false
					}
				}
			},
			xAxis: {
				// startOfWeek:0,
				tickLength: 0,
		        startOnTick: true,
				lineWidth: 0.05,
				labels: {
	                enabled: true,
	                overflow: 'justify',
	                style: {
	                    color: '#666'
	                },
	                format: '{value:%m-%Y}',
		            align: 'left'
		        },
				title: {
					text: ''
				},
				plotLines:[{
		            width: 2,
		            value: options.current_dts_week,
		            color : '#005493',
	                dashStyle : 'shortdash',
	                label : {
	                	enabled:true,
	                    style: {
	                        color: '#005493',
	                        fontFamily: 'Roboto,Helvetica Neue,Helvetica',
	                        fontSize: '1.6em'
	                    },
	                    text : 'Today',
		                verticalAlign: 'middle',
		                textAlign: 'right',
		                x: -135
	                }
	            }]
			},
			//    time:{
			// 		// timezone: 'GMT +5:30',
			// 		useUTC:false
			//    },

			plotOptions:{

				area: {
	                allowPointSelect : false,
	                marker: {
	                    enabled:false,
	                    radius:4
	                },
	                fillOpacity: 0.3,
	                dataGrouping:{
	                    enabled: false
	                }
	            },
	            line: {
	                marker: {
	                    enabled:true,
	                    radius:3
	                },
	                fillOpacity: 0.3,
	                dataGrouping:{
	                    enabled: false
	                }
	            },
	            series:{
	            	showInNavigator: true,
	            	dataGrouping:{
	            		enabled : false
	            	}
	            }
			},
			yAxis: {
				lineWidth: 0.5,
	            gridLineWidth: 0.5,
	            gridLineDashStyle:"Dot",
	            min:0,
	            gridLineColor:'#808080',
	            reversedStacks: false,
	            opposite:false,
	            labels: {
	                enabled: true,
	                overflow: 'justify',
	                style: {
	                    color: '#666'
	                }
	            },
	            title: {
	                text: ''
	            },
	            startOnTick: true
			},
		   	tooltip: {
			   	useHTML: true,
	            valueDecimals: 2,
	            formatter:function(){
	                var s = '<b>'+ moment(this.x).format('YYYY-MM-DD') +'</b><br/>';
	                $.each(this.points, function(i, point) {
	                    s += '<span style="color:' + point.series.color + '">\u25CF</span> ' + point.series.name + ': <b>' + (point.y).toFixed(2) + '</b><br/>';
	                });
	                return s;
	            },
	            xDateFormat: '%Y-%m-%d'
		   	},
		   	labels: {
			   	enabled: false,
		   	},
		   	series: options.series
	   	});
	}

	private _y_axes(object) {
		var yaxes = [],
			charttype = object.charttype;
		function getAxis(options={}){
			let axes:any = {
				gridLineWidth: 0,
				min: 0,
				startOnTick: true,
				endOnTick: true,
				opposite: false,
				labels: {
					enabled: true,
					useHTML: true,
					formatter: function(){
						if(this.value >= 500 && this.value < 100000){
							return (Math.round(this.value/100)/10)+ 'k';
						}
						else if(this.value >= 100000){
							return (Math.round(this.value/100000)/10)+ 'm';
						}
						return this.value;
					},
					style: {
						fontSize: '10px',
						color: '#424243'
					}
				},
				title: {
					text: ''
				}
			}
			for(let key in axes){
				if(key in options){
					axes[key] = options[key];
				}
			}
			return axes;
		}
		if(object['yAxis']){
			return [
				getAxis(), 
				getAxis({
					labels: {
						enabled: false
					}
				})
			];
		}
		if(object['yAxes']){
			return object['yAxes'].map(d => getAxis(d));
		}
		return [getAxis()];
	}
	private _plot_options(object): object {
		if(object.plotOptions){
			return object.plotOptions;
		}
		else{
			var plotoptions: any = {
				series: {
					marker: {
						enabled: false
					},
					borderColor: null,
					stacking: 'normal'
				}
			};
			switch (object.charttype) {
				case 'bar':
					plotoptions.bar = {
						dataLabels: {
							enabled: true
						}
					};
					break;
				case 'column':
					plotoptions.column = {
						minPointLength: 1,
						dataLabels: {
							allowOverlap: true,
							enabled: true,
							style: {
								fontSize: '10px',
								color: '#424243'
							},
							formatter: function () {
								return Math.round(this.y * 10) / 10 + object.suffix;
							}
						}
					};
					break;
			}
			return plotoptions;

		}
		
	}
	private _base_chart(options): object {
		var xAxis = {};
		var yAxis = {};
		if(options.xAxis){
			xAxis = options.xAxis;
		}
		else{
			 xAxis = {
				categories: options.categories,
				tickLength: 0,
				labels: {
					enabled: true,
					useHTML: true,
					style: {
						fontSize: options.fontSize ? options.fontSize : '10px',
						color: '#888888'
					},
					// rotation: 0,
					step: options.step ? options.step : 1
				}
			};
		}

		if(options.yAxis){
			yAxis = options.yAxis
		}
		else{
			yAxis = this._y_axes(options);
		}
		var chart = {
			chart: {
				backgroundColor: null,
				type: options.chartType ? options.chartType : 'line',
				renderTo: options.id,
				spacing: [5, 0, 5, 0],
				defaultSeriesType: 'areaspline'
			},
			legend: {
				enabled: options.islegend,
				itemStyle: {
					color: '#444444',
					fontWeight: 'normal',
					fontSize: '12px'
				},
				symbolHeight: 12,
   				symbolWidth: 12,
   				symbolRadius: 6,
				reversed: true,
				layout: 'horizontal'
			},
			credits: {
				enabled: false
			},
		    colors: ['#3bc9db','#69b764','#ffdd71','#f21a1a'],
			exporting: {
				enabled: false
			},
			title: {
				text: ''
			},
			noData: {},
			xAxis: xAxis,
			yAxis: yAxis,
			plotOptions: this._plot_options(options),
			series: options.series
		};
		chart['boost'] = {
			seriesThreshold: 10
		}
		if(options.tooltip){
			chart['tooltip'] = options.tooltip;
		}
		if(options.legend){
			chart['legend'] = options.legend;
		}
		if (options.height) {
			chart['chart']['height'] = options.height;
		}
		return chart
	}
	public gauge(options): object {
		var container = $('#' + options.id),
			_w = container.width(),
			_h = container.height(),
			_size = _h * 1.5 < _w ? _h * 1.5 : _w;
		return new Highcharts.Chart({
			chart: {
				type: 'gauge',
				backgroundColor: null,
				plotBackgroundColor: null,
				plotBackgroundImage: null,
				spacing: [5, 0, 0, 0],
				margin: [0, 0, 0, 0],
				renderTo: options.id,
				events: {
					load: function () {
						if (_h < 50)
							return
						var riskText = 'LOW', riskColor = '';
						var chart = this,
							rend = chart.renderer;
						rend.text(options.series[0].data[0], chart.chartWidth / 2, chart.chartHeight / 2)
							.attr({ 'fill': riskColor, 'text-anchor': 'middle', 'font-size': '24px' })
							.add();
					}
				}
			},
			credits: {
				enabled: false
			},
			title: {
				text: ''
			},
			exporting: {
				enabled: false
			},
			tooltip: {
				enabled: false
			},
			plotOptions: {
				gauge: {
					// borderWidth: 0,
					dataLabels: {
						enabled: false
					},
					dial: {
						radius: '107%',
						backgroundColor: '#444444',
						borderWidth: 0,
						baseWidth: 8,
						topWidth: 2,
						baseLength: '0%',
						// rareLength: '2%'
					},
					pivot: {
						radius: 0
					}
				}
			},
			pane: {
				startAngle: -100,
				endAngle: 100,
				center: ['50%', '80%'],
				size: _size,
				// borderWidth: 0,
				background: [{
					borderWidth: 0,
					backgroundColor: 'transparent'
				}]
			},

			// the value axis
			yAxis: {
				min: 0,
				max: 100,
				minorTickWidth: 0,
				minorTickLength: 0,
				tickWidth: 0,
				tickLength: 0,
				lineWidth: 0,
				labels: {
					enabled: false
				},
				title: {
					text: ''
				},
				plotBands: [{
					from: 0,
					to: 10,
					thickness: 10,
					borderColor: null,
					color: '#00ff00'
				}, {
					from: 11,
					to: 20,
					thickness: 10,
					borderColor: null,
					color: {
						linearGradient: { x1: 0, y1: 0, x2: 1, y2: 0 },
						stops: [
							[0, '#2bff00'],
							[1, '#00ff00']
						]
					}
				}, {
					from: 21,
					to: 30,
					thickness: 10,
					color: {
						linearGradient: { x1: 0, y1: 0, x2: 1, y2: 0 },
						stops: [
							[0, '#55ff00'],
							[1, '#2bff00']
						]
					}
				}, {
					from: 31,
					to: 40,
					thickness: 10,
					color: {
						linearGradient: { x1: 0, y1: 0, x2: 1, y2: 0 },
						stops: [
							[0, '#56ff00'],
							[1, '#e6ff00']
						]
					}
				}, {
					from: 41,
					to: 50,
					thickness: 10,
					color: {
						linearGradient: { x1: 0, y1: 0, x2: 1, y2: 0 },
						stops: [
							[0, '#ffff00'],
							[1, '#eaff00']
						]
					}
				}, {
					from: 51,
					to: 60,
					thickness: 10,
					color: '#ffff00'
				}, {
					from: 61,
					to: 70,
					thickness: 10,
					color: {
						linearGradient: { x1: 0, y1: 0, x2: 1, y2: 0 },
						stops: [
							[0, '#ffff00'],
							[0.25, '#ffee00'],
							[0.5, '#ffdd00'],
							[0.75, '#ffcc00'],
							[1, '#ffc200']
						]
					}
				}, {
					from: 71,
					to: 80,
					thickness: 10,
					color: {
						linearGradient: { x1: 0, y1: 0, x2: 1, y2: 1 },
						stops: [
							[0, '#ff7100'],
							[0.3, '#ff5200'],
							[0.75, '#ff6200'],
							[1, '#ff4200']
						]
					}
				}, {
					from: 81,
					to: 90,
					thickness: 10,
					color: {
						linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
						stops: [
							[0, '#ee2900'],
							[1, '#e61e00']
						]
					}
				}, {
					from: 91,
					to: 100,
					thickness: 10,
					color: {
						linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
						stops: [
							[0, '#e61e00'],
							[1, '#d90e00']
						]
					}
				}]
			},
			series: options.series
		});
	};
	public get_pie_chart(options): object {
		var container = $('#' + options.id),
			_w = container.width(),
			_h = container.height();
		return new Highcharts.Chart({
			chart: {
				plotBackgroundColor: null,
				plotBorderWidth: null,
				plotShadow: false,
				spacing: [0, 0, 0, 0],
				padding: [0, 0, 0, 0],
				margin: [0, 0, 0, 0],
				type: 'pie',
				renderTo: options.id,
				events: {
					load: function () {
						if (_h < 50)
							return
						var chart = this,
							rend = chart.renderer;
						rend.text('Total', chart.chartWidth / 2, chart.chartHeight / 2 - 30)
							.attr({ 'fill': '#484746', 'text-anchor': 'middle', 'font-size': '13px' })
							.add();
						rend.text(Math.round(options.total) + 'kWh', chart.chartWidth / 2, chart.chartHeight / 2)
							.attr({ 'fill': '#484746', 'text-anchor': 'middle', 'font-size': '24px' })
							.add();
					}
				}
			},
			title: { text: '' },
			tooltip: {
				pointFormat: '{series.name}: <b>{point.percentage:.1f}% |{point.y:.1f}kWh</b>'
			},
			credits: { enabled: false },
			legend: { enabled: false },
			plotOptions: {
				pie: {
					allowPointSelect: true,
					cursor: 'pointer',
					dataLabels: {
						enabled: false
					},
					showInLegend: true
				}
			},
			series: options.series
		});
	}

	public get_speed(options): object {
		return new Highcharts.Chart({
			chart: {
				type: 'gauge',
				plotBackgroundColor: null,
				plotBackgroundImage: null,
				plotBorderWidth: 0,
				plotShadow: false,
				spacing: [0, 0, 0, 0],
				padding: [0, 0, 0, 0],
				margin: [0, 0, 0, 0],
				renderTo: options.id
			},
			title: { text: '' },
			credits: { enabled: false },
			plotOptions: {
				gauge: {
					dataLabels: {
						enabled: true
					}
				}
			},
			pane: {
				startAngle: -150,
				endAngle: 150,
				background: [{
					borderWidth: 0,
					backgroundColor: '#fff'
				}]
			},

			// the value axis
			yAxis: {
				min: options.min,
				max: options.max,

				minorTickInterval: 'auto',
				minorTickWidth: 0,
				minorTickLength: 4,
				minorTickPosition: 'inside',
				minorTickColor: '#666',

				tickPixelInterval: 30,
				tickWidth: 0,
				tickPosition: 'inside',
				tickLength: 0,
				tickColor: '#666',
				labels: {
					step: 2,
					distance: -16,
					rotation: 'auto'
				},
				title: {
					y: 20,
					text: options.title,
					style: {
						color: options.color,
						fontSize: '16px'
					}
				},
				plotBands: [{
					thickness: 4,
					from: options.min,
					to: options.max / 3,
					color: '#55BF3B' // green
				}, {
					thickness: 4,
					from: options.max / 3,
					to: 2 * (options.max / 3),
					color: '#DDDF0D' // yellow
				}, {
					thickness: 4,
					from: 2 * (options.max / 3),
					to: options.max,
					color: '#DF5353' // red
				}]
			},
			series: options.series
		});
	}

	
	private _base_platform_chart(options): object {
		let cLen = options['categories'].length;
		let scroll = cLen > 5;
		let max = scroll ? 4 : cLen-1;
		var xAxis = {
			scopeQ: this,
			categories: options.categories,
			tickLength: 0,
			min: 0,
			max: max,
			scrollbar: {
				enabled: scroll
			},
			labels: {
				enabled: true,
				useHTML: true,
				style: {
					'fontSize': options.fontSize ? options.fontSize : '1.2rem',
					'cursor': 'pointer',
					'textDecoration': 'underline',
					'fontWeight': 'bold',
					'color': '#0288cc'
				},
				// rotation: 0,
				step: options.step ? options.step : 1,
				formatter: function () {
					if(this.value.length > 12){
						return '<div title="Click to Filter">'+this.value.substr(0, 10)+'...</div>';
					}					
					return '<div title="Click to Filter">'+this.value+'</div>';
				}
                
			}
		};

		var chart = {
			chart: {
				backgroundColor: null,
				type: options.chartType ? options.chartType : 'line',
				renderTo: options.id,
				spacing: [10, 0, 0, 0]
			},
			legend: {
				enabled: options.legend,
				itemStyle: {
					color: '#222',
					fontWeight: 'normal',
					fontSize: '12px'
				}
			},
			credits: {
				enabled: false
			},
			exporting: {
				enabled: false
			},
			title: {
				text: ''
			},
			tooltip: {
				shared: true,
				useHTML: true,
				shadow: false,
				borderWidth: 1,
				backgroundColor: 'rgba(255, 255, 255, 1)',
				formatter: function(){
					var tip = '';
					var me = this;
					tip += '<div class="text-medium border-bottom padding-quarter">' + this.x + '</div>';
					this.points.forEach(d => {
						var suffix = options.percentaxes ? '%' : '',
						_name = d.x,
						_color = d.series.color;
						if(_color == 'rgba(200,200,200,0.2)')
						_color = '#444';
						let val = (Math.round(d.y * 100) / 100).toLocaleString() + suffix;
						tip += '<div class="text-reading-small" style="font-size:12px;color:' + _color + ';padding:2px;">' + d.series.name + '</span>: <b>' + val + '</b></div>';
					});
					return tip; 
				}
			},
			noData: {},
			xAxis: xAxis,
			yAxis: options['yAxis'] ? options['yAxis'] : this._y_axes(options),
			plotOptions: {
				series: {
					marker: {
						enabled: false
					},
					bar: {
						dataLabels: {
							enabled: false
						}
					},
					pointWidth: 25
				},
			},
			series: options.series
		};
		if (options.height) {
			chart['chart']['height'] = options.height;
		}

		return chart
	}

	public get_chart(options): object {
		return new Highcharts.Chart(this._base_chart(options));
	}

	public get_platform_chart(options): object {
		return new Highcharts.Chart(this._base_platform_chart(options));
	}

	public draw_stacked_bar(options): object {
		var filterObj = {};
		return Highcharts.chart('function_id', {
			colors:['#33E0FF','#07B8D8','#04869E'],
			chart: {
				height: 200,
			  type: 'bar',
			  backgroundColor:'rgba(255, 255, 255, 0.0)'
			},
			title: {
			  text: ''
			},
			credits: {
				enabled: false
			},
			xAxis: {
			  categories: options['categories'],
				scopeQ: this,
				gridLineWidth: 0,
              minorGridLineWidth: 0,
			},
			yAxis: {
			  min: 0,
			  max:options['total'],
			  visible:false,
			  gridLineWidth: 0,
              minorGridLineWidth: 0,
			  title: {
				text: 'Function'
			  }
			},
			legend: {
			  reversed: true
			},
			plotOptions: {
			  	series: {
				stacking: 'normal',
				pointWidth: 30,
				cursor: 'pointer',
				dataLabels: {
					enabled: true,
					style: {
						textShadow: false,
						textOutline: false 
					}
				},
				bar: {

					}
	  			}
			  
			},
			series: options['series']
			

		  });
		
	}
	public draw_stacked_bar_wo_axis(options): object {
		return Highcharts.chart('criticality_id', {
			chart: {
				height: 200,
			  type: 'bar',
			  backgroundColor:'rgba(255, 255, 255, 0.0)'
			},
			title: {
			  text: ''
			},
			credits: {
				enabled: false
			},
			xAxis: {
			  categories: options['categories'],
			  scopeQ: this,
			  gridLineWidth: 0,
              minorGridLineWidth: 0,
			},
			yAxis: {
			  min: 0,
			  max:options['total'],
			  gridLineWidth: 0,
			  visible:false,
             minorGridLineWidth: 0,
			  title: {
				text: 'Criticality'
			  }
			},
			legend: {
			  reversed: true
			},
			plotOptions: {
			  series: {
				stacking: 'normal',
				pointWidth:30,
				cursor: 'pointer',
				dataLabels: {
					enabled: true,
					style: {
						textShadow: false,
						textOutline: false 
					}
				},
			   bar: {
				},
			},
		},
			series: options['series']
			

		  });

	}
	public draw_stacked_bar2(options): object {
		var filterObj = {};
		return Highcharts.chart('performance_id', {
			colors:['#c1cdc1','#8fbc8f','#20b2aa'],
			chart: {
				height: 200,
			  type: 'bar',
			  backgroundColor:'rgba(255, 255, 255, 0.0)',
			},
			title: {
			  text: ''
			},
			credits: {
				enabled: false
			},
			xAxis: {
			  categories: options['categories'],
				scopeQ: this,
				gridLineWidth: 0,
              minorGridLineWidth: 0,
				stackLabels:{
					style: {
						color: 'black'
					},
					enabled: true
				},
			},
			yAxis: {
			//   min: 0,
			//   max:options['total'],
			  visible:false,
			  gridLineWidth: 0,
              minorGridLineWidth: 0,
			  title: {
				text: 'Progress'
			  },
			  
			},
			labels: {
                enabled: false
            },
			legend: {
			  reversed: true
			},
			plotOptions: {
			  series: {
				stacking: 'normal',
				pointWidth: 30,
				cursor: 'pointer',
				dataLabels: {
					enabled: true,
					style: {
						textShadow: false,
						textOutline: false 
					},
					
				},
				
			   bar: {
				
	  			}
			  },
			  
			},
			series: options['series']
			

		  });

		}


	constructor() { }
}


// Highcharts.setOptions({
// 	lang: {
// 		thousandsSep: ',',
// 		noData: 'Data not available for this section'
// 	}
// });
