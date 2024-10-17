//////////////////////////////////////////////////////////////////////
//
// filename: logListPanel.js
// author: Tom Connolly
// description: Contains logListPanel controller functionality for 
//                       the index.html
//
//////////////////////////////////////////////////////////////////////


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