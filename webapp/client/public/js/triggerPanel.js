//////////////////////////////////////////////////////////////////////
//
// filename: triggerPanel.js
// author: Tom Connolly
// description: Contains triggerPanel controller functionality for 
//                       the index.html
//
//////////////////////////////////////////////////////////////////////


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