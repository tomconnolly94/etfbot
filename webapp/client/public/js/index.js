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

// translate this function to be vue compatible
function buildChart(){

	const ctx = document.getElementById('performanceChart');
	const labels = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
	const data = {
		labels: labels,
		datasets: [{
			label: 'My Stock Portfolio',
			data: [65, 59, 80, 81, 56, 55, 40],
			fill: false,
			borderColor: 'rgb(0, 255, 0)',
			tension: 0.1
		},
		{
			label: 'SPY 500 performance',
			data: [5, 17, 26, 21, 60, 85, 80],
			fill: false,
			borderColor: 'rgb(255, 0, 0)',
			tension: 0.1
		}]
	};

	const config = {
		type: 'line',
		data: data,
	};

	new Chart(ctx, config);
}

buildChart();