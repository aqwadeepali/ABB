import { Component, OnInit } from '@angular/core';
import { UtilService } from '../shared/service/utils.service';
import { ApiService } from '../shared/service/api.service';
import { ChartsService } from '../shared/service/charts.service';
import { forkJoin } from "rxjs/observable/forkJoin";
import { DomSanitizer } from '@angular/platform-browser';

// import * as jsPDF from 'jspdf';
// import * as html2canvas from 'html2canvas';
import { saveAs } from 'file-saver/dist/FileSaver';
import { FormControl } from '@angular/forms';

import { MenuItem} from 'primeng/api';

import * as _moment from 'moment';
import { Moment } from 'moment';
import { MomentDateAdapter, MatMomentDateModule } from '@angular/material-moment-adapter';
import { DateAdapter, MAT_DATE_FORMATS, MAT_DATE_LOCALE } from '@angular/material/core';

const moment =  _moment;
export const MY_FORMATS = {
  parse: {
    dateInput: 'YYYY-MM-DD',
  },
  display: {
    dateInput: 'YYYY-MM-DD',
    monthYearLabel: 'MMMM YYYY',
    dateA11yLabel: 'DD/MM/YYYY',
    monthYearA11yLabel: 'MMMM YYYY',
  },
};


@Component({
  selector: 'app-overview',
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.scss'],
  providers: [
    // { provide: MAT_MOMENT_DATE_ADAPTER_OPTIONS, useValue: { useUtc: true } }
    {provide: DateAdapter, useClass: MomentDateAdapter, deps: [MAT_DATE_LOCALE] },
    {provide: MAT_DATE_FORMATS, useValue: MY_FORMATS}
  ],
})

export class OverviewComponent implements OnInit {

    public mask:boolean = false;
    public ignoreInPDF:boolean = false;
	public sideBarVisibility:boolean = false;
	public todayDate: Date = null;
	public fromDate:FormControl;
    public toDate:FormControl;
    public yesterDayString: String = null;
    public toDayString:String = "";
	public datePickerDate;
    public disableDownload:Boolean = true;

    public summaryKeys:Array<String> = [];
    public reportKeys: Array<Object> = [];
    public recipeKey: string = "1";
    public reportMaxHeight: number = 0;
    public menuItems: MenuItem[];
    public activeMenuItem: MenuItem;
    public selected_tab:String = "Overview";
    public summaryPanel:Array<Object> = [];
    public moulderSummaryPanel: Array<Object> = [];
    public cmsSummaryPanel: Array<Object> = [];
    public wtWeightSummaryPanel: Array<Object> = [];
    public packingSummaryPanel: Array<Object> = [];
    public lossesSummaryPanel: Array<Object> = [];
    public ovenSummaryPanel: Array<Object> = [];
    public ovenAvergaePanel: Array<Object> = [];
    public ovenBakingChart: Object = {};
    public summaryPanelAvailable: boolean = true;
    public hideTrendChart: boolean = false;
    public reportPanelAvailable: boolean = true;
    public reports:Array<Object> = [];
    public moulder_reports:Array<Object> = [];
    public moulder_headers:Array<Object> = [];
    public moulder_keyheaders:Array<Object> = [];
    public moulder_gridheaders:Array<Object> = [];
    public moulder_downtime_reports: Array<Object> = [];
    public cms_reports: Array<Object> = [];
    public wt_weight_reports: Array<Object> = [];
    public wt_weight_sample_reports:Array<Object> = [];
    public packing_reports:Array<Object> = [];
    public losses_reports:Array<Object> = [];
    public oven_reports:Array<Object> = [];
    public bori_reports:Array<Object> = [];
    public boriFooter:any;
    public boriColumns:Array<Object> = [];
    public downFooter: Array<Object> = [];
    public downFooterDuration: Array<Object> = [];
    public title: String = "";
    public subtitle: String = "";
    public selected_tile: String = "";

    public overviewVisible: Boolean = true;
    public reportVisible: Boolean = false;
    public columns:Array<Object> = [];
    public downTimeColumns:Array<Object> = [];
    public cmsReportColumns:Array<Object> = [];
    public wtWeightReportColumns:Array<Object> = [];
    public wtWeightSampleReportColumns:Array<Object> = [];
    public packingReportColumns:Array<Object> = [];
    public lossesReportColumns:Array<Object> = [];
    public cbbReportColumns:Array<Object> = [];
    public isTodayDate: boolean = false;
    public iswtWeight:boolean = false;
    public isSampleWeight: boolean = false;

    private saveTimeout:any;
    private tileToShow:Array<string> = [];
    private lastElement:string = "";

    public all_dashboards: Array<Object> = [];
    public mixings: Array<Object> = [];
    public all_mixings: Array<Object> = [];
    public selectedMixing: Array<Object> = [];
    public selectAllMixing: boolean = true;
    public searchMixing: string;


  	constructor(
    		private utilService: UtilService,
    		private apiService: ApiService,
    		private chartService: ChartsService,
            private sanitizer: DomSanitizer
    	) { 
                window.scrollTo(0, 0);

  	}  

  	ngOnInit() {
  		// let dateTime = "2019-03-29 20:01:00"; 
        // this.callAllDashboards();
        
        this.saveTimeout = "7:3";
        this.read_settings();
        let dateTime = new Date();
		this.todayDate = new Date(moment(dateTime.toString()).format("YYYY-MM-DD HH:MM:SS"));
        let yesterdayDateTime:Moment = moment(this.todayDate, 'YYYY-MM-DD').subtract(1, 'days');//moment().subtract(1, 'day');
        let todayTimeHr = this.todayDate.getHours();
        if(todayTimeHr < 7){
            yesterdayDateTime = moment(this.todayDate, 'YYYY-MM-DD').subtract(2, 'days');//moment().subtract(1, 'day');
        }
		
		this.fromDate = new FormControl();
        this.yesterDayString = moment(yesterdayDateTime.toString()).format("YYYY-MM-DD");
        this.fromDate.setValue(moment(yesterdayDateTime.toString()).format("YYYY-MM-DD"));

        this.toDate = new FormControl();
        this.toDayString = moment(yesterdayDateTime.toString()).format("YYYY-MM-DD");
        this.toDate.setValue(moment(yesterdayDateTime.toString()).format("YYYY-MM-DD"));

		this.toDayString = moment(dateTime).format("YYYY-MM-DD");

        this.title = "";
        this.selected_tile = "";
        this.subtitle = "";

        this.columns = [
            { field: 'MaxTime', header: 'Time' },
            { field: 'BatchCount', header: 'Batch Count' },
            { field: 'TotalSetPoint', header: 'Set Point' },
            { field: 'TotalActualQty', header: 'Actual Qty' },
            { field: 'Deviation', header: 'Deviation' },
            { field: 'AvgDuration', header: 'Duration' },
            { field: 'PercentDeviation', header: '% Deviation' }
        ];

        this.cmsReportColumns = [
            { field: 'Time', header: 'Time' },
            { field: 'CreamRatioSP', header: 'Set Cream Ratio' },
            { field: 'CreamRatioActual', header: 'Actual Cream Ratio' },
            { field: 'MaidaActual', header: 'Maida Qty' },
            { field: 'CreamActual', header: 'Cream Qty' },
            { field: 'Throughput', header: 'Throughput Rate'}
        ];

        this.wtWeightReportColumns = [
            { field: 'Time', header: 'Time'},
            { field: 'ContinuousWeight', header: 'ContinuousWeight' },
            { field: 'Totaliser', header: 'Totaliser' }
        ];

        this.wtWeightSampleReportColumns = [
            { field: 'Time', header: 'Time'},
            { field: 'SampleWeight', header: 'Sample Weight' },
            { field: 'SampleBit', header: 'Sample Bit' }
        ];

        this.packingReportColumns = [
            { field: 'Time', header: 'Time', width: '50%' },
            { field: 'PackingAverageRate', header: 'Packing Average Rate', width: '30%' },
            { field: 'TotalWeightAcceptedPacks', header: 'Total Weight Accepted Packs', width: '30%'  },
            { field: 'TotalAcceptedPacks', header: 'Total Accepted Packs', width: '30%'  },
            { field: 'TotalRejectedPacks', header: 'Total Rejected Packs', width: '30%'  },
            { field: 'TotalJointPacks', header: 'Total Joint Packs', width: '30%'  },
            { field: 'TotalLSL', header: 'Total LSL', width: '30%'  },
            { field: 'TotalUSL', header: 'Total USL', width: '30%'  },
            { field: 'NoOfStopagges', header: 'No Of Stopagges', width: '30%'  },
            { field: 'StoppageDuration', header: 'Stoppage Duration', width: '30%'  },
            { field: 'NoOfPacksInAcceptedBand', header: 'No Of Packs In Accepted Band', width: '30%'  },
            { field: 'SKU', header: 'SKU', width: '30%'  },
            { field: 'Efficiency', header: 'Efficiency', width: '30%'  }
        ];

        this.lossesReportColumns = [
            { field: 'Time', header: 'Time', width: '50%' },
            { field: 'TotalWeightAcceptedPacks', header: 'Total Weight Accepted Packs', width: '30%'  },
            { field: 'TotalSetPoint', header: 'Total Accepted Packs', width: '30%'  },
            { field: 'NoOfPacksInAcceptedBand', header: 'No Of Packs In Accepted Band', width: '30%'  },
            { field: 'SKU', header: 'SKU', width: '30%'  },
            { field: 'GiveAwayLoss', header: 'Give Away Losses', width: '30%'  }
        ];

        this.cbbReportColumns = [
            { field: 'Time', header: 'Time', width: '50%' },
            { field: 'Weight', header: 'CBB Weight', width: '30%' },
            { field: 'AverageWeight', header: 'Average Weight', width: '30%'  },
            { field: 'AcceptedPacks', header: 'Accepted Packs', width: '30%'  },
            { field: 'TotalLSL', header: 'Total LSL', width: '30%'  },
            { field: 'TotalUSL', header: 'Total USL', width: '30%'  },
            { field: 'NoOfStopagges', header: 'No Of Stopagges', width: '30%'  },
            { field: 'StoppageDuration', header: 'Stoppage Duration', width: '30%'  },
        ];

  		this.overviewClicked(this.selected_tile);

  	}

    private read_settings(): void {
        this.apiService.postapi("readsettings", {}).subscribe(d => {
            this.saveTimeout = d.Results["time"];
            // this.tileToShow = d.Results["tile"];
            let allTiles = d.Results["tile"];
            let isTitleSet = false;
            for(let i=0; i<allTiles.length; i++){
                let obj = allTiles[i];
                this.tileToShow[obj["name"]] = obj["value"];
                if(obj["value"] === true){
                    if(isTitleSet === false) {
                        if(obj["name"] === "Mixing"){
                            this.title = obj["name"] + " - Overview(Milk Bikis)";
                        }
                        else {
                            this.title = obj["name"] + " - Overview";    
                        }
                        
                        this.selected_tile = obj["name"];
                        this.subtitle = "Overview";
                        isTitleSet = true;
                        this.overviewClicked(this.selected_tile);
                    }

                    this.lastElement = obj["name"];    
                }
            }

            this.menuItems = [{
                label: 'Mixing',
                expanded : this.selected_tile === "Mixing", 
                visible: this.tileToShow["Mixing"],
                items:[{
                    label: 'Milk Bikis',
                    expanded : true, 
                    items: [{
                            label: 'Overview', 
                            icon: 'fa fa-fw fa-bar-chart',
                            command: (event) => { 
                                this.recipeKey = "1";
                                this.title = "Mixing - Overview(Milk Bikis)";
                                this.subtitle = "Overview";
                                this.selected_tile = "Mixing";
                                this.overviewClicked('Mixing'); 
                                this.summaryPanelAvailable = true;
                                this.reportPanelAvailable = false;
                                this.sideBarVisibility = false;
                            }
                        },{
                            label: 'Report', 
                            icon: 'fa fa-fw fa-book',
                            command: (event) => { 
                                this.recipeKey = "1";
                                this.title = "Mixing - Report(Milk Bikis)"
                                this.subtitle = "Report";
                                this.selected_tile = "Mixing";
                                this.reportClicked('Mixing');
                                this.reportPanelAvailable = true;
                                this.summaryPanelAvailable = false;
                                this.sideBarVisibility = false;
                            }
                        }
                    ]
                },{
                    label: 'Nutri Choice',
                    expanded : false, 
                    items: [{
                            label: 'Overview', 
                            icon: 'fa fa-fw fa-bar-chart',
                            command: (event) => { 
                                this.recipeKey = "2";
                                this.title = "Mixing - Overview(Nutri Choice)";
                                this.subtitle = "Overview";
                                this.selected_tile = "Mixing";
                                this.overviewClicked('Mixing'); 
                                this.summaryPanelAvailable = true;
                                this.reportPanelAvailable = false;
                                this.sideBarVisibility = false;
                            }
                        },{
                            label: 'Report', 
                            icon: 'fa fa-fw fa-book',
                            command: (event) => { 
                                this.recipeKey = "2";
                                this.title = "Mixing - Report(Nutri Choice)"
                                this.subtitle = "Report";
                                this.selected_tile = "Mixing";
                                this.reportClicked('Mixing');
                                this.reportPanelAvailable = true;
                                this.summaryPanelAvailable = false;
                                this.sideBarVisibility = false;
                            }
                        }
                    ]
                },{
                    label : 'Nice',
                    expanded : false, 
                    items: [{
                            label: 'Overview', 
                            icon: 'fa fa-fw fa-bar-chart',
                            command: (event) => { 
                                this.recipeKey = "3";
                                this.title = "Mixing - Overview(Nice)";
                                this.subtitle = "Overview";
                                this.selected_tile = "Mixing";
                                this.overviewClicked('Mixing'); 
                                this.summaryPanelAvailable = true;
                                this.reportPanelAvailable = false;
                                this.sideBarVisibility = false;
                            }
                        },{
                            label: 'Report', 
                            icon: 'fa fa-fw fa-book',
                            command: (event) => { 
                                this.recipeKey = "3";
                                this.title = "Mixing - Report(Nice)"
                                this.subtitle = "Report";
                                this.selected_tile = "Mixing";
                                this.reportClicked('Mixing');
                                this.reportPanelAvailable = true;
                                this.summaryPanelAvailable = false;
                                this.sideBarVisibility = false;
                            }
                        }
                    ]
                }]
                // items: [{
                //             label: 'Overview', 
                //             icon: 'fa fa-fw fa-bar-chart',
                //             command: (event) => { 
                //                 this.title = "Mixing - Overview";
                //                 this.subtitle = "Overview";
                //                 this.selected_tile = "Mixing";
                //                 this.overviewClicked('Mixing'); 
                //                 this.summaryPanelAvailable = true;
                //                 this.reportPanelAvailable = false;
                //                 this.sideBarVisibility = false;
                //             }
                //         },{
                //             label: 'Report', 
                //             icon: 'fa fa-fw fa-book',
                //             command: (event) => { 
                //                 this.title = "Mixing - Report"
                //                 this.subtitle = "Report";
                //                 this.selected_tile = "Mixing";
                //                 this.reportClicked('Mixing');
                //                 this.reportPanelAvailable = true;
                //                 this.summaryPanelAvailable = false;
                //                 this.sideBarVisibility = false;
                //             }
                //         }
                //     ]
            },{
                label: 'Moulder', 
                expanded: this.selected_tile === "Moulder",
                visible: this.tileToShow["Moulder"],
                items: [{
                        label: 'Overview', 
                        icon: 'fa fa-fw fa-bar-chart',
                        command: (event) => { 
                            this.title = "Moulder - Overview";
                            this.selected_tile = "Moulder";
                            this.subtitle = "Overview";
                            this.overviewClicked('Moulder');
                            this.summaryPanelAvailable = true;
                            this.reportPanelAvailable = false;
                            this.sideBarVisibility = false;
                        }
                    },{
                        label: 'Report', 
                        icon: 'fa fa-fw fa-book',
                        command: (event) => { 
                            this.title = "Moulder - Report";
                            this.selected_tile = "Moulder";
                            this.subtitle = "Report";
                            this.reportClicked('Moulder'); 
                            this.summaryPanelAvailable = true;
                            this.reportPanelAvailable = false;
                            this.sideBarVisibility = false;
                        }
                    },{
                        label: 'DownTime Report', 
                        icon: 'fa fa-fw fa-support',
                        command: (event) => { 
                            this.title = "Moulder - DownTime Report";
                            this.selected_tile = "Moulder";
                            this.subtitle = "Downtime";
                            this.reportClicked('Moulder');
                            this.summaryPanelAvailable = true;
                            this.reportPanelAvailable = false;
                            this.sideBarVisibility = false; 
                        }
                    }
                ]
            },{
                label: 'Oven', 
                expanded:this.selected_tile === "Oven",
                visible: this.tileToShow["Oven"],
                items: [{
                        label: 'Overview', 
                        icon: 'fa fa-fw fa-bar-chart',
                        command: (event) => { 
                            this.title = "Oven - Overview";
                            this.selected_tile = "Oven";
                            this.subtitle = "Overview";
                            this.overviewClicked('Oven');
                            this.summaryPanelAvailable = true;
                            this.reportPanelAvailable = false;
                            this.sideBarVisibility = false;
                        }
                    },{
                        label: 'Report', 
                        icon: 'fa fa-fw fa-book',
                        command: (event) => { 
                            this.title = "Oven - Report";
                            this.selected_tile = "Oven";
                            this.subtitle = "Report";
                            this.reportClicked('Oven'); 
                            this.summaryPanelAvailable = true;
                            this.reportPanelAvailable = false;
                            this.sideBarVisibility = false;
                        }
                    }
                ]
            },{
                label: 'Bori', 
                expanded:this.selected_tile === "Bori",
                visible: this.tileToShow["Bori"],
                items: [{
                        label: 'Report', 
                        icon: 'fa fa-fw fa-book',
                        command: (event) => { 
                            this.title = "Bori - Report";
                            this.selected_tile = "Bori";
                            this.subtitle = "Report";
                            this.reportClicked('Bori'); 
                            this.summaryPanelAvailable = true;
                            this.reportPanelAvailable = false;
                            this.sideBarVisibility = false;
                        }
                    }
                ]
            },{
                label: 'CMS', 
                expanded: this.selected_tile === "CMS",
                visible: this.tileToShow["CMS"],
                items: [{
                        label: 'Overview', 
                        icon: 'fa fa-fw fa-bar-chart',
                        command: (event) => { 
                            this.title = "CMS - Overview";
                            this.selected_tile = "CMS";
                            this.overviewClicked('CMS');
                            this.subtitle = "Overview";
                            this.summaryPanelAvailable = true;
                            this.reportPanelAvailable = false;
                            this.sideBarVisibility = false; 
                        }
                    },{
                        label: 'Report', 
                        icon: 'fa fa-fw fa-book',
                        command: (event) => { 
                            this.title = "CMS - Report";
                            this.selected_tile = "CMS";
                            this.subtitle = "Report";
                            this.reportClicked('CMS');
                            this.summaryPanelAvailable = true;
                            this.reportPanelAvailable = false;
                            this.sideBarVisibility = false; 
                        }
                    }
                ]
            },{
                label: 'Wet Weight', 
                expanded: this.selected_tile === "Wet Weight",
                visible: this.tileToShow["Wet Weight"],
                items: [{
                        label: 'Overview', 
                        icon: 'fa fa-fw fa-bar-chart',
                        command: (event) => { 
                            this.title = "Wet Weight - Overview";
                            this.subtitle = "Overview";
                            this.selected_tile = "Wet Weight";
                            this.overviewClicked('Wet Weight');
                            this.summaryPanelAvailable = true;
                            this.reportPanelAvailable = false;
                            this.sideBarVisibility = false; 
                        }
                    },{
                        label: 'Report', 
                        icon: 'fa fa-fw fa-book',
                        command: (event) => { 
                            this.title = "Wet Weight - Report";
                            this.selected_tile = "Wet Weight";
                            this.subtitle = "Report";
                            this.reportClicked('Wet Weight');
                            this.summaryPanelAvailable = true;
                            this.reportPanelAvailable = false;
                            this.sideBarVisibility = false; 
                        }
                    }
                ]
            },{
                label: 'Packing', 
                expanded: this.selected_tile === "Packing",
                visible: this.tileToShow["Packing"],
                items: [{
                        label: 'Overview', 
                        icon: 'fa fa-fw fa-bar-chart',
                        command: (event) => { 
                            this.title = "Packing - Overview";
                            this.subtitle = "Overview";
                            this.selected_tile = "Packing";
                            this.overviewClicked('Packing');
                            this.summaryPanelAvailable = true;
                            this.reportPanelAvailable = false;
                            this.sideBarVisibility = false; 
                        }
                    },{
                        label: 'Report', 
                        icon: 'fa fa-fw fa-book',
                        command: (event) => { 
                            this.title = "Packing - Report";
                            this.selected_tile = "Packing";
                            this.subtitle = "Report";
                            this.reportClicked('Packing');
                            this.summaryPanelAvailable = true;
                            this.reportPanelAvailable = false;
                            this.sideBarVisibility = false; 
                        }
                    }
                ]
            },{
                label: 'Losses', 
                expanded: this.selected_tile === "Losses",
                visible: this.tileToShow["Losses"],
                items: [{
                        label: 'Overview', 
                        icon: 'fa fa-fw fa-bar-chart',
                        command: (event) => { 
                            this.title = "Losses - Overview";
                            this.subtitle = "Overview";
                            this.selected_tile = "Losses";
                            this.overviewClicked('Losses');
                            this.summaryPanelAvailable = true;
                            this.reportPanelAvailable = false;
                            this.sideBarVisibility = false; 
                        }
                    },{
                        label: 'Report', 
                        icon: 'fa fa-fw fa-book',
                        command: (event) => { 
                            this.title = "Losses - Report";
                            this.selected_tile = "Losses";
                            this.subtitle = "Report";
                            this.reportClicked('Losses');
                            this.summaryPanelAvailable = true;
                            this.reportPanelAvailable = false;
                            this.sideBarVisibility = false; 
                        }
                    }
                ]
            }];

        });
    }

    private getLossesHome(): void {
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString
        };
        this.mask = true;
        this.apiService.postapi("getlosseshome", params).subscribe(d => {
            this.summaryKeys = [];
            this.lossesSummaryPanel = d.Results;
            
            if(this.lossesSummaryPanel.length ===  0){
                this.summaryPanelAvailable = false;
                this.disableDownload = true;
            }
            else{
                this.disableDownload = false;
            }
            for(let i=0; i<this.lossesSummaryPanel.length; i++){
                let obj = this.lossesSummaryPanel[i];
                this.summaryKeys.push(obj["prop"]);
                setTimeout (() => {
                    this.chartService.draw_pie_with_title(obj["data"]["pie_chart"]);
                }, 300);
            }
            this.mask = false;
        });
    }

    private getPackingHome(): void {
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString
        };
        this.mask = true;
        this.apiService.postapi("getpackinghome", params).subscribe(d => {
            this.summaryKeys = [];
            this.packingSummaryPanel = d.Results;
            
            if(this.packingSummaryPanel.length ===  0){
                this.summaryPanelAvailable = false;
                this.disableDownload = true;
            }
            else{
                this.disableDownload = false;
            }
            for(let i=0; i<this.packingSummaryPanel.length; i++){
                let obj = this.packingSummaryPanel[i];
                this.summaryKeys.push(obj["prop"]);
                setTimeout (() => {
                    this.chartService.draw_line_chart_2(obj["production"]["line_column_chart"]);
                    this.chartService.draw_line_chart_2(obj["packets"]["line_column_chart"]);
                    this.chartService.draw_line_chart_2(obj["efficiency"]["line_column_chart"]);
                    this.chartService.draw_pie_with_title(obj["efficiency"]["pie_chart"]);
                    this.chartService.draw_line_chart_2(obj["packing_rate"]["line_column_chart"]);
                }, 300);
            }
            this.mask = false;
        });
    }

    private getWetWeightHome(): void {
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString
        };
        this.mask = true;
        this.apiService.postapi("getwwhome", params).subscribe(d => {
            this.summaryKeys = [];
            this.wtWeightSummaryPanel = d.Results;
            if(this.wtWeightSummaryPanel.length ===  0){
                this.summaryPanelAvailable = false;
                this.disableDownload = true;
            }
            else{
                this.disableDownload = false;
            }
            this.summaryKeys.push("wet_weight");
            this.summaryKeys.push("sample_weight");
            for(let i=0; i<this.wtWeightSummaryPanel.length; i++){

                let obj = this.wtWeightSummaryPanel[i];
                setTimeout (() => {
                    this.chartService.draw_line_chart_2(obj["data"]["line_chart_wt_weight"]);
                    this.chartService.draw_column_chart(obj["data"]["line_chart_sample_weight"]);
                }, 300);
            }
            this.mask = false;
        });
    }

    private getCMSHome(): void {
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString
        };
        this.mask = true;
        this.apiService.postapi("getcmshome", params).subscribe(d => {
            this.summaryKeys = [];
            this.cmsSummaryPanel = d.Results;
            if(this.cmsSummaryPanel.length ===  0){
                this.summaryPanelAvailable = false;
                this.disableDownload = true;
            }
            else{
                this.disableDownload = false;
            }
            for(let i=0; i<this.cmsSummaryPanel.length; i++){
                let obj = this.cmsSummaryPanel[i];
                this.summaryKeys.push(obj["prop"]);
                setTimeout (() => {
                    this.chartService.draw_line_chart_2(obj["data"]["line_chart_qty"]);
                    this.chartService.draw_line_chart_2(obj["data"]["line_chart_ratio"]);
                }, 300);
            }
            this.mask = false;
        });
    }

    private getOvenHome(): void {
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString
        };
        this.mask = true;
        this.apiService.postapi("getovenhome", params).subscribe(d => {
            this.summaryKeys = [];
            this.ovenAvergaePanel = d.Results.average;
            this.ovenSummaryPanel = d.Results.overview;
            if(this.ovenSummaryPanel.length ===  0){
                this.summaryPanelAvailable = false;
                this.disableDownload = true;
            }
            else{
                this.disableDownload = false;
            }
            for(let i=0; i<this.ovenSummaryPanel.length; i++){
                let obj = this.ovenSummaryPanel[i];
                setTimeout (() => {
                    this.chartService.draw_line_chart_2(obj["data"]["line_chart"]);
                }, 300);
            }
            for(let i=0; i<this.ovenAvergaePanel.length; i++){
                let obj = this.ovenAvergaePanel[i];
                setTimeout (() => {
                    this.chartService.draw_line_chart_2(obj["chart"]);
                }, 300);
            }
            this.mask = false;
        });
    }

    private getMoulderHome(): void{
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString
        };
        this.mask = true;
        this.apiService.postapi("getmoulderhome", params).subscribe(d => {
            this.summaryKeys = [];
            this.moulderSummaryPanel = d.Results;
            if(this.moulderSummaryPanel.length ===  0){
                this.summaryPanelAvailable = false;
                this.disableDownload = true;
            }
            else{
                this.disableDownload = false;
            }
            for(let i=0; i<this.moulderSummaryPanel.length; i++){
                let obj = this.moulderSummaryPanel[i];
                this.summaryKeys.push(obj["prop"]);
                setTimeout (() => {
                    this.chartService.draw_line_chart_2(obj["data"]["line_chart"]);
                }, 300);
            }
            this.mask = false;
        });
    }

    private getMixingMenu(): void {
        let params = {
            "recipeValue": this.recipeKey
        };

        this.apiService.postapi("getmixingmenu", params).subscribe(d => {
            this.mixings = d.Results.items;
            this.all_mixings = d.Results.items;
            this.selectedMixing = this.utilService.notNullOrEmpty(this.selectedMixing) ? this.selectedMixing : d.Results.selected;
            this.getHome();
        });
    }

  	private getHome():void{
  		let params = {
  			"selectedDate": this.fromDate.value,
            "today": this.toDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "recipeValue": this.recipeKey,
            "selectedItems": this.selectedMixing
  		};

        if(this.fromDate.value === this.toDate.value) {
            this.hideTrendChart = false;
        }
        else {
            this.hideTrendChart = true;
        }

        this.mask = true;
  		this.apiService.postapi("gethome", params).subscribe(d => {
            this.summaryPanel = d.Results;
            this.summaryKeys = [];
            if(this.summaryPanel.length ===  0){
                this.summaryPanelAvailable = false;
                this.disableDownload = true;
            }
            else{
                this.disableDownload = false;
            }

            for(let i=0; i<this.summaryPanel.length; i++){
                let obj = this.summaryPanel[i];
                this.summaryKeys.push(obj["prop"]);
                if(this.hideTrendChart){
                    setTimeout (() => {
                        this.chartService.draw_pie_with_title(obj["data"]["pie_chart"]);
                    }, 300);
                }
                else{
                    setTimeout (() => {
                        this.chartService.draw_pie_with_title(obj["data"]["pie_chart"]);
                        this.chartService.draw_line_chart(obj["data"]["line_chart"]);    
                    }, 300);
                }
            }
            this.mask = false;
  		});
  	}

    private getMoulderDownTimeReport(): void {
        let params = {
           "selectedDate": this.fromDate.value,
           "selectedFromDate": this.fromDate.value,
           "selectedToDate": this.toDate.value,
           "today": this.toDayString
        }; 
        this.mask = true;
        this.apiService.postapi("getmoulderdowntimereport", params).subscribe(d => {

            this.moulder_downtime_reports = d.Results["all_rows"];
            this.downTimeColumns = d.Results["columns"];
            let footerData = d.Results["footer"];
            let footerDuration = d.Results["footer_duration"];
            this.downFooter = [];
            this.downFooterDuration = [];
            for(let i=0; i<this.downTimeColumns.length; i++){
                this.downFooter.push({
                  "key": this.downTimeColumns[i]["header"],
                  "value": footerData[this.downTimeColumns[i]["field"]]
                });
                this.downFooterDuration.push({
                    "key": this.downTimeColumns[i]["header"],
                    "value": footerDuration[this.downTimeColumns[i]["field"]]
                });
            }
            this.reportPanelAvailable = true;
            if(this.moulder_downtime_reports.length === 0){
                this.reportPanelAvailable = false;
                this.disableDownload = true;
            }
            else{
                this.disableDownload = false;
            }
            this.mask = false;
        });   
    }

    private getLossesReport(): void {
        let params = {
           "selectedDate": this.fromDate.value,
           "selectedFromDate": this.fromDate.value,
           "selectedToDate": this.toDate.value,
           "today": this.toDayString
        }; 
        this.mask = true;
        this.apiService.postapi("getlossesreport", params).subscribe(d => {
            this.losses_reports = d.Results;
            this.reportPanelAvailable = true;
            if(this.losses_reports.length === 0){
                this.reportPanelAvailable = false;
                this.disableDownload = true;
            }
            else{
                this.disableDownload = false;
            }
            this.mask = false;
        }); 
    }

    private getPackingReport(): void {
        let params = {
           "selectedDate": this.fromDate.value,
           "selectedFromDate": this.fromDate.value,
           "selectedToDate": this.toDate.value,
           "today": this.toDayString
        }; 
        this.mask = true;
        this.apiService.postapi("getpackingreport", params).subscribe(d => {
            console.log(d);
            this.packing_reports = d.Results;
            this.reportPanelAvailable = true;
            if(this.packing_reports.length === 0){
                this.reportPanelAvailable = false;
                this.disableDownload = true;
            }
            else{
                this.disableDownload = false;
            }
            this.mask = false;
        }); 
    }

    private getWetWeightReport(): void {
        let params = {
           "selectedDate": this.fromDate.value,
           "selectedFromDate": this.fromDate.value,
           "selectedToDate": this.toDate.value,
           "today": this.toDayString
        }; 
        this.mask = true;
        this.apiService.postapi("getwwreport", params).subscribe(d => {
            this.wt_weight_reports = d.Results["WetWeight"];
            this.wt_weight_sample_reports = d.Results["SampleWeight"];
            this.reportPanelAvailable = true;
            setTimeout(() => {
                this.iswtWeight = true;
            },300);
            setTimeout(() => {
                this.isSampleWeight = true;
            },300);
            // if(this.wt_weight_reports.length === 0){
            //     this.reportPanelAvailable = false;
            //     this.disableDownload = true;
            // }
            // else{
            //     this.disableDownload = false;
            // }
            this.mask = false;
        });  
    }

    private getCMSReport(): void {
        let params = {
           "selectedDate": this.fromDate.value,
           "selectedFromDate": this.fromDate.value,
           "selectedToDate": this.toDate.value,
           "today": this.toDayString
        }; 
        this.mask = true;
        this.apiService.postapi("getcmsreport", params).subscribe(d => {
            this.cms_reports = d.Results;
            this.reportPanelAvailable = true;
            if(this.cms_reports.length === 0){
                this.reportPanelAvailable = false;
                this.disableDownload = true;
            }
            else{
                this.disableDownload = false;
            }
            this.mask = false;
        });   
    }

    private getMoulderReport(): void {
        let params = {
           "selectedDate": this.fromDate.value,
           "selectedFromDate": this.fromDate.value,
           "selectedToDate": this.toDate.value,
           "today": this.toDayString
        }; 
        this.mask = true;
        this.apiService.postapi("getmoulderreport", params).subscribe(d => {
            this.moulder_reports = d.Results;
            // this.moulder_gridheaders = d.Results.gridHeaders;
            // this.moulder_headers = d.Results.headers;
            // this.moulder_keyheaders = d.Results.keyheaders;
            // console.log(d.Results);
            this.reportPanelAvailable = true;
            if(this.moulder_reports.length === 0){
                this.reportPanelAvailable = false;
                this.disableDownload = true;
            }
            else{
                this.disableDownload = false;
            }
            this.mask = false;
        });   
    }

    private getOvenReport(): void {
        let params = {
           "selectedDate": this.fromDate.value,
           "selectedFromDate": this.fromDate.value,
           "selectedToDate": this.toDate.value,
           "today": this.toDayString
        }; 
        this.mask = true;
        this.apiService.postapi("getovenreport", params).subscribe(d => {
            this.oven_reports = d.Results;

            this.reportPanelAvailable = true;
            if(this.oven_reports.length === 0){
                this.reportPanelAvailable = false;
                this.disableDownload = true;
            }
            else{
                this.disableDownload = false;
            }
            this.mask = false;
        });   
    }

    private getBoriReport(): void {
        let params = {
           "selectedDate": this.fromDate.value,
           "selectedFromDate": this.fromDate.value,
           "selectedToDate": this.toDate.value,
           "today": this.toDayString
        }; 
        this.mask = true;
        this.apiService.postapi("getborireport", params).subscribe(d => {
            this.bori_reports = d.Results.data;
            this.boriFooter = d.Results.footer_data;
            this.boriColumns = d.Results.columns;

            this.reportPanelAvailable = true;
            if(this.bori_reports.length === 0){
                this.reportPanelAvailable = false;
                this.disableDownload = true;
            }
            else{
                this.disableDownload = false;
            }
            this.mask = false;
        });
    }

    private getReports(): void {
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString,
            "recipeValue":this.recipeKey,
            "selectedItems": this.selectedMixing
        };
        this.mask = true;
        this.apiService.postapi("getreports", params).subscribe(d => {
            this.reports = d.Results;
            if(this.reports.length === 0){
                this.reportPanelAvailable = false;
                this.disableDownload = true;
            }
            else{
                this.disableDownload = false;
            }
            this.mask = false;
        });   
    }

    public searchTextChange() {
        this.mixings = [];
        this.all_mixings.forEach(ele => {
            if(ele['value'].toLowerCase().includes(this.searchMixing.toLowerCase())){
                this.mixings.push(ele);
            }

            this.selectedMixing.forEach(item => {
                if(ele['value'] === item) {
                    ele['display'] = true;
                    this.addToMixingStore(ele);
                }
            }); 
        });
    }

    public addToMixingStore(element){
        let isFound = false;
        for(let item of this.mixings) {
            if(element['value'] === item['value']){
                isFound = true;
                break;
            }
        }
        if(!isFound) {
            this.mixings.push(element);
        }
    }

    public toggleMixingSelection() {
        this.selectedMixing = [];

        if(this.selectAllMixing){
            this.mixings.forEach(ele => {
                ele['display'] = true;
                this.selectedMixing.push(ele['value']);
            });
        }
        else{
            this.selectedMixing = [];
            this.mixings.forEach(ele => {
                ele['display'] = false;
            });
        }
        this.mixingMenuChanged();
    }

    public clearAllSearch() {
        this.searchMixing = null;
        this.mixings.forEach(ele => {
            ele['display'] = true;
        })

    }

    public mixingMenuChanged(): void {

        if(this.subtitle === "Overview"){
            this.summaryPanelAvailable = true;
            this.reportPanelAvailable = false; 
            this.disableDownload = false;   
            this.getHome();
        }
        else {
            this.reportPanelAvailable = true;
            this.summaryPanelAvailable = false;
            this.disableDownload = false;
            this.getReports();
        }
    }

    public downloadOverview(): void {
        this.disableDownload = true;
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString,
            "title": this.title,
            "recipeValue": this.recipeKey,
            "selectedItems": this.selectedMixing
        }; 
        this.apiService.postapi("savedashboardreport", params).subscribe(d => {
            this.apiService.download(d.Results);
            // let filename = d.Results;
            // let filename = "Mixing_Dashboard_56257e5f-db57-4ae2-97fd-959f64fedc6.zip";
            // let emailParam = {
            //     "attachment": filename,
            // }
            // this.apiService.postapi("senddashboardemail", emailParam).subscribe(d => {
            //     console.log(d);
            // });

            this.mask = false;
            this.disableDownload = false;
        });
    }

    public downloadMoulderOverview(): void {
        this.disableDownload = true;
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString,
            "title": this.title
        }; 
        this.apiService.postapi("savemoulderhome", params).subscribe(d => {
            this.apiService.download(d.Results);
            this.mask = false;
            this.disableDownload = false;
        });
    }

    public downloadOvenOverview(): void {
        this.disableDownload = true;
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString,
            "title": this.title
        }; 
        this.apiService.postapi("saveovenhome", params).subscribe(d => {
            this.apiService.download(d.Results);
            this.mask = false;
            this.disableDownload = false;
        });
    }

    public downloadPackingOverview(): void{
        this.disableDownload = true;
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString,
            "title": this.title
        }; 
        this.apiService.postapi("savepackinghome", params).subscribe(d => {
            this.apiService.download(d.Results);
            this.mask = false;
            this.disableDownload = false;
        });
    }

    public downloadFile(): void {
        this.mask = true;
        console.log(this.selected_tile + " Download Started");
        if(this.subtitle === "Overview"){
            let element = "";

            if(this.selected_tile === "Mixing"){
                // element = '#nodeToRenderAsPDF';
                this.downloadOverview();
            }
            if(this.selected_tile === "Moulder"){
                this.downloadMoulderOverview();
            }
            if(this.selected_tile === "Oven"){
                this.downloadOvenOverview();
            }
            if(this.selected_tile === "CMS"){
                element = '#cmsnodeToRenderAsPDF';
            }
            if(this.selected_tile === "Wet Weight"){
                element = '#wtweightnodeToRenderAsPDF';
            }
            if(this.selected_tile === "Packing"){
                this.downloadPackingOverview();
            }
            if(this.selected_tile === "Losses"){
                element = '#lossesnodeToRenderAsPDF';
            }
            
            // this.downloadPDF(element, "");
        }
        else{
            if(this.selected_tile === "Mixing"){
                this.downloadReport();
            }
            else if(this.selected_tile === "Moulder"){
                if(this.subtitle === "Report"){
                    this.downloadMoulderReport();    
                }
                else if(this.subtitle === "Downtime"){
                    this.downloadMoulderDowntimeReport();
                }
                
            }
            else if(this.selected_tile === "Oven"){
                this.downloadOvenReport();
            }
            else if(this.selected_tile === "CMS"){
                this.downloadCMSReport();
            }
            else if(this.selected_tile === "Wet Weight"){
                this.downloadWetWeightReport();
            }
            else if(this.selected_tile === "Packing"){
                this.downloadPackingReport();
            }
            else if(this.selected_tile === "Losses"){
                this.downloadLossesReport();
            }
            else if(this.selected_tile === "Bori"){
                this.downloadBoriReport();
            }
        }
        
    }

    public downloadReport():void {
        this.disableDownload = true;
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString,
            "title": this.title,
            "recipeValue": this.recipeKey,
            "selectedItems": this.selectedMixing
        }; 
        this.apiService.postapi("savereport", params).subscribe(d => {
            this.apiService.download(d.Results);
            this.mask = false;
            this.disableDownload = false;
        });
    }

    public downloadLossesReport(): void {
        this.disableDownload = true;
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString,
            "title": this.title
        }; 
        this.apiService.postapi("savelossesreport", params).subscribe(d => {
            this.apiService.download(d.Results);
            this.mask = false;
            this.disableDownload = false;
        });
    }

    public downloadPackingReport(): void {
        this.disableDownload = true;
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString,
            "title": this.title
        }; 
        this.apiService.postapi("savepackingreport", params).subscribe(d => {
            this.apiService.download(d.Results);
            this.mask = false;
            this.disableDownload = false;
        });
    }

    public downloadWetWeightReport():void {
        this.disableDownload = true;
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString,
            "title": this.title
        }; 
        this.apiService.postapi("savewwreport", params).subscribe(d => {
            this.apiService.download(d.Results);
            this.mask = false;
            this.disableDownload = false;
        });
    }

    public downloadCMSReport():void {
        this.disableDownload = true;
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString,
            "title": this.title
        }; 
        this.apiService.postapi("savecmsreport", params).subscribe(d => {
            this.apiService.download(d.Results);
            this.mask = false;
            this.disableDownload = false;
        });
    }

    public downloadMoulderDowntimeReport(): void {
        this.disableDownload = true;
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString,
            "title": this.title
        }; 
        this.apiService.postapi("savemoulderdowntimereport", params).subscribe(d => {
            this.apiService.download(d.Results);
            this.mask = false;
            this.disableDownload = false;
        });
    }

    public downloadMoulderReport():void {
        this.disableDownload = true;
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString,
            "title": this.title
        }; 
        this.apiService.postapi("savemoulderreport", params).subscribe(d => {
            this.apiService.download(d.Results);
            this.mask = false;
            this.disableDownload = false;
        });
    }

    public downloadOvenReport():void {
        this.disableDownload = true;
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString,
            "title": this.title
        }; 
        this.apiService.postapi("saveovenreport", params).subscribe(d => {
            this.apiService.download(d.Results);
            this.mask = false;
            this.disableDownload = false;
        });
    }

    public downloadBoriReport():void {
        this.disableDownload = true;
        let params = {
            "selectedDate": this.fromDate.value,
            "selectedFromDate": this.fromDate.value,
            "selectedToDate": this.toDate.value,
            "today": this.toDayString,
            "title": this.title
        }; 
        this.apiService.postapi("saveborireport", params).subscribe(d => {
            this.apiService.download(d.Results);
            this.mask = false;
            this.disableDownload = false;
        });
    }

    /*public downloadPDF(element, mode):void { 
        let divHeight = 600;
        let divWidth = 1259;
        this.mask=true;
        let file_name = this.selected_tile.toLowerCase().replace(" ","_") + '_All_charts_' + this.yesterDayDate.value + '.pdf'
        if(this.disableDownload === false){
            divHeight = $(element).height();
            divWidth = $(element).width();
        }

        if(this.selected_tile === "Packing"){
            divHeight = divHeight * 2;
            divWidth = divWidth + 50;
        }
        
        let ratio = divHeight / divWidth;
        let doc = new jsPDF('l', 'mm', [divWidth, divHeight]);
        var width = doc.internal.pageSize.getWidth();
        var height = doc.internal.pageSize.getHeight();
        // height = ratio * width;
        let options = {
          pagesplit: true
        };

        var big_img = new Image();
        big_img.src = './assets/customer/abz2_big.png';

        doc.addImage(big_img, 'png', 295, 3, 85, 40);
        doc.setFont("Helvetica");
        doc.setFontType("bold");
        doc.setFontSize(40);
        doc.text(250, 75, this.title);
        doc.text(220, 125, 'Generation Date ('+this.yesterDayString+')');

        var small_img = new Image();
        small_img.src = './assets/customer/abz2_small.png';
        
        doc.addPage();
        doc.addImage(small_img, 'png', 15, -5, 25, 20);
        doc.setFont("Helvetica");
        doc.setFontType("normal");
        doc.setFontSize(14);
        doc.text(190, 5, this.title);
        doc.text(340, 5, 'Generation Date ('+this.yesterDayString+')');


        if(this.disableDownload === false){
            this.disableDownload = true;
            let ids = [];
            let deferreds = [];
            if(this.selected_tile === "Packing"){
                // ids.push(this.summaryKeys[this.summaryKeys.length - 1]);
                for(let i=0; i<=this.summaryKeys.length; i++){
                    ids.push(this.summaryKeys[i]);
                }
            }
            else{
                ids.push(this.summaryKeys[this.summaryKeys.length - 1]);
                for(let i=0; i<=this.summaryKeys.length; i++){
                    ids.push(this.summaryKeys[i]);
                }
            }
            
            let length = ids.length;
            for(let i=0; i<ids.length; i++){
                let panelName = ids[i] + '_prop';
                let deferred = $.Deferred();
                deferreds.push(deferred.promise());
                let new_chart = document.getElementById(panelName);
                if(this.selected_tile === "CMS"){
                    this.generateCanvas2(i, new_chart, doc, length, width, height, deferred, mode, file_name);
                }
                else if(this.selected_tile === "Packing"){
                    this.generateCanvas3(i, new_chart, doc, length, width, height, deferred, mode, file_name);    
                }
                else{
                    this.generateCanvas(i, new_chart, doc, length, width, height, deferred, mode, file_name);    
                }
            }
            $.when.apply($, deferreds).then(function () {
                this.mask = false;
                this.disableDownload = false;
            });
        }
        else{
            setTimeout(() => {
                doc.save(file_name);
                this.all_dashboards.push({
                    name: this.selected_tile,
                    file: file_name
                });
                this.mask = false;
                this.disableDownload = false;
                if(mode === "callback"){
                    setTimeout(() => {
                        this.apiService.postapi("getalldashboards", {"files": this.all_dashboards}).subscribe(d => {
                            console.log(d);
                        });
                    }, 5000);
                }
            }, 1000);  
        }
    }

    async generateCanvas(i, chart, doc, length, width, height, deferred, mode, pdffile) {
        await html2canvas(chart, { scale: 1 }).then( canvas => {
                let j = i;
                let x = 10;
                let y = 15;
                if(i % 2 === 0){
                    y = y * 10;
                }

                var small_img = new Image();
                small_img.src = './assets/customer/abz2_small.png';

                doc.addImage(canvas.toDataURL('image/png'), 'PNG', x, y, width-20, height-215); //height-170
                
                if(i % 2 === 0 && i < length && i != 0){
                    doc.addPage();
                    doc.addImage(small_img, 'png', 15, -5, 25, 20);
                    doc.setFont("Helvetica");
                    doc.setFontType("normal");
                    doc.setFontSize(14);
                    doc.text(190, 5, this.title);
                    doc.text(340, 5, 'Generation Date ('+this.yesterDayString+')');
                }
                if(i == 0){
                    setTimeout(() => {
                        doc.save(pdffile);
                        this.all_dashboards.push({
                            name: this.selected_tile,
                            file: pdffile
                        });
                        this.mask = false;
                        this.disableDownload = false;
                        if(mode === "callback"){
                            setTimeout(() => {
                                this.apiService.postapi("getalldashboards", {"files": this.all_dashboards}).subscribe(d => {
                                    console.log(d);
                                });
                            }, 5000);
                        }
                    }, 1000);    
                }
            });
    }

    async generateCanvas3(i, chart, doc, length, width, height, deferred, mode, pdffile) {
        await html2canvas(chart, { scale: 1 }).then( canvas => {
                let j = i;
                let x = 10;
                let y = 12;
                
                var small_img = new Image();
                small_img.src = './assets/customer/abz2_small.png';

                doc.addImage(canvas.toDataURL('image/png'), 'PNG', x, y, width-20, height-35); //height-170
                
                if(i < length){
                    doc.addPage();
                    doc.addImage(small_img, 'png', 15, -5, 25, 18);
                    doc.setFont("Helvetica");
                    doc.setFontType("normal");
                    doc.setFontSize(14);
                    doc.text(190, 5, this.title);
                    doc.text(340, 5, 'Generation Date ('+this.yesterDayString+')');
                }
                if(i == 0){
                    setTimeout(() => {
                        doc.save(pdffile);
                        this.all_dashboards.push({
                            name: this.selected_tile,
                            file: pdffile
                        });
                        this.mask = false;
                        this.disableDownload = false;
                        if(mode === "callback"){
                            setTimeout(() => {
                                this.apiService.postapi("getalldashboards", {"files": this.all_dashboards}).subscribe(d => {
                                    console.log(d);
                                });
                            }, 5000);
                        }
                    }, 1000);    
                }
            });
    }

    async generateCanvas2(i, chart, doc, length, width, height, deferred, mode, pdffile) {
        await html2canvas(chart, { scale: 1 }).then( canvas => {
                let j = i;
                let x = 10;
                let y = 5;
                if(i % 2 === 0){
                    y = y * 8;
                }
                
                var small_img = new Image();
                small_img.src = './assets/customer/abz2_small.png';

                doc.addImage(canvas.toDataURL('image/png'), 'PNG', x, y, width-20, height-60); //height-170
                
                if(i % 2 === 0 && i < length && i != 0){
                    doc.addPage();
                    doc.addImage(small_img, 'png', 15, -5, 25, 18);
                    doc.setFont("Helvetica");
                    doc.setFontType("normal");
                    doc.setFontSize(14);
                    doc.text(190, 5, this.title);
                    doc.text(340, 5, 'Generation Date ('+this.yesterDayString+')');
                }
                if(i == 0){
                    setTimeout(() => {
                        doc.save(pdffile);
                        this.all_dashboards.push({
                            name: this.selected_tile,
                            file: pdffile
                        });
                        if(mode === "callback"){
                            this.apiService.postapi("getalldashboards", {"files": this.all_dashboards}).subscribe(d => {
                                window.open("about:blank", "_self");
                                setTimeout (window.close, 5000);
                            });
                        }
                        this.mask = false;
                        this.disableDownload = false;
                    }, 1000);    
                }
            });
    }*/

    public onFromDateChange(event:any): void {
        let dateValue = event.value;
        let nw = moment(dateValue.toString()).format("YYYY-MM-DD");
        this.fromDate.setValue(nw);
        this.yesterDayString = nw;
        if(this.subtitle === "Overview"){
            this.summaryPanelAvailable = true;
            this.reportPanelAvailable = false; 
            this.disableDownload = false;   
            this.overviewClicked(this.selected_tile);
        }
        else {
            this.reportPanelAvailable = true;
            this.summaryPanelAvailable = false;
            this.disableDownload = false;
            this.reportClicked(this.selected_tile);   
        }
    }

    public onToDateChange(event:any): void {
        let dateValue = event.value;
        let nw = moment(dateValue.toString()).format("YYYY-MM-DD");
        this.toDate.setValue(nw);
        this.yesterDayString = nw;
        if(this.subtitle === "Overview"){
            this.summaryPanelAvailable = true;
            this.reportPanelAvailable = false; 
            this.disableDownload = false;   
            this.overviewClicked(this.selected_tile);
        }
        else {
            this.reportPanelAvailable = true;
            this.summaryPanelAvailable = false;
            this.disableDownload = false;
            this.reportClicked(this.selected_tile);   
        }
    }

    public openSideBar():void{
    	let visible = this.sideBarVisibility;
    	this.sideBarVisibility = !visible;
    };

    public overviewClicked(menu:String):void {
        this.overviewVisible = true;
        this.reportVisible = false;
        if(menu === 'Mixing'){
            this.getMixingMenu();
        }
        if(menu === "Moulder"){
            this.getMoulderHome();
        }
        if(menu === "CMS"){
            this.getCMSHome();
        }
        if(menu === "Wet Weight"){
            this.getWetWeightHome();
        }
        if(menu === "Packing") {
            this.getPackingHome();
        }
        if(menu === "Losses") {
            this.getLossesHome();
        }
        if(menu === "Oven") {
            this.getOvenHome();
        }
    }

    public reportClicked(menu: String): void {
        if(menu === 'Mixing'){
            this.overviewVisible = false;
            this.reportVisible = true;
            this.getReports();
        }
        if(menu === "Moulder"){
            this.overviewVisible = false;
            this.reportVisible = true;
            if(this.subtitle === "Report"){
                this.getMoulderReport();
            }
            else if(this.subtitle === "Downtime"){
                this.getMoulderDownTimeReport();
            }
        }
        if(menu === "CMS"){
            this.overviewVisible = false;
            this.reportVisible = true;
            this.getCMSReport();
        }
        if(menu === "Wet Weight"){
            this.overviewVisible = false;
            this.reportVisible = true;
            this.getWetWeightReport();
        }
        if(menu === "Packing"){
            this.overviewVisible = false;
            this.reportVisible = true;
            this.getPackingReport();
        }
        if(menu === "Losses"){
            this.overviewVisible = false;
            this.reportVisible = true;
            this.getLossesReport();
        }
        if(menu === "Oven"){
            this.overviewVisible = false;
            this.reportVisible = true;
            this.getOvenReport();
        }
        if(menu === "Bori"){
            this.overviewVisible = false;
            this.reportVisible = true;
            this.getBoriReport();
        }
    }
}
