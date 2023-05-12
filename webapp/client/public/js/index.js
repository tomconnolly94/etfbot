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
			running: false,
			startTime: null,
			originalSpinnerParentClass: "col-sm-6 col-xl-4",
			spinnerParentClass: this.originalSpinnerParentClass
		}
	},
	methods: {
		runInvestmentBalancer: function (){
			console.log("runInvestmentBalancer called.")
		}
	}
});

function getData(){
	axios.get(`/getInvestmentPerformanceData`).then((response) => {
		buildChart(response.data);
	})
}

// translate this function to be vue compatible
function buildChart(data){

	const ctx = document.getElementById('performanceChart');
	const labels = [];
	const dataKeys = Object.keys(data["spy500"]);
	
	for(let i = 0; i < dataKeys.length; i++)
	{
		let dateParts = new Date(dataKeys[i]*1000).toUTCString().split(" ");
		let date = `${dateParts[1]} ${dateParts[2]} ${dateParts[3]}`
		labels.push(date);
	}

	const graphData = {
		labels: labels,
		datasets: [{
			label: 'My Stock Portfolio',
			data: Object.values(data["portfolio"]),
			fill: false,
			borderColor: 'rgb(0, 255, 0)',
			tension: 0.1
		},
		{
			label: 'SPY 500 performance',
			data: Object.values(data["spy500"]),
			fill: false,
			borderColor: 'rgb(255, 0, 0)',
			tension: 0.1
		}]
	};

	const config = {
		type: 'line',
		data: graphData,
	};

	new Chart(ctx, config);
}

getData();