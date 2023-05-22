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
var homeUrl = "/"

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
		}
	}
});

function getData(){
	axios.get(`/getInvestmentPerformanceData`).then((response) => {
		buildChart(response.data);
	})
}


// perform very basic data validation
function dataIsMalformed(data)
{
	let dataKeys = Object.keys(data);
	let dataLength;

	//assert all the lists in the data dict are the same length

	for(let i = 0; i < dataKeys.length; i++)
	{
		if(!dataLength)
		{
			dataLength = data[dataKeys[i]].length; // init dataLength
			continue;
		}

		currentDataItemLength = data[dataKeys[i]].length
		if(currentDataItemLength != dataLength);
		console.log(`Data is not uniform, one list has ${dataLength} elements, another has ${currentDataItemLength} elements`)
		return true;
	}
	return false;
}

function getFinalThirtyEntries(list){
	return list.slice(list.length-30, list.length);
}

// translate this function to be vue compatible
function buildChart(data){

	const yearPerformanceChartContainer = document.getElementById('yearPerformanceChart');
	const monthPerformanceChartContainer = document.getElementById('monthPerformanceChart');
	const labels = [];
	const dataKeys = Object.keys(data["SPY500"]);

	if(dataIsMalformed(data))
		return;
	
	for(let i = 0; i < dataKeys.length; i++)
	{
		let dateParts = new Date(dataKeys[i]*1000).toUTCString().split(" ");
		let date = `${dateParts[1]} ${dateParts[2]} ${dateParts[3]}`
		labels.push(date);
	}

	const yearGraphData = {
		labels: labels,
		datasets: [{
			label: 'Current holdings',
			data: Object.values(data["CurrentHoldings"]),
			fill: false,
			borderColor: 'rgb(0, 255, 0)',
			tension: 0.1
		},
		{
			label: 'SPY 500',
			data: Object.values(data["SPY500"]),
			fill: false,
			borderColor: 'rgb(255, 0, 0)',
			tension: 0.1
		},
		{
			label: 'Portfolio',
			data: Object.values(data["PortfolioPerformance"]),
			fill: false,
			borderColor: 'rgb(0, 0, 255)',
			tension: 0.1
		}]
	};

	const monthGraphData = {
		labels: getFinalThirtyEntries(labels),
		datasets: [{
			label: 'Current holdings',
			data: getFinalThirtyEntries(Object.values(data["CurrentHoldings"])),
			fill: false,
			borderColor: 'rgb(0, 255, 0)',
			tension: 0.1
		},
		{
			label: 'SPY 500',
			data: getFinalThirtyEntries(Object.values(data["SPY500"])),
			fill: false,
			borderColor: 'rgb(255, 0, 0)',
			tension: 0.1
		},
		{
			label: 'Portfolio',
			data: getFinalThirtyEntries(Object.values(data["PortfolioPerformance"])),
			fill: false,
			borderColor: 'rgb(0, 0, 255)',
			tension: 0.1
		}]
	};

	const yearConfig = {
		type: 'line',
		data: yearGraphData,
	};
	const monthConfig = {
		type: 'line',
		data: monthGraphData,
	};

	new Chart(yearPerformanceChartContainer, yearConfig);
	new Chart(monthPerformanceChartContainer, monthConfig);
}

getData();