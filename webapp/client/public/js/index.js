//////////////////////////////////////////////////////////////////////
//
// filename: index.js
// author: Tom Connolly
// description: Contains controller functionality for the index.html
//
//////////////////////////////////////////////////////////////////////

// create bus for communication between vue instances
Vue.prototype.$bus = new Vue();


// const vars
var charts = [];

new Vue({
	el: '#triggerPanel',
	data() {
		return {
			responseMessage: "",
			outputLogs: [],
			running: false,
			startTime: null,
			originalSpinnerParentClass: "col-sm-6 col-xl-4",
			spinnerParentClass: this.originalSpinnerParentClass
		}
	},
	methods: {
		runInvestmentBalancer: function (){
			console.log("runInvestmentBalancer called.")

			if (this.running){
				return;
			}

			this.running = true;
			this.startTime = new Date().toLocaleString();
			this.spinnerParentClass = "col-sm-8"
			this.responseMessage = "";
			this.outputLogs = [];
			vueComponent = this;

			axios.get(`/runInvestmentBalancer`).then((response) => {
				vueComponent.cleanUpInvestmentAppRun(true, response);
			}).catch(function(error){
				vueComponent.cleanUpInvestmentAppRun(false, error);
			});
		},
		cleanUpInvestmentAppRun: function(success, response){
			var successStr = success ? "successfully" : "unsuccessfully";
			console.log(`runInvestmentApp finished ${successStr}.`);
			this.responseMessage = `InvestmentApp run ${successStr} at ${vueComponent.startTime}`
			this.running = false;
			this.spinnerParentClass = this.originalSpinnerParentClass;
			if(response.data && response.data.logs)
				this.outputLogs = response.data.logs;
			Vue.prototype.$bus.$emit('reloadLogFileNameList', {});
		}
	}
});


new Vue({
	el: '#excludeListPanel',
	data() {
		return {
			stocks: [],
			newExcludeListStockSymbol: "",
			excludeReason: "immoral"
		}
	},
	beforeMount() {
		this.reloadExcludeList();
	},
	methods: {
		reloadExcludeList(){
			this.stocks = [];
			axios.get(`/excludeList`).then((response) => {
				for(const stockRecord of response.data)
				{
					this.stocks.push({
						symbol: stockRecord["symbol"],
						companyName: stockRecord["companyName"],
						reason: stockRecord["reason"]
					})
				}
			}).catch(function(error){
				console.log(`Failed to retrieve excludeList error: ${error}`);
			});
		},
		removeExcludeListItem(stockForRemoval) {
			const stockSymbolForRemoval = stockForRemoval.stock["symbol"]
			for(let index = 0; index < this.stocks.length; index++)
			{
				const stockSymbol = this.stocks[index]["symbol"];
				if(stockSymbol == stockSymbolForRemoval)
				{
					axios.delete(`/excludeList/${stockSymbolForRemoval}`).then((response) => {
						this.stocks.splice(index, 1);
					}).catch(function(error){
						console.log(`Failed to remove item from excludeList error: ${error}`);
					});
				}
			}
		},
		addExcludeListItem(){
			
			if(!this.excludeReason)
			{
				console.log(`Please select an "excludeReason"`);
				return;
			}

			let vueComponent = this;
			// add symbol
			axios.post(`excludeList/${this.newExcludeListStockSymbol}`, null, { params: {
				reason: this.excludeReason
			}}).then((response) => {
				vueComponent.reloadExcludeList();
				console.log(`Successfully added ${vueComponent} to excludeList, and reloaded the list to the UI`);
			}).catch(function(error){
				console.log(`Failed to add to excludeList, error: ${error}`);
			});
		}
	}
});


new Vue({
	el: '#logListPanel',
	data() {
		return {
			logFileNameList: []
		}
	},
	mounted() {
		Vue.prototype.$bus.$on('reloadLogFileNameList', (payload) => {
			this.reloadLogFileNameList();
		});
	},
	beforeMount() {
		this.reloadLogFileNameList();
	},
	methods: {
		reloadLogFileNameList(){
			console.log("reloading... logFileNameList");
			this.logFileNameList = [];
			axios.get(`/logFileNames`).then((response) => {
				for(const logFileName of response.data)
				{
					this.logFileNameList.push(logFileName);
				}
				console.log("successfully reloaded logFileNameList");
			}).catch(function(error){
				console.log(`Failed to retrieve excludeList error: ${error}`);
			});
		}
	}
});


new Vue({
	el: '#displayPanel',
	data() {
		return {
			monthPerformanceChartDataPanelMessages: [],
			yearPerformanceChartDataPanelMessages: []
		}
	},
	methods: {
		dataIsMalformed: function(data) // perform very basic data validation
		{
			let dataKeys = Object.keys(data);
			if(dataKeys.length == 0)
			{
				console.log(`Data is malformed, no object keys found in ${JSON.stringify(data)}.`)
				return true;
			}
			let dataSetsLengths = [];
		
			//assert all the lists in the data dict are the same length
			for(let i = 0; i < dataKeys.length; i++)
			{
				let dataPack = data[dataKeys[i]];
		
				if(typeof dataPack != 'object')
				{
					console.log(`${dataPack} is not an object`)
					return true;
				}
		
				let dataPackValues = data[dataKeys[i]]["values"];
		
				if(typeof dataPackValues != 'object' )
				{
					console.log(`${dataPackValues} is not an object`)
					return true;
				}
		
				if(dataPackValues != null)
					dataSetsLengths.push(dataPackValues.length);
			}
		
			let prevDataSetLength = dataSetsLengths[0];
			for(let i = 0; i < dataSetsLengths.length; i++)
			{
				if(prevDataSetLength != dataSetsLengths[i])
				{
					console.log(`Data is not uniform, some datasets in ${JSON.stringify(data)} were not the same length.`)
					return true;
				}
			}
		
			return false;
		},
		buildChart: function(data) // translate this function to be vue compatible
		{
			vueComponent = this;
			const yearPerformanceChartContainer = document.getElementById('yearPerformanceChart');
			const monthPerformanceChartContainer = document.getElementById('monthPerformanceChart');
			const labels = [];
			const dataKeys = Object.keys(data["SPY500"]["values"]); // SPY500 is the most consistently available data

			for(let i = 0; i < dataKeys.length; i++)
			{
				let dateParts = new Date(dataKeys[i]*1000).toUTCString().split(" ");
				let date = `${dateParts[1]} ${dateParts[2]} ${dateParts[3]}`
				labels.push(date);
			}
			const yearGraphData = {
				labels: labels,
				datasets: [
					data["CurrentHoldings"] ? vueComponent.formatGraphData('Current holdings', Object.values(data["CurrentHoldings"]["values"]), null, false, 'rgb(0, 255, 0)', 0.1) : {},
					data["SPY500"] ? vueComponent.formatGraphData('SPY 500', Object.values(data["SPY500"]["values"]), null, false, 'rgb(255, 0, 0)', 0.1) : {},
					data["PortfolioPerformance"] ? vueComponent.formatGraphData('Portfolio', Object.values(data["PortfolioPerformance"]["values"]), null, false, 'rgb(0, 0, 255)', 0.1) : {}
				]
			};

			const monthGraphData = {
				labels: vueComponent.getFinalThirtyEntries(labels),
				datasets: [
					data["CurrentHoldings"] ? vueComponent.formatGraphData('Current holdings', Object.values(data["CurrentHoldings"]["values"]), vueComponent.getFinalThirtyEntries, false, 'rgb(0, 255, 0)', 0.1) : {},
					data["SPY500"] ? vueComponent.formatGraphData('SPY 500', Object.values(data["SPY500"]["values"]), vueComponent.getFinalThirtyEntries, false, 'rgb(255, 0, 0)', 0.1) : {},
					data["PortfolioPerformance"] ? vueComponent.formatGraphData('Portfolio', Object.values(data["PortfolioPerformance"]["values"]), vueComponent.getFinalThirtyEntries, false, 'rgb(0, 0, 255)', 0.1) : {}
				]
			};

			const yearConfig = {
				type: 'line',
				data: yearGraphData,
			};
			const monthConfig = {
				type: 'line',
				data: monthGraphData,
			};


			charts.forEach(function(chart){
				chart.destroy();
			});    

			charts.push(new Chart(yearPerformanceChartContainer, yearConfig));
			charts.push(new Chart(monthPerformanceChartContainer, monthConfig));
		},
		getFinalThirtyEntries: function(list){
			return list.slice(list.length-30, list.length);
		},		
		formatGraphData: function(label, data, dataFunction, fill, borderColor, tension)
		{
			return {
				label: label,
				data: dataFunction ? dataFunction(data) : data,
				fill: fill,
				borderColor:borderColor,
				tension: tension
			};
		},
		formatDataPanelString: function(label, prevValue, currentValue)
		{
			let change = ((currentValue/prevValue * 100) - 100).toFixed(1);
			if(change >= 0)
				change = `+${change}%`;
			else if(change < 0)
				change = `-${change}%`;
			else
				change = "N/A";

			return `${label} - Start: ${prevValue}, End: ${currentValue}, Change: ${change}.`
		}
	},
	beforeMount() {
		vueComponent = this;
		axios.get(`/getInvestmentPerformanceData`).then((response) => {

			let data = response.data;

			if(vueComponent.dataIsMalformed(data))
				return;

			vueComponent.buildChart(data);


			vueComponent.monthPerformanceChartDataPanelMessages = [];

			let SPY500CurrentValue = data["SPY500"].currentValue ? (data["SPY500"].currentValue).toFixed(1) : "N/A";
			let SPY500OneMonthPrevValue = data["SPY500"].oneMonthPrevValue ? (data["SPY500"].oneMonthPrevValue).toFixed(1) : "N/A";
			vueComponent.monthPerformanceChartDataPanelMessages.push(vueComponent.formatDataPanelString("SPY500", SPY500OneMonthPrevValue, SPY500CurrentValue));

			let currentHoldingsCurrentValue = data["CurrentHoldings"].currentValue ? (data["CurrentHoldings"].currentValue).toFixed(1) : "N/A";
			let currentHoldingsOneMonthPrevValue = data["CurrentHoldings"].oneMonthPrevValue ? (data["CurrentHoldings"].oneMonthPrevValue).toFixed(1) : "N/A";
			vueComponent.monthPerformanceChartDataPanelMessages.push(vueComponent.formatDataPanelString("CurrentHoldings", currentHoldingsOneMonthPrevValue, currentHoldingsCurrentValue));

			let portfolioPerformanceCurrentValue = data["PortfolioPerformance"].currentValue ? (data["PortfolioPerformance"].currentValue).toFixed(1) : "N/A";
			let portfolioPerformanceOneMonthPrevValue = data["PortfolioPerformance"].oneMonthPrevValue ? (data["PortfolioPerformance"].oneMonthPrevValue).toFixed(1) : "N/A";
			vueComponent.monthPerformanceChartDataPanelMessages.push(vueComponent.formatDataPanelString("Portfolio", portfolioPerformanceOneMonthPrevValue, portfolioPerformanceCurrentValue));

			vueComponent.yearPerformanceChartDataPanelMessages = [];			

			let SPY500OneYearPrevValue = data["SPY500"].oneYearPrevValue ? (data["SPY500"].oneYearPrevValue).toFixed(1) : "N/A";
			vueComponent.yearPerformanceChartDataPanelMessages.push(vueComponent.formatDataPanelString("SPY500", SPY500OneYearPrevValue, SPY500CurrentValue));

			let currentHoldingsOneYearPrevValue = data["CurrentHoldings"].oneYearPrevValue ? (data["CurrentHoldings"].oneYearPrevValue).toFixed(1) : "N/A";
			vueComponent.yearPerformanceChartDataPanelMessages.push(vueComponent.formatDataPanelString("CurrentHoldings", currentHoldingsOneYearPrevValue, currentHoldingsCurrentValue));

			let portfolioPerformanceOneYearPrevValue = data["PortfolioPerformance"].oneYearPrevValue ? (data["PortfolioPerformance"].oneYearPrevValue).toFixed(1) : "N/A";
			vueComponent.yearPerformanceChartDataPanelMessages.push(vueComponent.formatDataPanelString("Portfolio", portfolioPerformanceOneYearPrevValue, portfolioPerformanceCurrentValue));
		})
	}
});
