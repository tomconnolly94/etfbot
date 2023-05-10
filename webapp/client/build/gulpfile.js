//external dependencies
var gulp = require('gulp'),
    sass = require('gulp-sass')(require('sass'));
    concat = require('gulp-concat'),
	gutil = require('gulp-util'),
	uglify = require('gulp-terser'),
	gulpif = require('gulp-if'),
	fs = require('fs'),
	map = require('map-stream'),
	async = require('async'),
	argv = require('yargs').argv;

//internal dependencies
var production_arg = (argv.production === undefined) ? false : true;

//global variables
var is_production = production_arg || process.env.NODE_ENV == "production"
var path_to_root = "../";
var css_out_directory = path_to_root + "public/dist/css";
var compiled_webfonts_directory = path_to_root + "public/dist/fonts";
var compiled_font_directory = path_to_root + "public/dist/fonts";
var js_out_directory = path_to_root + "public/dist/js/";
var non_page_config_lists = [ "all", "unused"];
var file_string_base = `
/* Include calls to individual javascript files so they appear in the debugger 
as separate files, increasing the ease of file navigation */
jQuery.extend({
	getScript: function(url, callback) {
		var head = document.getElementsByTagName("head")[0];
		var script = document.createElement("script");
		script.src = url;
		// Handle Script loading
		{
			var done = false;
			// Attach handlers for all browsers
			script.onload = script.onreadystatechange = function(){
				if ( !done && (!this.readyState ||
					this.readyState == "loaded" || this.readyState == "compvare") ) {
				done = true;
				if (callback)
					callback();
				// Handle memory leak in IE
				script.onload = script.onreadystatechange = null;
				}
			};
		}
		head.appendChild(script);
		// We handle everything using the script element injection
		return undefined;
	},
});
//load dev scripts synchronously`;


function add_relative_root_path(item){
	if(item.indexOf("https://") >= 0){
		return `url("${item}")`;
	}
	else if(item.indexOf(".js") >= 0){
		return `${path_to_root}${item}`;
	}
	return `"${path_to_root}${item}"`;
};


gulp.task('css', function(done) {

	var client_css_page_config = JSON.parse(fs.readFileSync('client_css_page_config.json', 'utf8'));
	var page_names = Object.keys(client_css_page_config);
	var universal_css_files = client_css_page_config["all"];
	var tmp_page_scss_config_folder = `${path_to_root}public/scss/tmp/`;
	var page_promises = [];
	var delete_tmp_folder = true;
	
	//if it doesnt exist, create tmp folder to hold page scss config files
	if (!fs.existsSync(tmp_page_scss_config_folder)) { fs.mkdirSync(tmp_page_scss_config_folder); }

	for(var page_name_index = 0; page_name_index < page_names.length; page_name_index++){

		var page_name = page_names[page_name_index];
		if(non_page_config_lists.indexOf(page_name) >= 0){ //exit if page_name is a non_page config
			continue;
		}

		page_promises.push(new Promise(function(resolve, reject){
			var specific_css_scripts = client_css_page_config[page_name].map(add_relative_root_path);
			var relative_universal_css_files = universal_css_files.map(add_relative_root_path);
			var relevant_css_scripts = relative_universal_css_files.concat(specific_css_scripts);
			var tmp_scss_config_file = `${tmp_page_scss_config_folder}${page_name}.scss`;
			var tmp_scss_config_file_content = "@charset \"UTF-8\";\n";

			for(var script_index = 0; script_index < relevant_css_scripts.length; script_index++){
				tmp_scss_config_file_content += `@import ${relevant_css_scripts[script_index]};\n`;
			}

			//write an scss file with all the relevant imports for that page
			fs.writeFile(tmp_scss_config_file, tmp_scss_config_file_content, (err) => {
				if (err) throw err;

				gulp.src(tmp_scss_config_file)
					.pipe(
						gulpif(is_production, 
							sass({outputStyle: 'compressed'}).on('error', sass.logError), 
							sass({outputStyle: 'expanded'}).on('error', sass.logError)
						)
					)
					.pipe( gulp.dest(css_out_directory) )
					.on('end', function(){
						if(delete_tmp_folder){
							fs.unlink(tmp_scss_config_file, function (err) { //delete tmp file
								if (err) throw err;
								resolve();
							});
						}
						resolve();
					});
			});
		}));
	}

	Promise.all(page_promises).then(function(values){
		if(delete_tmp_folder){
			fs.rmdirSync(tmp_page_scss_config_folder); //delete the tmp scss config folder
		}
		done();
	});
});


gulp.task('css_fonts', function() {
	return gulp.src([
		'../node_modules/font-awesome/fonts/fontawesome-webfont.ttf',
		'../node_modules/font-awesome/fonts/fontawesome-webfont.woff',
		'../node_modules/font-awesome/fonts/fontawesome-webfont.woff2'
	]).pipe( gulp.dest(compiled_font_directory))
});


gulp.task('js', function(done) {

	var client_javascript_page_config = JSON.parse(fs.readFileSync('client_javascript_page_config.json', 'utf8'))
	var page_names = Object.keys(client_javascript_page_config);
	var universal_javascript_files = client_javascript_page_config["all"];
	var page_promises = [];

	for(var page_name_index = 0; page_name_index < page_names.length; page_name_index++){

		var page_entry = page_names[page_name_index];
		if(non_page_config_lists.indexOf(page_entry) >= 0){ //exit if page_name is a non_page config
			continue;
		}

		page_promises.push(new Promise(function(resolve, reject){
			var page_name = page_entry;
			var specific_js_scripts = client_javascript_page_config[page_name].map(add_relative_root_path);
			var relative_universal_javascript_files = universal_javascript_files.map(add_relative_root_path);
			var relevant_js_scripts = relative_universal_javascript_files.concat(specific_js_scripts);

			if(is_production){
				gulp.src(relevant_js_scripts)
					//.pipe(minifyJS())
					.pipe(concat(page_name + ".js"))
					.pipe(uglify())
					.on('error', function (err) { gutil.log(gutil.colors.red('[Error]'), err.toString()); })
					.pipe(gulp.dest(js_out_directory))
					resolve();
			}
			else{
				gulp.src(relevant_js_scripts)
					//.pipe(minifyJS())
					.pipe(concat(page_name + ".js"))
					//.pipe(uglify())
					.on('error', function (err) { gutil.log(gutil.colors.red('[Error]'), err.toString()); })
					.pipe(gulp.dest(js_out_directory))
					resolve();
			}
		}));
	}

	Promise.all(page_promises).then(function (values) {
		done();
	});
});


gulp.task('default', function(done) {
	console.log("Usage:");
	console.log("	--production - production build, minify javascript and collapse each views required scripts into one master js file.")
	done();
});


// gulp.task('icons', function() {
//     return gulp.src('./node_modules/components-font-awesome/webfonts/**.*')
//         .pipe(gulp.dest(compiled_webfonts_directory));
// });


//gulp.task('build', gulp.series('css'), gulp.series('css_fonts'), gulp.series('icons'), gulp.series('js'));
gulp.task('build', gulp.series('js', 'css', 'css_fonts'));